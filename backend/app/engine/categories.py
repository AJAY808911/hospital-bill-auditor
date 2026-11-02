"""
Standard Bill Item Categories and Categorization Keywords
Aligns with Indian Health Insurance (IRDAI) guidelines and billing norms.
"""
from enum import Enum
from typing import List, Dict

class BillCategory(str, Enum):
    ROOM_RENT = "ROOM_RENT"
    ASSOCIATE_MEDICAL = "ASSOCIATE_MEDICAL"
    PHARMACY = "PHARMACY"
    DIAGNOSTICS = "DIAGNOSTICS"
    NON_PAYABLE_CONSUMABLE = "NON_PAYABLE_CONSUMABLE"
    NON_PAYABLE_ADMIN = "NON_PAYABLE_ADMIN"
    SURGERY_IMPLANT = "SURGERY_IMPLANT"
    OTHER_MEDICAL = "OTHER_MEDICAL"
    AMBIGUOUS_UNCATEGORIZED = "AMBIGUOUS_UNCATEGORIZED"

CATEGORY_METADATA: Dict[BillCategory, Dict[str, str]] = {
    BillCategory.ROOM_RENT: {
        "label": "Room Rent & ICU",
        "description": "Hospital accommodation, bed charges, nursing room charges, and ICU charges.",
        "default_payable": "CAPPED",
    },
    BillCategory.ASSOCIATE_MEDICAL: {
        "label": "Doctor, Nursing, OT & Surgery",
        "description": "Consultation fees, surgeon charges, anesthetist, nursing care, and operating theater charges.",
        "default_payable": "PROPORTIONATE_ELIGIBLE",
    },
    BillCategory.PHARMACY: {
        "label": "Pharmacy & Medications",
        "description": "In-patient medicines, prescription drugs, IV fluids, and therapeutic infusions.",
        "default_payable": "PAYABLE",
    },
    BillCategory.DIAGNOSTICS: {
        "label": "Diagnostics & Lab Investigations",
        "description": "Blood tests, pathology, radiology, X-ray, MRI, CT scans, and ECG.",
        "default_payable": "PAYABLE",
    },
    BillCategory.NON_PAYABLE_CONSUMABLE: {
        "label": "Consumables & PPE (Non-Payable)",
        "description": "Gloves, masks, PPE kits, aprons, bedsheets, thermometer, wipes, and disposable items.",
        "default_payable": "NON_PAYABLE",
    },
    BillCategory.NON_PAYABLE_ADMIN: {
        "label": "Administrative & Misc (Non-Payable)",
        "description": "Registration fees, admission charge, documentation, maintenance, bio-waste disposal fees.",
        "default_payable": "NON_PAYABLE",
    },
    BillCategory.SURGERY_IMPLANT: {
        "label": "Implants & Prosthetics",
        "description": "Stents, orthopedic implants, pacemakers, lenses, mesh, and specialized prosthetics.",
        "default_payable": "PAYABLE",
    },
    BillCategory.OTHER_MEDICAL: {
        "label": "Other Medical Services",
        "description": "Physiotherapy, dietary advice, dialysis, ambulance, oxygen administration.",
        "default_payable": "PAYABLE",
    },
    BillCategory.AMBIGUOUS_UNCATEGORIZED: {
        "label": "Ambiguous / Needs Review",
        "description": "Items with vague descriptions requiring manual classification.",
        "default_payable": "REQUIRES_REVIEW",
    },
}

# Heuristic keyword matchers for normalization
KEYWORD_MAPPINGS: Dict[BillCategory, List[str]] = {
    BillCategory.ROOM_RENT: [
        "room", "bed", "icu", "nicu", "picu", "ward", "deluxe", "twin sharing", 
        "single room", "suite", "board", "accommodation", "nursing room"
    ],
    BillCategory.ASSOCIATE_MEDICAL: [
        "doctor", "dr.", "physician", "surgeon", "consultant", "consultation",
        "visit", "anesthesia", "anesthetist", "ot charge", "ot charges", 
        "operation theatre", "operation theater", "nursing fee", "nursing charges",
        "assistant surgeon", "procedural charge"
    ],
    BillCategory.PHARMACY: [
        "pharmacy", "medicine", "medication", "drug", "tablet", "capsule", 
        "injection", "iv fluid", "saline", "syrup", "infusion", "dextrose", "antibiotic"
    ],
    BillCategory.DIAGNOSTICS: [
        "lab", "laboratory", "pathology", "test", "investigation", "blood",
        "x-ray", "xray", "mri", "ct scan", "ultrasound", "usg", "ecg", "echo",
        "biopsy", "culture", "urine", "cbc", "lipid", "radiology", "diagnostics"
    ],
    BillCategory.NON_PAYABLE_CONSUMABLE: [
        "glove", "gloves", "mask", "masks", "ppe", "gown", "cotton", "gauze",
        "bandage", "sanitizer", "disposable", "apron", "thermometer", "needle",
        "syringe", "spirit", "swab", "tape", "cannula fixator", "tissue", "bedsheet",
        "diaper", "soap", "toothpaste"
    ],
    BillCategory.NON_PAYABLE_ADMIN: [
        "registration", "admission fee", "admission charge", "admin fee", 
        "administrative", "record", "documentation", "file charge", 
        "service charge", "maintenance", "bio medical", "waste management", 
        "biomedical waste", "discharge summary", "visitor pass", "convenience"
    ],
    BillCategory.SURGERY_IMPLANT: [
        "stent", "implant", "pacemaker", "mesh", "screw", "plate", "lens", "prosthesis"
    ],
}

def normalize_category_from_description(desc: str) -> BillCategory:
    """Classifies a bill item description into a standard BillCategory using keyword heuristics."""
    if not desc or not desc.strip():
        return BillCategory.AMBIGUOUS_UNCATEGORIZED
    
    clean_desc = desc.lower().strip()
    
    # Check specific non-payable admin and consumable patterns first
    for kw in KEYWORD_MAPPINGS[BillCategory.NON_PAYABLE_ADMIN]:
        if kw in clean_desc:
            return BillCategory.NON_PAYABLE_ADMIN
            
    for kw in KEYWORD_MAPPINGS[BillCategory.NON_PAYABLE_CONSUMABLE]:
        if kw in clean_desc:
            return BillCategory.NON_PAYABLE_CONSUMABLE
            
    for kw in KEYWORD_MAPPINGS[BillCategory.ROOM_RENT]:
        if kw in clean_desc:
            return BillCategory.ROOM_RENT
            
    for kw in KEYWORD_MAPPINGS[BillCategory.ASSOCIATE_MEDICAL]:
        if kw in clean_desc:
            return BillCategory.ASSOCIATE_MEDICAL
            
    for kw in KEYWORD_MAPPINGS[BillCategory.PHARMACY]:
        if kw in clean_desc:
            return BillCategory.PHARMACY
            
    for kw in KEYWORD_MAPPINGS[BillCategory.DIAGNOSTICS]:
        if kw in clean_desc:
            return BillCategory.DIAGNOSTICS

    for kw in KEYWORD_MAPPINGS[BillCategory.SURGERY_IMPLANT]:
        if kw in clean_desc:
            return BillCategory.SURGERY_IMPLANT

    return BillCategory.AMBIGUOUS_UNCATEGORIZED

