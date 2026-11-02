"""
SQLAlchemy Model for Audit Records and Audit Line Items.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class AuditModel(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_name = Column(String(255), nullable=True, default="Synthetic Patient")
    hospital_name = Column(String(255), nullable=True, default="General Hospital")
    bill_number = Column(String(100), nullable=True)
    policy_name = Column(String(255), nullable=False)
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="SET NULL"), nullable=True)
    
    # Financial metrics
    total_billed = Column(Float, nullable=False)
    total_allowed = Column(Float, nullable=False)
    item_level_deductions = Column(Float, nullable=False)
    deductible_applied = Column(Float, nullable=False, default=0.0)
    copay_applied = Column(Float, nullable=False, default=0.0)
    copay_percentage = Column(Float, nullable=False, default=0.0)
    sum_insured_excess_applied = Column(Float, nullable=False, default=0.0)
    total_estimated_payable = Column(Float, nullable=False)
    total_estimated_shortfall = Column(Float, nullable=False)

    # Status & Metadata
    status = Column(String(50), default="AUDIT_CLEAN")
    length_of_stay_days = Column(Integer, default=5)
    proportionate_ratio_applied = Column(Float, default=1.0)
    assumptions_json = Column(Text, nullable=True)
    flags_json = Column(Text, nullable=True)
    source_document_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    items = relationship("AuditItemModel", back_populates="audit", cascade="all, delete-orphan")

class AuditItemModel(Base):
    __tablename__ = "audit_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    category_label = Column(String(100), nullable=True)
    billed_amount = Column(Float, nullable=False)
    allowed_amount = Column(Float, nullable=False)
    deduction_amount = Column(Float, nullable=False)
    payable_amount = Column(Float, nullable=False)
    deduction_reason = Column(Text, nullable=False)
    is_non_payable = Column(Boolean, default=False)
    is_proportionate_deduction = Column(Boolean, default=False)
    is_room_rent_excess = Column(Boolean, default=False)
    requires_review = Column(Boolean, default=False)
    review_reason = Column(Text, nullable=True)

    # Relationship
    audit = relationship("AuditModel", back_populates="items")

