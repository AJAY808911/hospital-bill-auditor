"""
Pydantic Schemas for Policy API requests and responses.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.engine.rules import RoomRentLimitType

class PolicyCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sum_insured: Decimal = Field(default=Decimal("500000.00"), ge=1000)
    room_rent_limit_type: RoomRentLimitType = Field(default=RoomRentLimitType.FIXED_AMOUNT)
    room_rent_limit_amount: Decimal = Field(default=Decimal("3000.00"), ge=0)
    room_rent_limit_percentage: Decimal = Field(default=Decimal("1.00"), ge=0, le=100)
    icu_rent_limit_amount: Optional[Decimal] = Field(default=Decimal("6000.00"), ge=0)
    apply_proportionate_deduction: bool = Field(default=True)
    custom_proportionate_ratio: Optional[Decimal] = Field(default=None, ge=0, le=1)
    copay_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    deductible_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    non_payable_categories: List[str] = Field(
        default_factory=lambda: ["NON_PAYABLE_CONSUMABLE", "NON_PAYABLE_ADMIN"]
    )
    length_of_stay_days: int = Field(default=5, ge=1)
    is_default: bool = False

class PolicyUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sum_insured: Optional[Decimal] = None
    room_rent_limit_type: Optional[RoomRentLimitType] = None
    room_rent_limit_amount: Optional[Decimal] = None
    room_rent_limit_percentage: Optional[Decimal] = None
    icu_rent_limit_amount: Optional[Decimal] = None
    apply_proportionate_deduction: Optional[bool] = None
    custom_proportionate_ratio: Optional[Decimal] = None
    copay_percentage: Optional[Decimal] = None
    deductible_amount: Optional[Decimal] = None
    non_payable_categories: Optional[List[str]] = None
    length_of_stay_days: Optional[int] = None
    is_default: Optional[bool] = None

class PolicyResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    sum_insured: float
    room_rent_limit_type: str
    room_rent_limit_amount: float
    room_rent_limit_percentage: float
    icu_rent_limit_amount: Optional[float] = None
    apply_proportionate_deduction: bool
    custom_proportionate_ratio: Optional[float] = None
    copay_percentage: float
    deductible_amount: float
    non_payable_categories: List[str]
    length_of_stay_days: int
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

