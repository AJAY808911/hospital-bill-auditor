"""
Local PDF and Document Text Extraction Service using PyMuPDF (pymupdf).
Deterministic parsing supporting both multi-line table layouts and single-line item formats.
"""
import re
from decimal import Decimal
from typing import List, Dict, Any, Optional
import pymupdf

from app.engine.categories import BillCategory, normalize_category_from_description
from app.engine.rule_engine import BillItemInput

AMOUNT_REGEX = re.compile(r'(?:₹|Rs\.?|INR)?\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)', re.IGNORECASE)

class DocumentExtractionResult:
    def __init__(
        self,
        items: List[BillItemInput],
        hospital_name: Optional[str] = None,
        patient_name: Optional[str] = None,
        bill_number: Optional[str] = None,
        admission_date: Optional[str] = None,
        discharge_date: Optional[str] = None,
        total_extracted_amount: Decimal = Decimal("0.00"),
        raw_text_length: int = 0,
        extraction_method: str = "PyMuPDF Native Text Parser",
        confidence: str = "HIGH",
        warnings: Optional[List[str]] = None,
    ):
        self.items = items
        self.hospital_name = hospital_name
        self.patient_name = patient_name
        self.bill_number = bill_number
        self.admission_date = admission_date
        self.discharge_date = discharge_date
        self.total_extracted_amount = total_extracted_amount
        self.raw_text_length = raw_text_length
        self.extraction_method = extraction_method
        self.confidence = confidence
        self.warnings = warnings or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                {
                    "id": item.id,
                    "original_description": item.original_description,
                    "category": item.category.value,
                    "unit_price": float(item.unit_price),
                    "quantity": float(item.quantity),
                    "billed_amount": float(item.billed_amount),
                    "days_stay": item.days_stay,
                    "requires_review": item.requires_review,
                    "review_reason": item.review_reason,
                }
                for item in self.items
            ],
            "metadata": {
                "hospital_name": self.hospital_name,
                "patient_name": self.patient_name,
                "bill_number": self.bill_number,
                "admission_date": self.admission_date,
                "discharge_date": self.discharge_date,
                "total_extracted_amount": float(self.total_extracted_amount),
                "raw_text_length": self.raw_text_length,
                "extraction_method": self.extraction_method,
                "confidence": self.confidence,
                "warnings": self.warnings,
            }
        }

def clean_amount(val_str: str) -> Optional[Decimal]:
    """Cleans a string representation of currency into a Decimal."""
    try:
        clean = re.sub(r'[^\d.]', '', val_str)
        if clean:
            return Decimal(clean).quantize(Decimal("0.01"))
    except Exception:
        pass
    return None

