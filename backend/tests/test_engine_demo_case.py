"""
Test suite verifying the exact Required Demonstration Case from Section 7 of the specification.

Case details:
- Total hospital bill: ₹1,50,000
- Room rent: ₹25,000
- Doctor, nursing, and OT charges: ₹60,000
- Pharmacy: ₹30,000
- Gloves, masks, and administrative fees: ₹8,000
- Diagnostics: ₹27,000

Demonstration rules:
- Room-rent limit: ₹3,000 per day
- Length of stay: 5 days
- Room-rent payable amount: ₹15,000
- Proportionate deduction reduces doctor, nursing, OT charges to 60% of billed (₹36,000)
- Pharmacy fully payable: ₹30,000
- Diagnostics fully payable: ₹27,000
- Consumables and administrative fees: non-payable (₹0)

Expected results:
- Room rent payable: ₹15,000
- Doctor, nursing, and OT payable: ₹36,000
- Pharmacy payable: ₹30,000
- Consumables and administrative fees payable: ₹0
- Diagnostics payable: ₹27,000
- Total estimated payable amount: ₹1,08,000
- Total estimated shortfall: ₹42,000
"""
from decimal import Decimal
import pytest
from app.engine.categories import BillCategory
from app.engine.rules import PolicyConfig, RoomRentLimitType
from app.engine.rule_engine import RuleEngine, BillItemInput

def test_section_7_required_demonstration_case():
    # 1. Setup Demonstration Policy
    policy = PolicyConfig(
        name="Section 7 Demonstration Policy",
        sum_insured=Decimal("500000.00"),
        room_rent_limit_type=RoomRentLimitType.FIXED_AMOUNT,
        room_rent_limit_amount=Decimal("3000.00"),  # ₹3,000 per day
        apply_proportionate_deduction=True,
        length_of_stay_days=5,                       # 5 days
        copay_percentage=Decimal("0.00"),
        deductible_amount=Decimal("0.00"),
        non_payable_categories=["NON_PAYABLE_CONSUMABLE", "NON_PAYABLE_ADMIN"],
    )

    # 2. Setup Bill Items exactly matching Section 7
    items = [
        BillItemInput(
            id="item-1",
            original_description="Room rent (Deluxe Ward - 5 Days)",
            category=BillCategory.ROOM_RENT,
            unit_price=Decimal("5000.00"),
            quantity=Decimal("5.00"),
            billed_amount=Decimal("25000.00"),
            days_stay=5,
        ),
        BillItemInput(
            id="item-2",
            original_description="Doctor, nursing, and OT charges",
            category=BillCategory.ASSOCIATE_MEDICAL,
            unit_price=Decimal("60000.00"),
            quantity=Decimal("1.00"),
            billed_amount=Decimal("60000.00"),
        ),
        BillItemInput(
            id="item-3",
            original_description="Pharmacy and medications",
            category=BillCategory.PHARMACY,
            unit_price=Decimal("30000.00"),
            quantity=Decimal("1.00"),
            billed_amount=Decimal("30000.00"),
        ),
        BillItemInput(
            id="item-4",
            original_description="Gloves, masks, and administrative fees",
            category=BillCategory.NON_PAYABLE_CONSUMABLE,
            unit_price=Decimal("8000.00"),
            quantity=Decimal("1.00"),
            billed_amount=Decimal("8000.00"),
        ),
        BillItemInput(
            id="item-5",
            original_description="Diagnostics and lab investigations",
            category=BillCategory.DIAGNOSTICS,
            unit_price=Decimal("27000.00"),
            quantity=Decimal("1.00"),
            billed_amount=Decimal("27000.00"),
        ),
    ]

    # Verify input total before audit
    total_billed = sum(item.billed_amount for item in items)
    assert total_billed == Decimal("150000.00"), "Total bill must be ₹1,50,000"

    # 3. Execute Audit
    result = RuleEngine.audit(items=items, policy=policy)

    # 4. Verify Individual Item Payable Amounts
    item_map = {it.category: it for it in result.items}

    # Room rent: ₹15,000 payable, ₹10,000 deduction
    room_result = item_map[BillCategory.ROOM_RENT]
    assert room_result.billed_amount == Decimal("25000.00")
    assert room_result.payable_amount == Decimal("15000.00")
    assert room_result.deduction_amount == Decimal("10000.00")
    assert room_result.is_room_rent_excess is True

    # Associate medical (Doctor, nursing, OT): reduced to 60% -> ₹36,000 payable, ₹24,000 deduction
    # 3000 / 5000 = 0.60
    assoc_result = item_map[BillCategory.ASSOCIATE_MEDICAL]
    assert assoc_result.billed_amount == Decimal("60000.00")
    assert assoc_result.payable_amount == Decimal("36000.00")
    assert assoc_result.deduction_amount == Decimal("24000.00")
    assert assoc_result.is_proportionate_deduction is True

    # Pharmacy: fully payable ₹30,000, ₹0 deduction
    pharm_result = item_map[BillCategory.PHARMACY]
    assert pharm_result.billed_amount == Decimal("30000.00")
    assert pharm_result.payable_amount == Decimal("30000.00")
    assert pharm_result.deduction_amount == Decimal("0.00")

    # Consumables and administrative fees: non-payable -> ₹0 payable, ₹8,000 deduction
    consumable_result = item_map[BillCategory.NON_PAYABLE_CONSUMABLE]
    assert consumable_result.billed_amount == Decimal("8000.00")
    assert consumable_result.payable_amount == Decimal("0.00")
    assert consumable_result.deduction_amount == Decimal("8000.00")
    assert consumable_result.is_non_payable is True

    # Diagnostics: fully payable ₹27,000, ₹0 deduction
    diag_result = item_map[BillCategory.DIAGNOSTICS]
    assert diag_result.billed_amount == Decimal("27000.00")
    assert diag_result.payable_amount == Decimal("27000.00")
    assert diag_result.deduction_amount == Decimal("0.00")

    # 5. Verify Totals
    summary = result.summary
    assert summary.total_billed == Decimal("150000.00")
    assert summary.total_estimated_payable == Decimal("108000.00")
    assert summary.total_estimated_shortfall == Decimal("42000.00")
    assert summary.reconciliation_verified is True
    assert summary.total_billed == (summary.total_estimated_payable + summary.total_estimated_shortfall)

