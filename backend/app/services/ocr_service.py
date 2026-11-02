"""
Local OCR Extraction Service using pytesseract and Pillow/OpenCV.
Gracefully detects if Tesseract binary is available on the system.
If Tesseract is not installed, provides clear guidance and instructions.
"""
import io
import shutil
from typing import Optional, List
from PIL import Image
import pytesseract
import pymupdf

from app.services.extractor import DocumentExtractionResult, clean_amount
from app.engine.categories import normalize_category_from_description, BillCategory
from app.engine.rule_engine import BillItemInput
from decimal import Decimal
import re

AMOUNT_REGEX = re.compile(r'(?:₹|Rs\.?|INR)?\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)', re.IGNORECASE)

class OCRService:
    @staticmethod
    def is_tesseract_available() -> bool:
        """Checks if tesseract executable is installed and reachable."""
        return shutil.which("tesseract") is not None

    @classmethod
    def get_ocr_status(cls) -> dict:
        available = cls.is_tesseract_available()
        return {
            "available": available,
            "engine": "Tesseract OCR (Local)",
            "message": (
                "Tesseract OCR is detected and active for scanned bills."
                if available
                else "Tesseract OCR executable was not found on system PATH. "
                     "For scanned bills, install Tesseract OCR (e.g. 'winget install UB-Mannheim.TesseractOCR' on Windows) "
                     "or use digital text PDFs / manual entry."
            ),
            "install_instructions": {
                "windows": "winget install UB-Mannheim.TesseractOCR or download from GitHub UB-Mannheim/tesseract/wiki",
                "linux": "sudo apt-get install tesseract-ocr",
                "mac": "brew install tesseract",
            }
        }

    @classmethod
    def extract_from_scanned_pdf(cls, pdf_bytes: bytes) -> DocumentExtractionResult:
        if not cls.is_tesseract_available():
            status = cls.get_ocr_status()
            return DocumentExtractionResult(
                items=[],
                extraction_method="OCR (Unavailable)",
                confidence="OCR_NOT_INSTALLED",
                warnings=[
                    status["message"],
                    "Please use a digital PDF or use the Manual Entry table to add bill items."
                ]
            )

        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            extracted_text = ""
            for page_index in range(min(len(doc), 5)):  # Process up to 5 pages
                page = doc[page_index]
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                page_text = pytesseract.image_to_string(img)
                extracted_text += page_text + "\n"

            lines = [ln.strip() for ln in extracted_text.splitlines() if ln.strip()]
            items: List[BillItemInput] = []
            item_counter = 1

            for line in lines:
                matches = list(AMOUNT_REGEX.finditer(line))
                if matches:
                    last_match = matches[-1]
                    amt_str = last_match.group(1)
                    amount = clean_amount(amt_str)
                    if amount and amount >= Decimal("10.00"):
                        desc = line[:last_match.start()].strip()
                        desc = re.sub(r'[:\-–—\.]+$', '', desc).strip()
                        if len(desc) >= 3 and not desc.lower().startswith("total"):
                            cat = normalize_category_from_description(desc)
                            items.append(
                                BillItemInput(
                                    id=f"ocr-{item_counter}",
                                    original_description=desc,
                                    category=cat,
                                    unit_price=amount,
                                    quantity=Decimal("1.00"),
                                    billed_amount=amount,
                                    requires_review=True,
                                    review_reason="OCR extracted line; please verify numbers and category."
                                )
                            )
                            item_counter += 1

            total_extracted = sum((it.billed_amount for it in items), Decimal("0.00"))
            return DocumentExtractionResult(
                items=items,
                total_extracted_amount=total_extracted,
                raw_text_length=len(extracted_text),
                extraction_method="Tesseract Optical Character Recognition (OCR)",
                confidence="MEDIUM_NEEDS_REVIEW",
                warnings=["OCR extracted data may have optical noise. Review each line item carefully before auditing."]
            )

        except Exception as e:
            return DocumentExtractionResult(
                items=[],
                extraction_method="Tesseract OCR",
                confidence="ERROR",
                warnings=[f"OCR processing encountered an error: {str(e)}. Fallback to manual entry."]
            )

