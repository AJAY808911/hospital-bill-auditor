"""
Tests for PDF Extraction Service using sample hospital bill.
"""
import os
from decimal import Decimal
from app.services.extractor import PDFExtractorService
from app.engine.categories import BillCategory

def test_extract_sample_hospital_bill():
    pdf_path = "samples/sample_hospital_bill.pdf"
    assert os.path.exists(pdf_path), "Sample PDF should exist"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    result = PDFExtractorService.extract_from_bytes(pdf_bytes, "sample_hospital_bill.pdf")
    
    assert result.confidence in ["HIGH", "MEDIUM"]
    assert len(result.items) >= 4  # Should extract the line items
    assert result.total_extracted_amount > Decimal("100000.00")

    # Verify hospital name or patient extraction
    assert "Apollo" in (result.hospital_name or "") or result.patient_name is not None

