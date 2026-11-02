"""
Audits Router - Audit calculation, persistence, reporting, and dashboard analytics.
"""
import json
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit import AuditModel, AuditItemModel
from app.models.policy import PolicyModel
from app.schemas.audit import (
    AuditRequestSchema,
    SavedAuditResponse,
    SavedAuditItemResponse,
    DashboardStatsResponse,
    AuditSummaryCard,
)
from app.engine.rule_engine import RuleEngine, BillItemInput, AuditResult
from app.engine.rules import PolicyConfig, RoomRentLimitType
from app.services.report_generator import ReportGeneratorService

router = APIRouter(prefix="/api/audits", tags=["Audits"])

def resolve_policy_config(data: AuditRequestSchema, db: Session) -> PolicyConfig:
    """Builds a PolicyConfig object from either a policy_id or custom_policy schema."""
    if data.policy_id:
        p = db.query(PolicyModel).filter(PolicyModel.id == data.policy_id).first()
        if not p:
            raise HTTPException(status_code=404, detail=f"Policy with id {data.policy_id} not found.")
        
        cats = [c.strip() for c in (p.non_payable_categories or "").split(",") if c.strip()]
        return PolicyConfig(
            id=p.id,
            name=p.name,
            sum_insured=Decimal(str(p.sum_insured)),
            room_rent_limit_type=RoomRentLimitType(p.room_rent_limit_type),
            room_rent_limit_amount=Decimal(str(p.room_rent_limit_amount)),
            room_rent_limit_percentage=Decimal(str(p.room_rent_limit_percentage)),
            icu_rent_limit_amount=Decimal(str(p.icu_rent_limit_amount)) if p.icu_rent_limit_amount else None,
            apply_proportionate_deduction=p.apply_proportionate_deduction,
            custom_proportionate_ratio=Decimal(str(p.custom_proportionate_ratio)) if p.custom_proportionate_ratio else None,
            copay_percentage=Decimal(str(p.copay_percentage)),
            deductible_amount=Decimal(str(p.deductible_amount)),
            non_payable_categories=cats,
            length_of_stay_days=p.length_of_stay_days,
            description=p.description,
        )
    elif data.custom_policy:
        cp = data.custom_policy
        return PolicyConfig(
            name=cp.name,
            sum_insured=cp.sum_insured,
            room_rent_limit_type=cp.room_rent_limit_type,
            room_rent_limit_amount=cp.room_rent_limit_amount,
            room_rent_limit_percentage=cp.room_rent_limit_percentage,
            icu_rent_limit_amount=cp.icu_rent_limit_amount,
            apply_proportionate_deduction=cp.apply_proportionate_deduction,
            custom_proportionate_ratio=cp.custom_proportionate_ratio,
            copay_percentage=cp.copay_percentage,
            deductible_amount=cp.deductible_amount,
            non_payable_categories=cp.non_payable_categories,
            length_of_stay_days=cp.length_of_stay_days,
            description=cp.description,
        )
    else:
        # Fallback to first available policy or default demo policy
        p = db.query(PolicyModel).first()
        if p:
            cats = [c.strip() for c in (p.non_payable_categories or "").split(",") if c.strip()]
            return PolicyConfig(
                id=p.id,
                name=p.name,
                sum_insured=Decimal(str(p.sum_insured)),
                room_rent_limit_type=RoomRentLimitType(p.room_rent_limit_type),
                room_rent_limit_amount=Decimal(str(p.room_rent_limit_amount)),
                room_rent_limit_percentage=Decimal(str(p.room_rent_limit_percentage)),
                apply_proportionate_deduction=p.apply_proportionate_deduction,
                copay_percentage=Decimal(str(p.copay_percentage)),
                deductible_amount=Decimal(str(p.deductible_amount)),
                non_payable_categories=cats,
                length_of_stay_days=p.length_of_stay_days,
            )
        return PolicyConfig(name="Default Policy")

