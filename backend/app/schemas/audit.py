"""
Pydantic Schemas for Audit requests, normalization, calculation, and persistence.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.engine.categories import BillCategory
from app.engine.rule_engine import BillItemInput, ItemAuditBreakdown, AuditSummary
from app.schemas.policy import PolicyCreateSchema

class AuditRequestSchema(BaseModel):
    patient_name: Optional[str] = "Synthetic Patient"
    hospital_name: Optional[str] = "General Hospital"
    bill_number: Optional[str] = None
    policy_id: Optional[int] = None
    custom_policy: Optional[PolicyCreateSchema] = None
    items: List[BillItemInput]
    source_document_name: Optional[str] = None

class SavedAuditItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    category: str
    category_label: Optional[str] = None
    billed_amount: float
    allowed_amount: float
    deduction_amount: float
    payable_amount: float
    deduction_reason: str
    is_non_payable: bool
    is_proportionate_deduction: bool
    is_room_rent_excess: bool
    requires_review: bool
    review_reason: Optional[str] = None

class SavedAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_name: Optional[str] = None
    hospital_name: Optional[str] = None
    bill_number: Optional[str] = None
    policy_name: str
    policy_id: Optional[int] = None
    total_billed: float
    total_allowed: float
    item_level_deductions: float
    deductible_applied: float
    copay_applied: float
    copay_percentage: float
    sum_insured_excess_applied: float
    total_estimated_payable: float
    total_estimated_shortfall: float
    status: str
    length_of_stay_days: int
    proportionate_ratio_applied: float
    assumptions: List[str]
    flags: List[str]
    source_document_name: Optional[str] = None
    created_at: datetime
    items: List[SavedAuditItemResponse]

class AuditSummaryCard(BaseModel):
    id: int
    patient_name: Optional[str] = None
    hospital_name: Optional[str] = None
    policy_name: str
    total_billed: float
    total_estimated_payable: float
    total_estimated_shortfall: float
    status: str
    created_at: datetime
    item_count: int

class DashboardStatsResponse(BaseModel):
    total_audits_count: int
    total_billed_volume: float
    total_estimated_payable_volume: float
    total_shortfall_volume: float
    average_payable_percentage: float
    recent_audits: List[AuditSummaryCard]

