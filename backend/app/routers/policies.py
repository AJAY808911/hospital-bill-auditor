"""
Policies Router - CRUD and default policy seeding.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.database import get_db
from app.models.policy import PolicyModel
from app.schemas.policy import PolicyCreateSchema, PolicyUpdateSchema, PolicyResponseSchema

router = APIRouter(prefix="/api/policies", tags=["Policies"])

DEFAULT_POLICIES = [
    {
        "name": "Section 7 College Demo Policy",
        "description": "Standard demonstrative policy: Room rent ₹3,000/day, proportionate deduction enabled, consumables non-payable.",
        "sum_insured": 500000.0,
        "room_rent_limit_type": "FIXED_AMOUNT",
        "room_rent_limit_amount": 3000.0,
        "room_rent_limit_percentage": 1.0,
        "icu_rent_limit_amount": 6000.0,
        "apply_proportionate_deduction": True,
        "custom_proportionate_ratio": None,
        "copay_percentage": 0.0,
        "deductible_amount": 0.0,
        "non_payable_categories": "NON_PAYABLE_CONSUMABLE,NON_PAYABLE_ADMIN",
        "length_of_stay_days": 5,
        "is_default": True,
    },
    {
        "name": "Senior Citizen Co-Pay Care",
        "description": "Policy with 20% co-payment and ₹4,000/day room cap for senior citizens.",
        "sum_insured": 500000.0,
        "room_rent_limit_type": "FIXED_AMOUNT",
        "room_rent_limit_amount": 4000.0,
        "room_rent_limit_percentage": 1.0,
        "icu_rent_limit_amount": 8000.0,
        "apply_proportionate_deduction": True,
        "custom_proportionate_ratio": None,
        "copay_percentage": 20.0,
        "deductible_amount": 0.0,
        "non_payable_categories": "NON_PAYABLE_CONSUMABLE,NON_PAYABLE_ADMIN",
        "length_of_stay_days": 4,
        "is_default": False,
    },
    {
        "name": "Super Top-Up (₹25,000 Deductible)",
        "description": "High sum insured (₹15 Lakh) with mandatory initial deductible of ₹25,000 and no room rent cap.",
        "sum_insured": 1500000.0,
        "room_rent_limit_type": "NO_LIMIT",
        "room_rent_limit_amount": 0.0,
        "room_rent_limit_percentage": 0.0,
        "icu_rent_limit_amount": 0.0,
        "apply_proportionate_deduction": False,
        "custom_proportionate_ratio": None,
        "copay_percentage": 0.0,
        "deductible_amount": 25000.0,
        "non_payable_categories": "NON_PAYABLE_CONSUMABLE,NON_PAYABLE_ADMIN",
        "length_of_stay_days": 3,
        "is_default": False,
    },
    {
        "name": "Corporate 1% Sum Insured Capping",
        "description": "Group health insurance with 1% of Sum Insured room-rent limit (₹3,00,000 SI -> ₹3,000/day).",
        "sum_insured": 300000.0,
        "room_rent_limit_type": "PERCENTAGE_OF_SI",
        "room_rent_limit_amount": 3000.0,
        "room_rent_limit_percentage": 1.0,
        "icu_rent_limit_amount": 6000.0,
        "apply_proportionate_deduction": True,
        "custom_proportionate_ratio": None,
        "copay_percentage": 10.0,
        "deductible_amount": 0.0,
        "non_payable_categories": "NON_PAYABLE_CONSUMABLE,NON_PAYABLE_ADMIN",
        "length_of_stay_days": 5,
        "is_default": False,
    }
]

def ensure_default_policies(db: Session):
    count = db.query(PolicyModel).count()
    if count == 0:
        for p_data in DEFAULT_POLICIES:
            policy = PolicyModel(**p_data)
            db.add(policy)
        db.commit()

@router.get("", response_model=List[PolicyResponseSchema])
def list_policies(db: Session = Depends(get_db)):
    ensure_default_policies(db)
    policies = db.query(PolicyModel).order_by(PolicyModel.id.asc()).all()
    # Format non_payable_categories as list
    result = []
    for p in policies:
        cats = [c.strip() for c in (p.non_payable_categories or "").split(",") if c.strip()]
        result.append(
            PolicyResponseSchema(
                id=p.id,
                name=p.name,
                description=p.description,
                sum_insured=p.sum_insured,
                room_rent_limit_type=p.room_rent_limit_type,
                room_rent_limit_amount=p.room_rent_limit_amount,
                room_rent_limit_percentage=p.room_rent_limit_percentage,
                icu_rent_limit_amount=p.icu_rent_limit_amount,
                apply_proportionate_deduction=p.apply_proportionate_deduction,
                custom_proportionate_ratio=p.custom_proportionate_ratio,
                copay_percentage=p.copay_percentage,
                deductible_amount=p.deductible_amount,
                non_payable_categories=cats,
                length_of_stay_days=p.length_of_stay_days,
                is_default=p.is_default,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
        )
    return result

@router.post("", response_model=PolicyResponseSchema, status_code=status.HTTP_201_CREATED)
def create_policy(data: PolicyCreateSchema, db: Session = Depends(get_db)):
    cats_str = ",".join(data.non_payable_categories)
    policy = PolicyModel(
        name=data.name,
        description=data.description,
        sum_insured=float(data.sum_insured),
        room_rent_limit_type=data.room_rent_limit_type.value,
        room_rent_limit_amount=float(data.room_rent_limit_amount),
        room_rent_limit_percentage=float(data.room_rent_limit_percentage),
        icu_rent_limit_amount=float(data.icu_rent_limit_amount) if data.icu_rent_limit_amount else None,
        apply_proportionate_deduction=data.apply_proportionate_deduction,
        custom_proportionate_ratio=float(data.custom_proportionate_ratio) if data.custom_proportionate_ratio else None,
        copay_percentage=float(data.copay_percentage),
        deductible_amount=float(data.deductible_amount),
        non_payable_categories=cats_str,
        length_of_stay_days=data.length_of_stay_days,
        is_default=data.is_default,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return PolicyResponseSchema(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        sum_insured=policy.sum_insured,
        room_rent_limit_type=policy.room_rent_limit_type,
        room_rent_limit_amount=policy.room_rent_limit_amount,
        room_rent_limit_percentage=policy.room_rent_limit_percentage,
        icu_rent_limit_amount=policy.icu_rent_limit_amount,
        apply_proportionate_deduction=policy.apply_proportionate_deduction,
        custom_proportionate_ratio=policy.custom_proportionate_ratio,
        copay_percentage=policy.copay_percentage,
        deductible_amount=policy.deductible_amount,
        non_payable_categories=data.non_payable_categories,
        length_of_stay_days=policy.length_of_stay_days,
        is_default=policy.is_default,
        created_at=policy.created_at,
        updated_at=policy.updated_at,
    )

@router.get("/{id}", response_model=PolicyResponseSchema)
def get_policy(id: int, db: Session = Depends(get_db)):
    p = db.query(PolicyModel).filter(PolicyModel.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Policy not found")
    cats = [c.strip() for c in (p.non_payable_categories or "").split(",") if c.strip()]
    return PolicyResponseSchema(
        id=p.id,
        name=p.name,
        description=p.description,
        sum_insured=p.sum_insured,
        room_rent_limit_type=p.room_rent_limit_type,
        room_rent_limit_amount=p.room_rent_limit_amount,
        room_rent_limit_percentage=p.room_rent_limit_percentage,
        icu_rent_limit_amount=p.icu_rent_limit_amount,
        apply_proportionate_deduction=p.apply_proportionate_deduction,
        custom_proportionate_ratio=p.custom_proportionate_ratio,
        copay_percentage=p.copay_percentage,
        deductible_amount=p.deductible_amount,
        non_payable_categories=cats,
        length_of_stay_days=p.length_of_stay_days,
        is_default=p.is_default,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(id: int, db: Session = Depends(get_db)):
    p = db.query(PolicyModel).filter(PolicyModel.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(p)
    db.commit()
    return None

