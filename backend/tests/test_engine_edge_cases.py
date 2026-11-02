"""
Edge Case and Input Validation Tests for Rule Engine.
"""
from decimal import Decimal
import pytest
from app.engine.categories import BillCategory
from app.engine.rules import PolicyConfig
from app.engine.rule_engine import RuleEngine, BillItemInput

def test_negative_billed_amount_rejected():
    policy = PolicyConfig(name="Standard Policy")
    items = [
        BillItemInput(
            original_description="Invalid Item",
            category=BillCategory.PHARMACY,
            billed_amount=Decimal("-500.00"),
        )
    ]
    with pytest.raises(ValueError, match="negative billed amount"):
        RuleEngine.audit(items=items, policy=policy)

def test_empty_bill_items_rejected():
    policy = PolicyConfig(name="Standard Policy")
    with pytest.raises(ValueError, match="Cannot perform audit on an empty bill"):
        RuleEngine.audit(items=[], policy=policy)

def test_invalid_copay_percentage_rejected():
    with pytest.raises(ValueError, match="Co-pay percentage must be between 0 and 100"):
        PolicyConfig(name="Invalid Policy", copay_percentage=Decimal("120.00"))

def test_invalid_negative_deductible_rejected():
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        PolicyConfig(name="Invalid Policy", deductible_amount=Decimal("-1000.00"))

def test_ambiguous_item_flagged_for_review():
    policy = PolicyConfig(name="Standard Policy")
    items = [
        BillItemInput(
            original_description="Sundry Misc Pack",
            category=BillCategory.AMBIGUOUS_UNCATEGORIZED,
            billed_amount=Decimal("3500.00"),
        )
    ]
    result = RuleEngine.audit(items=items, policy=policy)
    assert result.summary.status == "AUDIT_FLAGGED_FOR_REVIEW"
    assert result.items[0].requires_review is True
    assert len(result.summary.flags_and_warnings) > 0

def test_rounding_precision():
    # Fractional values test
    policy = PolicyConfig(
        name="Fractional Policy",
        copay_percentage=Decimal("15.50"),
    )
    items = [
        BillItemInput(
            original_description="Lab Tests",
            category=BillCategory.DIAGNOSTICS,
            unit_price=Decimal("333.33"),
            quantity=Decimal("3"),
            billed_amount=Decimal("999.99"),
        )
    ]
    result = RuleEngine.audit(items=items, policy=policy)
    # Check that reconciliation holds exactly
    assert result.summary.reconciliation_verified is True
    assert result.summary.total_billed == (result.summary.total_estimated_payable + result.summary.total_estimated_shortfall)

