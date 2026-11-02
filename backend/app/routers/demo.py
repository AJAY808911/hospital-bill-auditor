"""
Demonstration Case Router - Specifically implements and runs the Section 7 college viva demo case.
"""
from decimal import Decimal
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.policy import PolicyModel
from app.schemas.audit import AuditRequestSchema, SavedAuditResponse
from app.engine.categories import BillCategory
from app.engine.rule_engine import BillItemInput
from app.routers.audits import create_and_save_audit

router = APIRouter(prefix="/api/demo", tags=["Demo Case"])

DEMO_ITEMS = [
    {
        "id": "demo-item-1",
        "original_description": "Room rent (Deluxe Room - 5 Days @ ₹5,000/day)",
        "category": "ROOM_RENT",
        "unit_price": 5000.0,
        "quantity": 5.0,
        "billed_amount": 25000.0,
        "days_stay": 5,
    },
    {
        "id": "demo-item-2",
        "original_description": "Doctor, nursing, and OT charges",
        "category": "ASSOCIATE_MEDICAL",
        "unit_price": 60000.0,
        "quantity": 1.0,
        "billed_amount": 60000.0,
    },
    {
        "id": "demo-item-3",
        "original_description": "Pharmacy medications and IV fluids",
        "category": "PHARMACY",
        "unit_price": 30000.0,
        "quantity": 1.0,
        "billed_amount": 30000.0,
    },
    {
        "id": "demo-item-4",
        "original_description": "Gloves, masks, and administrative fees",
        "category": "NON_PAYABLE_CONSUMABLE",
        "unit_price": 8000.0,
        "quantity": 1.0,
        "billed_amount": 8000.0,
    },
    {
        "id": "demo-item-5",
        "original_description": "Diagnostics and laboratory investigations",
        "category": "DIAGNOSTICS",
        "unit_price": 27000.0,
        "quantity": 1.0,
        "billed_amount": 27000.0,
    },
]

DEMO_POLICY = {
    "name": "Section 7 College Viva Demo Policy",
    "description": "Room rent ₹3,000/day, proportionate deduction reduces doctor/OT to 60%, consumables non-payable.",
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
}

@router.get("/data")
def get_demo_data():
    """Returns the pre-configured demonstration data for single-click loading into the UI."""
    return {
        "bill": {
            "patient_name": "Ramesh Kumar (Synthetic Case)",
            "hospital_name": "Apollo Multispeciality Hospital",
            "bill_number": "INV-2026-DEMO-001",
            "admission_date": "2026-10-15",
            "discharge_date": "2026-10-20",
            "total_billed": 150000.0,
            "items": DEMO_ITEMS,
        },
        "policy": DEMO_POLICY,
        "expected_results": {
            "total_billed": 150000.0,
            "total_estimated_payable": 108000.0,
            "total_estimated_shortfall": 42000.0,
            "breakdown": {
                "room_rent": {"billed": 25000.0, "payable": 15000.0, "deduction": 10000.0},
                "doctor_nursing_ot": {"billed": 60000.0, "payable": 36000.0, "deduction": 24000.0},
                "pharmacy": {"billed": 30000.0, "payable": 30000.0, "deduction": 0.0},
                "gloves_masks_admin": {"billed": 8000.0, "payable": 0.0, "deduction": 8000.0},
                "diagnostics": {"billed": 27000.0, "payable": 27000.0, "deduction": 0.0},
            }
        }
    }

@router.post("/run", response_model=SavedAuditResponse, status_code=status.HTTP_201_CREATED)
def execute_demo_audit(db: Session = Depends(get_db)):
    """Executes the Section 7 demonstration audit immediately and saves it to history."""
    # Find or create demo policy
    policy = db.query(PolicyModel).filter(PolicyModel.name == DEMO_POLICY["name"]).first()
    if not policy:
        policy = PolicyModel(**DEMO_POLICY)
        db.add(policy)
        db.commit()
        db.refresh(policy)

    req = AuditRequestSchema(
        patient_name="Ramesh Kumar (Viva Demo)",
        hospital_name="Apollo Multispeciality Hospital",
        bill_number="INV-2026-DEMO-001",
        policy_id=policy.id,
        items=[
            BillItemInput(
                id=it["id"],
                original_description=it["original_description"],
                category=BillCategory(it["category"]),
                unit_price=Decimal(str(it["unit_price"])),
                quantity=Decimal(str(it["quantity"])),
                billed_amount=Decimal(str(it["billed_amount"])),
                days_stay=it.get("days_stay"),
            )
            for it in DEMO_ITEMS
        ],
        source_document_name="Section_7_Demonstration_Sample.pdf"
    )

    return create_and_save_audit(data=req, db=db)
