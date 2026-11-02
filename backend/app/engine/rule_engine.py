"""
Deterministic Health Insurance Audit Rule Engine.
Performs exact, explainable, and reproducible calculations using Python Decimal.
"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.engine.categories import BillCategory, CATEGORY_METADATA
from app.engine.rules import PolicyConfig, RoomRentLimitType, quantize_inr

class BillItemInput(BaseModel):
    id: Optional[str] = None
    original_description: str
    category: BillCategory = BillCategory.AMBIGUOUS_UNCATEGORIZED
    unit_price: Decimal = Field(default=Decimal("0.00"))
    quantity: Decimal = Field(default=Decimal("1.00"))
    billed_amount: Decimal = Field(default=Decimal("0.00"))
    days_stay: Optional[int] = None
    requires_review: bool = False
    review_reason: Optional[str] = None

class ItemAuditBreakdown(BaseModel):
    id: Optional[str] = None
    description: str
    category: BillCategory
    category_label: str
    billed_amount: Decimal
    allowed_amount: Decimal
    deduction_amount: Decimal
    payable_amount: Decimal
    deduction_reason: str
    is_non_payable: bool = False
    is_proportionate_deduction: bool = False
    is_room_rent_excess: bool = False
    requires_review: bool = False
    review_reason: Optional[str] = None

class AuditSummary(BaseModel):
    total_billed: Decimal
    total_allowed_before_policy_deductions: Decimal
    item_level_deductions: Decimal
    deductible_applied: Decimal
    copay_applied: Decimal
    copay_percentage: Decimal
    sum_insured_excess_applied: Decimal
    total_estimated_payable: Decimal
    total_estimated_shortfall: Decimal
    
    # Audit verification
    reconciliation_verified: bool
    status: str  # "AUDIT_CLEAN" or "AUDIT_FLAGGED_FOR_REVIEW"
    
    # Calculation metadata
    length_of_stay_days: int
    room_rent_billed_daily_rate: Decimal
    room_rent_allowed_daily_rate: Decimal
    proportionate_ratio_applied: Decimal
    assumptions_applied: List[str]
    flags_and_warnings: List[str]
    statutory_disclaimer: str

class AuditResult(BaseModel):
    policy_name: str
    policy_summary: Dict[str, Any]
    items: List[ItemAuditBreakdown]
    summary: AuditSummary

STATUTORY_DISCLAIMER = (
    "DISCLAIMER: This report is an automated pre-claim estimation based on standard insurance rules "
    "and policy parameters provided. It is NOT an official insurer settlement guarantee, claim approval, "
    "or legal advice. Actual claim approval and deduction amounts depend on your insurance company's "
    "underwriting team, original hospital documentation, cashless desk processing, and policy terms."
)

class RuleEngine:
    """
    Independent, deterministic rule engine for hospital bill pre-claim audit.
    Zero external API dependencies. Fully testable and reproducible.
    """

    @classmethod
    def audit(cls, items: List[BillItemInput], policy: PolicyConfig) -> AuditResult:
        if not items:
            raise ValueError("Cannot perform audit on an empty bill. At least one line item is required.")

        # 1. Input validation
        for idx, item in enumerate(items):
            if item.billed_amount < 0:
                raise ValueError(f"Line item #{idx+1} ('{item.original_description}') has negative billed amount: ₹{item.billed_amount}. Negative amounts are not allowed.")
            if item.quantity < 0:
                raise ValueError(f"Line item #{idx+1} ('{item.original_description}') has negative quantity: {item.quantity}.")
            if item.unit_price < 0:
                raise ValueError(f"Line item #{idx+1} ('{item.original_description}') has negative unit price: ₹{item.unit_price}.")

        assumptions: List[str] = []
        warnings: List[str] = []

        # 2. Determine Length of Stay & Room Rent Limits
        room_items = [it for it in items if it.category == BillCategory.ROOM_RENT]
        
        # Calculate length of stay
        if room_items:
            # Check if any room item has quantity > 1 or days_stay
            room_item = room_items[0]
            if room_item.days_stay and room_item.days_stay > 0:
                stay_days = room_item.days_stay
            elif room_item.quantity and room_item.quantity > 0:
                stay_days = int(room_item.quantity)
            else:
                stay_days = policy.length_of_stay_days
                assumptions.append(f"Room stay length not explicitly specified; assumed policy default of {stay_days} days.")
        else:
            stay_days = policy.length_of_stay_days
            assumptions.append(f"No specific room rent line item found; policy default of {stay_days} days considered.")

        # Determine daily room rent cap
        if policy.room_rent_limit_type == RoomRentLimitType.NO_LIMIT:
            daily_room_cap = Decimal("9999999.00")
            assumptions.append("Policy has no daily room-rent cap; 100% room rent eligible.")
        elif policy.room_rent_limit_type == RoomRentLimitType.PERCENTAGE_OF_SI:
            daily_room_cap = quantize_inr(policy.sum_insured * (policy.room_rent_limit_percentage / Decimal("100.0")))
            assumptions.append(f"Room rent limit calculated as {policy.room_rent_limit_percentage}% of Sum Insured (₹{daily_room_cap}/day).")
        else:
            daily_room_cap = policy.room_rent_limit_amount
            assumptions.append(f"Room rent capped at policy limit of ₹{daily_room_cap}/day for {stay_days} days.")

        # Determine total room rent billed and actual daily rate
        total_room_billed = sum((it.billed_amount for it in room_items), Decimal("0.00"))
        actual_daily_room_rate = quantize_inr(total_room_billed / Decimal(stay_days)) if stay_days > 0 and total_room_billed > 0 else Decimal("0.00")

        # Determine proportionate deduction ratio
        # If room rent exceeds daily cap, associate medical charges are reduced proportionately
        proportionate_ratio = Decimal("1.0000")
        is_room_capped = False

        if policy.custom_proportionate_ratio is not None:
            proportionate_ratio = policy.custom_proportionate_ratio
            assumptions.append(f"Applied explicit policy proportionate deduction ratio override: {proportionate_ratio * Decimal('100.0'):.1f}%.")
            if proportionate_ratio < Decimal("1.0"):
                is_room_capped = True
        elif total_room_billed > 0 and actual_daily_room_rate > daily_room_cap:
            is_room_capped = True
            if policy.apply_proportionate_deduction:
                proportionate_ratio = (daily_room_cap / actual_daily_room_rate).quantize(Decimal("0.0001"))
                assumptions.append(
                    f"Room rent billed at ₹{actual_daily_room_rate}/day exceeds cap of ₹{daily_room_cap}/day. "
                    f"Proportionate deduction ratio calculated as ₹{daily_room_cap} / ₹{actual_daily_room_rate} = {proportionate_ratio * Decimal('100.0'):.1f}%."
                )
            else:
                assumptions.append("Policy room rent limit exceeded, but proportionate deduction is disabled in policy config.")
        else:
            assumptions.append("Room rent billed is within the eligible daily limit. No proportionate deduction applicable.")

        # 3. Item-level audit breakdown
        audit_items: List[ItemAuditBreakdown] = []
        total_billed = Decimal("0.00")
        item_level_deductions = Decimal("0.00")
        total_item_payable = Decimal("0.00")

        for item in items:
            billed = quantize_inr(item.billed_amount)
            total_billed += billed
            cat = item.category
            meta = CATEGORY_METADATA.get(cat, CATEGORY_METADATA[BillCategory.AMBIGUOUS_UNCATEGORIZED])
            
            allowed = billed
            deduction = Decimal("0.00")
            reason = "Fully payable as per standard policy terms."
            is_non_payable = False
            is_proportionate = False
            is_room_excess = False
            req_review = item.requires_review
            review_reason = item.review_reason

            if cat == BillCategory.ROOM_RENT:
                allowed_total_for_item = quantize_inr(min(billed, daily_room_cap * Decimal(stay_days)))
                if allowed_total_for_item < billed:
                    is_room_excess = True
                    deduction = billed - allowed_total_for_item
                    allowed = allowed_total_for_item
                    reason = (
                        f"Room-rent limit exceeded: Allowed ₹{daily_room_cap}/day × {stay_days} days = ₹{allowed_total_for_item}. "
                        f"Excess of ₹{deduction} deducted."
                    )
                else:
                    reason = f"Room rent within eligible limit of ₹{daily_room_cap}/day (₹{allowed_total_for_item} for {stay_days} days)."

            elif cat in [BillCategory.NON_PAYABLE_CONSUMABLE, BillCategory.NON_PAYABLE_ADMIN] or cat.value in policy.non_payable_categories:
                is_non_payable = True
                deduction = billed
                allowed = Decimal("0.00")
                if cat == BillCategory.NON_PAYABLE_CONSUMABLE:
                    reason = "Non-payable consumable items (gloves, masks, PPE, cotton, toiletries) as per IRDAI Non-Payable Schedule."
                else:
                    reason = "Non-payable administrative / hospital maintenance fee as per standard insurer guidelines."

            elif cat == BillCategory.ASSOCIATE_MEDICAL:
                if policy.apply_proportionate_deduction and is_room_capped and proportionate_ratio < Decimal("1.0000"):
                    is_proportionate = True
                    allowed = quantize_inr(billed * proportionate_ratio)
                    deduction = billed - allowed
                    reason = (
                        f"Proportionate deduction applied: Room rent exceeded cap; associate doctor/nursing/OT charges "
                        f"reduced to {proportionate_ratio * Decimal('100.0'):.1f}% of billed (₹{allowed})."
                    )
                else:
                    reason = "Doctor consultation, nursing, and OT charges fully payable (within policy limits)."

            elif cat in [BillCategory.PHARMACY, BillCategory.DIAGNOSTICS, BillCategory.SURGERY_IMPLANT, BillCategory.OTHER_MEDICAL]:
                allowed = billed
                deduction = Decimal("0.00")
                reason = f"Eligible medical expense ({meta['label']}) - fully payable."

            elif cat == BillCategory.AMBIGUOUS_UNCATEGORIZED:
                req_review = True
                review_reason = review_reason or "Description is ambiguous or non-standard. Manual verification recommended."
                warnings.append(f"Ambiguous item '{item.original_description}' (₹{billed}) requires user confirmation.")
                # We retain as allowed for user review, but flag it
                reason = "Pending manual categorization confirmation. Retained as candidate eligible amount."

            payable = allowed
            item_level_deductions += deduction
            total_item_payable += payable

            audit_items.append(
                ItemAuditBreakdown(
                    id=item.id,
                    description=item.original_description,
                    category=cat,
                    category_label=meta["label"],
                    billed_amount=billed,
                    allowed_amount=allowed,
                    deduction_amount=deduction,
                    payable_amount=payable,
                    deduction_reason=reason,
                    is_non_payable=is_non_payable,
                    is_proportionate_deduction=is_proportionate,
                    is_room_rent_excess=is_room_excess,
                    requires_review=req_review,
                    review_reason=review_reason,
                )
            )

        # 4. Policy-level deductions: Deductible -> Co-Payment -> Sum Insured
        current_eligible = total_item_payable

        # Deductible
        deductible_applied = Decimal("0.00")
        if policy.deductible_amount > Decimal("0.00"):
            deductible_applied = min(policy.deductible_amount, current_eligible)
            current_eligible -= deductible_applied
            assumptions.append(f"Applied mandatory policy deductible of ₹{deductible_applied}.")

        # Co-Payment
        copay_applied = Decimal("0.00")
        if policy.copay_percentage > Decimal("0.00"):
            copay_applied = quantize_inr(current_eligible * (policy.copay_percentage / Decimal("100.00")))
            current_eligible -= copay_applied
            assumptions.append(f"Applied co-payment of {policy.copay_percentage}%: ₹{copay_applied} patient share.")

        # Sum Insured Capping
        sum_insured_excess = Decimal("0.00")
        if current_eligible > policy.sum_insured:
            sum_insured_excess = current_eligible - policy.sum_insured
            current_eligible = policy.sum_insured
            warnings.append(f"Eligible bill exceeds total Sum Insured (₹{policy.sum_insured}). Capped at Sum Insured; excess ₹{sum_insured_excess} is shortfall.")

        total_estimated_payable = quantize_inr(current_eligible)
        total_estimated_shortfall = quantize_inr(total_billed - total_estimated_payable)

        # 5. Reconciliation verification
        reconciled = (total_billed == (total_estimated_payable + total_estimated_shortfall))
        if not reconciled:
            # Should never happen with Decimal math, but fail-safe guard
            warnings.append("Reconciliation discrepancy detected. Manual financial review required.")

        has_flagged_items = any(it.requires_review for it in audit_items)
        status = "AUDIT_FLAGGED_FOR_REVIEW" if (has_flagged_items or warnings) else "AUDIT_CLEAN"

        summary = AuditSummary(
            total_billed=quantize_inr(total_billed),
            total_allowed_before_policy_deductions=quantize_inr(total_item_payable),
            item_level_deductions=quantize_inr(item_level_deductions),
            deductible_applied=quantize_inr(deductible_applied),
            copay_applied=quantize_inr(copay_applied),
            copay_percentage=policy.copay_percentage,
            sum_insured_excess_applied=quantize_inr(sum_insured_excess),
            total_estimated_payable=total_estimated_payable,
            total_estimated_shortfall=total_estimated_shortfall,
            reconciliation_verified=reconciled,
            status=status,
            length_of_stay_days=stay_days,
            room_rent_billed_daily_rate=actual_daily_room_rate,
            room_rent_allowed_daily_rate=daily_room_cap,
            proportionate_ratio_applied=proportionate_ratio,
            assumptions_applied=assumptions,
            flags_and_warnings=warnings,
            statutory_disclaimer=STATUTORY_DISCLAIMER,
        )

        return AuditResult(
            policy_name=policy.name,
            policy_summary={
                "sum_insured": float(policy.sum_insured),
                "room_rent_limit_amount": float(policy.room_rent_limit_amount),
                "room_rent_limit_type": policy.room_rent_limit_type.value,
                "apply_proportionate_deduction": policy.apply_proportionate_deduction,
                "copay_percentage": float(policy.copay_percentage),
                "deductible_amount": float(policy.deductible_amount),
            },
            items=audit_items,
            summary=summary,
        )

