"""
Policy Configuration and Rule Definitions for Health Insurance Calculations.
"""
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class RoomRentLimitType(str, Enum):
    FIXED_AMOUNT = "FIXED_AMOUNT"
    PERCENTAGE_OF_SI = "PERCENTAGE_OF_SI"
    NO_LIMIT = "NO_LIMIT"

def quantize_inr(value: Decimal) -> Decimal:
    """Rounds a Decimal value to 2 decimal places using standard ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class PolicyConfig(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, description="Policy name, e.g. Demo Comprehensive Care")
    sum_insured: Decimal = Field(default=Decimal("500000.00"), description="Total sum insured in INR")
    room_rent_limit_type: RoomRentLimitType = Field(default=RoomRentLimitType.FIXED_AMOUNT)
    room_rent_limit_amount: Decimal = Field(default=Decimal("3000.00"), description="Per-day room rent cap in INR")
    room_rent_limit_percentage: Decimal = Field(default=Decimal("1.00"), description="Room rent percentage cap (e.g. 1% of SI)")
    icu_rent_limit_amount: Optional[Decimal] = Field(default=Decimal("6000.00"), description="Per-day ICU rent cap in INR")
    
    # Proportionate deduction
    apply_proportionate_deduction: bool = Field(default=True, description="Whether to apply proportionate deduction on associate medical charges")
    custom_proportionate_ratio: Optional[Decimal] = Field(default=None, description="Explicit proportionate ratio override (0.0 to 1.0)")
    
    # Co-pay and deductible
    copay_percentage: Decimal = Field(default=Decimal("0.00"), description="Co-payment percentage (0-100%)")
    deductible_amount: Decimal = Field(default=Decimal("0.00"), description="Mandatory deductible in INR")
    
    # Non-payables
    non_payable_categories: List[str] = Field(
        default_factory=lambda: ["NON_PAYABLE_CONSUMABLE", "NON_PAYABLE_ADMIN"],
        description="Categories treated as 100% non-payable"
    )
    
    # Length of stay default (used if not explicitly stated on bill)
    length_of_stay_days: int = Field(default=5, ge=1, description="Length of stay in days")
    description: Optional[str] = "Standard health insurance policy configuration"

    @field_validator("sum_insured")
    @classmethod
    def validate_sum_insured(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Sum insured must be greater than zero.")
        return quantize_inr(v)

    @field_validator("room_rent_limit_amount", "deductible_amount")
    @classmethod
    def validate_non_negative_amounts(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Amount cannot be negative.")
        return quantize_inr(v)

    @field_validator("copay_percentage")
    @classmethod
    def validate_copay(cls, v: Decimal) -> Decimal:
        if v < 0 or v > 100:
            raise ValueError("Co-pay percentage must be between 0 and 100.")
        return quantize_inr(v)

    @field_validator("custom_proportionate_ratio")
    @classmethod
    def validate_custom_ratio(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            if v < 0 or v > 1:
                raise ValueError("Custom proportionate ratio must be between 0.0 and 1.0.")
            return v.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        return None