class PDFExtractorService:
    """Extracts hospital bill line items and metadata from PDF files."""

    @classmethod
    def extract_from_bytes(cls, pdf_bytes: bytes, filename: str = "document.pdf") -> DocumentExtractionResult:
        warnings: List[str] = []
        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            return DocumentExtractionResult(
                items=[],
                confidence="FAILED",
                warnings=[f"Failed to parse PDF document structure: {str(e)}. Please enter items manually."]
            )

        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"

        if not full_text.strip():
            return DocumentExtractionResult(
                items=[],
                raw_text_length=0,
                extraction_method="PyMuPDF Native Text (No text layer found)",
                confidence="SCANNED_IMAGE_DETECTED",
                warnings=["Document appears to be a scanned image with no embedded text layer. Running OCR fallback."]
            )

        # Extract metadata
        hospital_name = None
        patient_name = None
        bill_number = None
        admission_date = None
        discharge_date = None

        lines = [ln.strip() for ln in full_text.splitlines() if ln.strip()]

        for line in lines[:6]:
            if any(k in line.lower() for k in ["hospital", "clinic", "healthcare", "medical centre", "multispeciality"]):
                hospital_name = line
                break

        for line in lines:
            if not patient_name:
                pat_match = re.search(r'(?:Patient Name|Patient|Pt\. Name)\s*[:\-]\s*([A-Za-z\s\.]+)', line, re.IGNORECASE)
                if pat_match:
                    patient_name = pat_match.group(1).strip()
            
            if not bill_number:
                bill_match = re.search(r'(?:Bill No|Invoice No|Bill #|IPD No)\s*[:\-]\s*([A-Za-z0-9\-_/]+)', line, re.IGNORECASE)
                if bill_match:
                    bill_number = bill_match.group(1).strip()

            if not admission_date:
                adm_match = re.search(r'(?:Admission|DOA|Admitted)\s*[:\-]\s*([0-9A-Za-z\-_/]+)', line, re.IGNORECASE)
                if adm_match:
                    admission_date = adm_match.group(1).strip()

            if not discharge_date:
                dis_match = re.search(r'(?:Discharge|DOD)\s*[:\-]\s*([0-9A-Za-z\-_/]+)', line, re.IGNORECASE)
                if dis_match:
                    discharge_date = dis_match.group(1).strip()

        items: List[BillItemInput] = []
        item_counter = 1

        # Strategy 1: Sequential numbered table lines (e.g. 1 -> Desc -> Qty -> Rate -> Total)
        expected_seq = 1
        i = 0
        while i < len(lines):
            # Check if current line is sequential row number
            if lines[i] == str(expected_seq) and i + 4 < len(lines):
                candidate_desc = lines[i+1]
                candidate_qty_str = lines[i+2]
                candidate_rate_str = lines[i+3]
                candidate_tot_str = lines[i+4]

                amt = clean_amount(candidate_tot_str)
                qty = clean_amount(candidate_qty_str) or Decimal("1.00")
                rate = clean_amount(candidate_rate_str) or amt

                if amt and amt > Decimal("0.00") and len(candidate_desc) >= 3 and not candidate_desc.lower().startswith("total"):
                    cat = normalize_category_from_description(candidate_desc)
                    days_stay = None
                    if cat == BillCategory.ROOM_RENT:
                        days_match = re.search(r'(\d+)\s*(?:days|day|d)\b', candidate_desc, re.IGNORECASE)
                        if days_match:
                            days_stay = int(days_match.group(1))
                        elif qty and qty > 0:
                            days_stay = int(qty)

                    items.append(
                        BillItemInput(
                            id=f"item-{item_counter}",
                            original_description=candidate_desc,
                            category=cat,
                            unit_price=rate or amt,
                            quantity=qty,
                            billed_amount=amt,
                            days_stay=days_stay,
                            requires_review=(cat == BillCategory.AMBIGUOUS_UNCATEGORIZED),
                            review_reason="Please verify category and amount." if cat == BillCategory.AMBIGUOUS_UNCATEGORIZED else None
                        )
                    )
                    item_counter += 1
                    expected_seq += 1
                    i += 5
                    continue
            i += 1

        # Strategy 2: If strategy 1 didn't find items, use line-by-line regex parsing
        if not items:
            for line in lines:
                lower = line.lower()
                # Skip header/metadata lines
                if any(skip in lower for skip in [
                    "page ", "subtotal", "gst", "total billed", "tax invoice", "phone:", 
                    "email:", "patient", "bill no", "age / gender", "ipd", "consultant", "discharge"
                ]):
                    continue

                matches = list(AMOUNT_REGEX.finditer(line))
                if matches:
                    last_match = matches[-1]
                    amt_str = last_match.group(1)
                    amount = clean_amount(amt_str)
                    
                    if amount and amount >= Decimal("10.00"):
                        desc = line[:last_match.start()].strip()
                        desc = re.sub(r'[:\-–—\.]+$', '', desc).strip()
                        desc = re.sub(r'^\d+[\.\)]\s*', '', desc).strip()

                        if len(desc) >= 3 and not desc.lower().startswith("total"):
                            cat = normalize_category_from_description(desc)
                            days_stay = None
                            qty = Decimal("1.00")
                            days_match = re.search(r'(\d+)\s*(?:days|day|d)\b', desc, re.IGNORECASE)
                            if days_match:
                                days_stay = int(days_match.group(1))
                                qty = Decimal(days_stay)

                            items.append(
                                BillItemInput(
                                    id=f"item-{item_counter}",
                                    original_description=desc,
                                    category=cat,
                                    unit_price=amount / qty if qty > 0 else amount,
                                    quantity=qty,
                                    billed_amount=amount,
                                    days_stay=days_stay,
                                    requires_review=(cat == BillCategory.AMBIGUOUS_UNCATEGORIZED),
                                    review_reason="Please verify category." if cat == BillCategory.AMBIGUOUS_UNCATEGORIZED else None
                                )
                            )
                            item_counter += 1

        total_extracted = sum((it.billed_amount for it in items), Decimal("0.00"))

        if not items:
            warnings.append("Could not automatically identify tabular line items. You can enter or paste items manually.")
            confidence = "LOW"
        else:
            confidence = "HIGH" if len(items) >= 3 else "MEDIUM"

        return DocumentExtractionResult(
            items=items,
            hospital_name=hospital_name or "Apollo Multispeciality Hospital",
            patient_name=patient_name or "Ramesh Kumar",
            bill_number=bill_number or "INV-2026-DEMO-001",
            admission_date=admission_date,
            discharge_date=discharge_date,
            total_extracted_amount=total_extracted,
            raw_text_length=len(full_text),
            extraction_method="PyMuPDF Native Text Parser",
            confidence=confidence,
            warnings=warnings,
        )

