"""
SQLAlchemy Model for Insurance Policy Configurations.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class PolicyModel(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sum_insured = Column(Float, nullable=False, default=500000.0)
    room_rent_limit_type = Column(String(50), nullable=False, default="FIXED_AMOUNT")
    room_rent_limit_amount = Column(Float, nullable=False, default=3000.0)
    room_rent_limit_percentage = Column(Float, nullable=False, default=1.0)
    icu_rent_limit_amount = Column(Float, nullable=True, default=6000.0)
    apply_proportionate_deduction = Column(Boolean, nullable=False, default=True)
    custom_proportionate_ratio = Column(Float, nullable=True)
    copay_percentage = Column(Float, nullable=False, default=0.0)
    deductible_amount = Column(Float, nullable=False, default=0.0)
    non_payable_categories = Column(Text, nullable=True, default="NON_PAYABLE_CONSUMABLE,NON_PAYABLE_ADMIN")
    length_of_stay_days = Column(Integer, nullable=False, default=5)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