@router.post("/preview", response_model=AuditResult)
def preview_audit(data: AuditRequestSchema, db: Session = Depends(get_db)):
    """Runs calculation engine in-memory without saving to database (live recalculation)."""
    if not data.items:
        raise HTTPException(status_code=400, detail="Cannot audit an empty bill. Add at least one line item.")
    
    policy_config = resolve_policy_config(data, db)
    try:
        return RuleEngine.audit(items=data.items, policy=policy_config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("", response_model=SavedAuditResponse, status_code=status.HTTP_201_CREATED)
def create_and_save_audit(data: AuditRequestSchema, db: Session = Depends(get_db)):
    """Runs calculation engine and persists the audit and line items to SQLite database."""
    if not data.items:
        raise HTTPException(status_code=400, detail="Cannot audit an empty bill. Add at least one line item.")

    policy_config = resolve_policy_config(data, db)
    
    try:
        calc_result = RuleEngine.audit(items=data.items, policy=policy_config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    summary = calc_result.summary

    # Save Audit Record
    audit_record = AuditModel(
        patient_name=data.patient_name or "Synthetic Patient",
        hospital_name=data.hospital_name or "General Hospital",
        bill_number=data.bill_number or "BILL-SYNTHETIC",
        policy_name=policy_config.name,
        policy_id=policy_config.id,
        total_billed=float(summary.total_billed),
        total_allowed=float(summary.total_allowed_before_policy_deductions),
        item_level_deductions=float(summary.item_level_deductions),
        deductible_applied=float(summary.deductible_applied),
        copay_applied=float(summary.copay_applied),
        copay_percentage=float(summary.copay_percentage),
        sum_insured_excess_applied=float(summary.sum_insured_excess_applied),
        total_estimated_payable=float(summary.total_estimated_payable),
        total_estimated_shortfall=float(summary.total_estimated_shortfall),
        status=summary.status,
        length_of_stay_days=summary.length_of_stay_days,
        proportionate_ratio_applied=float(summary.proportionate_ratio_applied),
        assumptions_json=json.dumps(summary.assumptions_applied),
        flags_json=json.dumps(summary.flags_and_warnings),
        source_document_name=data.source_document_name,
    )
    db.add(audit_record)
    db.flush()

    # Save Line Items
    saved_items = []
    for it in calc_result.items:
        db_item = AuditItemModel(
            audit_id=audit_record.id,
            description=it.description,
            category=it.category.value,
            category_label=it.category_label,
            billed_amount=float(it.billed_amount),
            allowed_amount=float(it.allowed_amount),
            deduction_amount=float(it.deduction_amount),
            payable_amount=float(it.payable_amount),
            deduction_reason=it.deduction_reason,
            is_non_payable=it.is_non_payable,
            is_proportionate_deduction=it.is_proportionate_deduction,
            is_room_rent_excess=it.is_room_rent_excess,
            requires_review=it.requires_review,
            review_reason=it.review_reason,
        )
        db.add(db_item)
        saved_items.append(db_item)

    db.commit()
    db.refresh(audit_record)

    return format_saved_audit(audit_record)

@router.get("", response_model=List[SavedAuditResponse])
def list_audits(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Returns saved audits ordered by newest first."""
    audits = db.query(AuditModel).order_by(AuditModel.created_at.desc()).offset(skip).limit(limit).all()
    return [format_saved_audit(a) for a in audits]

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Computes real-time statistics from persistent database records."""
    audits = db.query(AuditModel).order_by(AuditModel.created_at.desc()).all()
    total_count = len(audits)
    total_billed = sum(a.total_billed for a in audits)
    total_payable = sum(a.total_estimated_payable for a in audits)
    total_shortfall = sum(a.total_estimated_shortfall for a in audits)
    avg_payable_pct = (total_payable / total_billed * 100.0) if total_billed > 0 else 0.0

    recent_cards = [
        AuditSummaryCard(
            id=a.id,
            patient_name=a.patient_name,
            hospital_name=a.hospital_name,
            policy_name=a.policy_name,
            total_billed=a.total_billed,
            total_estimated_payable=a.total_estimated_payable,
            total_estimated_shortfall=a.total_estimated_shortfall,
            status=a.status,
            created_at=a.created_at,
            item_count=len(a.items) if a.items else 0,
        )
        for a in audits[:5]
    ]

    return DashboardStatsResponse(
        total_audits_count=total_count,
        total_billed_volume=round(total_billed, 2),
        total_estimated_payable_volume=round(total_payable, 2),
        total_shortfall_volume=round(total_shortfall, 2),
        average_payable_percentage=round(avg_payable_pct, 1),
        recent_audits=recent_cards,
    )

@router.get("/{id}", response_model=SavedAuditResponse)
def get_audit(id: int, db: Session = Depends(get_db)):
    audit = db.query(AuditModel).filter(AuditModel.id == id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit record not found")
    return format_saved_audit(audit)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_audit(id: int, db: Session = Depends(get_db)):
    audit = db.query(AuditModel).filter(AuditModel.id == id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit record not found")
    db.delete(audit)
    db.commit()
    return None

@router.get("/{id}/report-pdf")
def download_pdf_report(id: int, db: Session = Depends(get_db)):
    audit = db.query(AuditModel).filter(AuditModel.id == id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit record not found")
    
    formatted = format_saved_audit(audit)
    pdf_bytes = ReportGeneratorService.generate_pdf_report(formatted.model_dump())

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Hospital_Bill_Audit_{audit.id}.pdf"
        }
    )

def format_saved_audit(audit: AuditModel) -> SavedAuditResponse:
    assumptions = json.loads(audit.assumptions_json) if audit.assumptions_json else []
    flags = json.loads(audit.flags_json) if audit.flags_json else []
    
    items = [
        SavedAuditItemResponse(
            id=it.id,
            description=it.description,
            category=it.category,
            category_label=it.category_label,
            billed_amount=it.billed_amount,
            allowed_amount=it.allowed_amount,
            deduction_amount=it.deduction_amount,
            payable_amount=it.payable_amount,
            deduction_reason=it.deduction_reason,
            is_non_payable=it.is_non_payable,
            is_proportionate_deduction=it.is_proportionate_deduction,
            is_room_rent_excess=it.is_room_rent_excess,
            requires_review=it.requires_review,
            review_reason=it.review_reason,
        )
        for it in audit.items
    ]

    return SavedAuditResponse(
        id=audit.id,
        patient_name=audit.patient_name,
        hospital_name=audit.hospital_name,
        bill_number=audit.bill_number,
        policy_name=audit.policy_name,
        policy_id=audit.policy_id,
        total_billed=audit.total_billed,
        total_allowed=audit.total_allowed,
        item_level_deductions=audit.item_level_deductions,
        deductible_applied=audit.deductible_applied,
        copay_applied=audit.copay_applied,
        copay_percentage=audit.copay_percentage,
        sum_insured_excess_applied=audit.sum_insured_excess_applied,
        total_estimated_payable=audit.total_estimated_payable,
        total_estimated_shortfall=audit.total_estimated_shortfall,
        status=audit.status,
        length_of_stay_days=audit.length_of_stay_days,
        proportionate_ratio_applied=audit.proportionate_ratio_applied,
        assumptions=assumptions,
        flags=flags,
        source_document_name=audit.source_document_name,
        created_at=audit.created_at,
        items=items,
    )

