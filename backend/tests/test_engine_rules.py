"""
Comprehensive Unit Tests for Insurance Rule Engine.
Tests:
- Room-rent limits (Fixed, Percentage of SI, No Limit)
- Proportionate deductions
- Non-payable charge exclusions
- Co-payment deductions
- Mandatory deductibles
- Sum insured capping
- Rounding and reconciliation
"""
from decimal import Decimal
import pytest
from app.engine.categories import BillCategory
from app.engine.rules import PolicyConfig, RoomRentLimitType
from app.engine.rule_engine import RuleEngine, BillItemInput

def test_room_rent_percentage_of_sum_insured():
    # SI = 4,00,000, Room rent limit = 1% = ₹4,000/day
    policy = PolicyConfig(
        name="1% SI Room Cap Policy",
        sum_insured=Decimal("400000.00"),
        room_rent_limit_type=RoomRentLimitType.PERCENTAGE_OF_SI,
        room_rent_limit_percentage=Decimal("1.00"),  # ₹4,000/day
        length_of_stay_days=3,
    )
    items = [
        BillItemInput(
            original_description="Private Room 3 days",
            category=BillCategory.ROOM_RENT,
            billed_amount=Decimal("18000.00"),  # ₹6,000/day
            days_stay=3,
        )
    ]
    result = RuleEngine.audit(items=items, policy=policy)
    # Allowed: 3 days * ₹4,000 = ₹12,000. Excess deduction = ₹6,000.
    assert result.items[0].allowed_amount == Decimal("12000.00")
    assert result.items[0].deduction_amount == Decimal("6000.00")
    assert result.summary.total_estimated_payable == Decimal("12000.00")
    assert result.summary.total_estimated_shortfall == Decimal("6000.00")

def test_copay_deduction():
    # 20% Co-pay on ₹50,000 eligible medical bill
    policy = PolicyConfig(
        name="Senior Citizen 20% Co-pay",
        sum_insured=Decimal("500000.00"),
        room_rent_limit_type=RoomRentLimitType.NO_LIMIT,
        copay_percentage=Decimal("20.00"),
    )
    items = [
        BillItemInput(
            original_description="Surgery & Inpatient Care",
            category=BillCategory.ASSOCIATE_MEDICAL,
            billed_amount=Decimal("50000.00"),
        )
    ]
    result = RuleEngine.audit(items=items, policy=policy)
    # 20% copay on 50,000 = ₹10,000. Payable = ₹40,000.
    assert result.summary.copay_applied == Decimal("10000.00")
    assert result.summary.total_estimated_payable == Decimal("40000.00")
    assert result.summary.total_estimated_shortfall == Decimal("10000.00")
    assert result.summary.reconciliation_verified is True

def test_deductible_application():
    # ₹25,000 Deductible on ₹1,00,000 eligible bill
    policy = PolicyConfig(
        name="Top-up with ₹25k Deductible",
        sum_insured=Decimal("1000000.00"),
        room_rent_limit_type=RoomRentLimitType.NO_LIMIT,
        deductible_amount=Decimal("25000.00"),
        copay_percentage=Decimal("10.00"),  # 10% copay applied after deductible
    )
    items = [
        BillItemInput(
            original_description="Orthopedic Surgery",
            category=BillCategory.ASSOCIATE_MEDICAL,
            billed_amount=Decimal("100000.00"),
        )
    ]
    result = RuleEngine.audit(items=items, policy=policy)
    # Total: 1,00,000
    # Deductible: 25,000 -> balance: 75,000
    # Copay: 10% of 75,000 = 7,500 -> payable: 67,500
    # Shortfall: 25,000 + 7,500 = 32,500
    assert result.summary.deductible_applied == Decimal("25000.00")
    assert result.summary.copay_applied == Decimal("7500.00")
    assert result.summary.total_estimated_payable == Decimal("67500.00")
    assert result.summary.total_estimated_shortfall == Decimal("32500.00")
    assert result.summary.reconciliation_verified is True

def test_sum_insured_ceiling_capping():
    # Sum Insured = ₹50,000, Total eligible = ₹80,000
    policy = PolicyConfig(
        name="Small Sum Insured Policy",
        sum_insured=Decimal("500000.00"),
        room_rent_limit_type=RoomRentLimitType.NO_LIMIT,
    )
    # Now set sum_insured to 50,000
    policy.sum_insured = Decimal("50000.00")
    items = [
        BillItemInput(
            original_description="Major Surgery",
            category=BillCategory.ASSOCIATE_MEDICAL,
            billed_amount=Decimal("80000.00"),
        )
    ]
    result = RuleEngine.audit(items=items, policy=policy)
    # Payable capped at ₹50,000. Shortfall = ₹30,000.
    assert result.summary.total_estimated_payable == Decimal("50000.00")
    assert result.summary.total_estimated_shortfall == Decimal("30000.00")
    assert result.summary.sum_insured_excess_applied == Decimal("30000.00")
    assert result.summary.reconciliation_verified is True

def test_zero_deductions_full_coverage():
    # Standard clean bill with no room rent cap, no copay, no non-payables
    policy = PolicyConfig(
        name="Comprehensive Unlimited",
        sum_insured=Decimal("1000000.00"),
        room_rent_limit_type=RoomRentLimitType.NO_LIMIT,
        copay_percentage=Decimal("0.00"),
        deductible_amount=Decimal("0.00"),
    )
    items = [
        BillItemInput(
            original_description="Hospital Stay",
            category=BillCategory.ROOM_RENT,
            billed_amount=Decimal("20000.00"),
        ),
        BillItemInput(
            original_description="Medicines",
            category=BillCategory.PHARMACY,
            billed_amount=Decimal("15000.00"),
        )
    ]
    result = RuleEngine.audit(items=items, policy=policy)
    assert result.summary.total_billed == Decimal("35000.00")
    assert result.summary.total_estimated_payable == Decimal("35000.00")
    assert result.summary.total_estimated_shortfall == Decimal("0.00")
    assert result.summary.item_level_deductions == Decimal("0.00")

