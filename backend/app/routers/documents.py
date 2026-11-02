"""
Document Processing Router - Upload and extract text/tables from PDF and images.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.extractor import PDFExtractorService
from app.services.ocr_service import OCRService

router = APIRouter(prefix="/api/documents", tags=["Documents"])

MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB limit

@router.get("/ocr-status")
def get_ocr_status():
    """Returns local OCR availability and installation guidance."""
    return OCRService.get_ocr_status()

@router.post("/upload")
async def upload_and_extract_bill(file: UploadFile = File(...)):
    """
    Accepts a PDF or image bill, validates type & size, and extracts line items.
    """
    # 1. Validate file extension
    filename = file.filename or "unknown_bill"
    extension = filename.split(".")[-1].lower() if "." in filename else ""
    if extension not in ["pdf", "png", "jpg", "jpeg"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{extension}'. Please upload a PDF or image (PNG/JPG)."
        )

    # 2. Read and validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size limit of 15MB (uploaded size: {len(contents) / (1024*1024):.2f}MB)."
        )

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 3. Extraction
    if extension == "pdf":
        result = PDFExtractorService.extract_from_bytes(contents, filename)
        # If no text found (scanned PDF), try OCR
        if result.confidence == "SCANNED_IMAGE_DETECTED":
            ocr_result = OCRService.extract_from_scanned_pdf(contents)
            return ocr_result.to_dict()
        return result.to_dict()
    else:
        # Direct image uploaded
        # Let OCR service handle image bytes if tesseract is available
        return {
            "items": [],
            "metadata": {
                "hospital_name": "Image Document",
                "patient_name": "Patient",
                "total_extracted_amount": 0.0,
                "extraction_method": "Image OCR Check",
                "confidence": "IMAGE_REQUIRES_OCR",
                "warnings": [
                    "Direct image uploaded. " + OCRService.get_ocr_status()["message"],
                    "Please verify items or enter them in the editable bill table."
                ]
            }
        }

