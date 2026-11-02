# Comprehensive Project & College Viva Defense Guide
## Hospital Bill Auditor — System Architecture, Algorithms & Code Walkthrough

---

## 1. Directory Structure & File Manifest

| Directory / File | Type | Purpose & Responsibility |
| :--- | :--- | :--- |
| **`backend/app/main.py`** | Application Entrypoint | Initializes FastAPI, mounts CORS middleware, seeds default policies, serves static frontend files, and includes all routers. |
| **`backend/app/database.py`** | Database Configuration | Configures SQLite connection string and SQLAlchemy 2.0 ORM session factory (`SessionLocal`, `engine`, `Base`). |
| **`backend/app/engine/categories.py`** | Domain Engine | Defines the 9 standard IRDAI-aligned `BillCategory` enums, category metadata, and keyword normalization heuristics. |
| **`backend/app/engine/rules.py`** | Domain Rules | Defines `PolicyConfig` Pydantic model with strict validation (positive sum insured, 0-100% copay, non-negative amounts). |
| **`backend/app/engine/rule_engine.py`** | Core Engine | **Heart of the project.** Deterministic rule engine using Python `Decimal` to calculate room rent caps, proportionate deductions, non-payables, co-pays, deductibles, and financial reconciliation. |
| **`backend/app/models/`** | SQLAlchemy Models | Defines database tables: `PolicyModel` (`policies`), `AuditModel` (`audits`), and `AuditItemModel` (`audit_items`). |
| **`backend/app/schemas/`** | Pydantic Schemas | Data Transfer Objects (DTOs) for request validation and response serialization. |
| **`backend/app/services/extractor.py`** | Document Service | PyMuPDF-based text and table extraction parser for digital PDF bills. |
| **`backend/app/services/ocr_service.py`** | OCR Service | Local Tesseract OCR scanner for image-based/scanned bills with dependency detection and user guidance. |
| **`backend/app/services/report_generator.py`**| Report Service | ReportLab engine that builds printable, official PDF audit reports with itemized tables and disclaimers. |
| **`backend/app/services/ai_service.py`** | AI Service | Optional decoupled assistant for category suggestions with automatic fallback to local regex heuristics. |
| **`backend/app/routers/`** | REST Endpoints | Routers for `/api/audits`, `/api/policies`, `/api/documents`, `/api/demo`, and `/api/ai`. |
| **`backend/tests/`** | Test Suite | 18 automated unit and integration tests covering Section 7 demo case, rule engine edge cases, and endpoints. |
| **`frontend/src/App.tsx`** | Frontend Router | Top-level component managing active views: Dashboard, New Audit, Report, Policies, History, Viva Guide. |
| **`frontend/src/components/`** | React Components | Modular UI components: `Dashboard`, `NewAudit`, `AuditReport`, `PolicyManager`, `AuditHistory`, `DemoWalkthrough`, `VivaDocumentation`, `StatusBadge`. |
| **`frontend/src/services/api.ts`** | API Client | Typed HTTP client interfacing with backend endpoints. |
| **`samples/`** | Sample Files | Sample PDF bill generator script (`generate_sample_pdf.py`) and generated sample bill (`sample_hospital_bill.pdf`). |

---

## 2. Deterministic Insurance Rule Engine & Mathematical Algorithms

The financial engine ([`rule_engine.py`](file:///c:/Users/AJAY/OneDrive/Desktop/hospitalbileditior/backend/app/engine/rule_engine.py)) operates strictly on Python `Decimal` values quantized to 2 decimal places with `ROUND_HALF_UP`.

### Step 1: Input Validation & Sanitization
Every line item is checked:
- `billed_amount >= 0` (negative amounts raise a validation error).
- `quantity >= 0` and `unit_price >= 0`.
- At least one line item is required.

### Step 2: Room Rent Evaluation & Daily Cap
1. The engine checks if the policy specifies a room rent limit:
   - `FIXED_AMOUNT`: `daily_cap = policy.room_rent_limit_amount`
   - `PERCENTAGE_OF_SI`: `daily_cap = policy.sum_insured * (room_rent_limit_percentage / 100)`
   - `NO_LIMIT`: `daily_cap = infinity`
2. Effective length of stay ($D$) is extracted from the bill item or defaults to `policy.length_of_stay_days`.
3. Allowed Room Rent:
   $$\text{Allowed Room Rent} = \min(\text{Billed Room Rent}, \text{daily\_cap} \times D)$$
4. Room Rent Deduction:
   $$\text{Deduction}_{\text{room}} = \text{Billed Room Rent} - \text{Allowed Room Rent}$$
5. Actual Daily Billed Rate:
   $$\text{Actual Daily Rate} = \frac{\text{Billed Room Rent}}{D}$$

### Step 3: Proportionate Deduction Calculation
When actual room rent per day exceeds the daily limit, health insurers apply a proportionate penalty on associate medical charges (doctors, surgeons, anesthetists, OT fees, nursing fees):
$$\text{Proportionate Ratio} = \min\left(1.0, \frac{\text{daily\_cap}}{\text{Actual Daily Rate}}\right)$$

For each line item categorized under `ASSOCIATE_MEDICAL`:
$$\text{Allowed Amount} = \text{Billed Amount} \times \text{Proportionate Ratio}$$
$$\text{Deduction} = \text{Billed Amount} - \text{Allowed Amount}$$

**Section 7 Demonstration Proof**:
- Daily Cap = ₹3,000 / day
- Actual Rate = ₹25,000 / 5 days = ₹5,000 / day
- Ratio = $3000 / 5000 = 0.60$ (60%)
- Doctor & OT charges = ₹60,000
- Allowed = $60,000 \times 0.60 = \mathbf{₹36,000}$
- Deduction = $60,000 - 36,000 = \mathbf{₹24,000}$

### Step 4: Non-Payable Charges Exclusion
Items classified as `NON_PAYABLE_CONSUMABLE` or `NON_PAYABLE_ADMIN` (gloves, PPE kits, masks, admission fees, registration charges) are 100% excluded:
$$\text{Allowed Amount} = 0.00$$
$$\text{Deduction} = \text{Billed Amount}$$

### Step 5: Fully Eligible Items
Items in `PHARMACY`, `DIAGNOSTICS`, `SURGERY_IMPLANT`, and `OTHER_MEDICAL` are fully payable:
$$\text{Allowed Amount} = \text{Billed Amount}$$
$$\text{Deduction} = 0.00$$

### Step 6: Policy-Level Deductions & Sum Insured Capping
1. **Subtotal**: $\text{Eligible Subtotal} = \sum \text{Allowed Amount of all items}$
2. **Deductible**:
   $$\text{Deductible Applied} = \min(\text{policy.deductible\_amount}, \text{Eligible Subtotal})$$
   $$\text{Balance} = \text{Eligible Subtotal} - \text{Deductible Applied}$$
3. **Co-Payment**:
   $$\text{CoPay Applied} = \text{Balance} \times \left(\frac{\text{policy.copay\_percentage}}{100}\right)$$
   $$\text{Payable Pre-Cap} = \text{Balance} - \text{CoPay Applied}$$
4. **Sum Insured Capping**:
   $$\text{Total Estimated Payable} = \min(\text{policy.sum\_insured}, \text{Payable Pre-Cap})$$
   $$\text{Total Estimated Shortfall} = \text{Total Billed} - \text{Total Estimated Payable}$$

### Step 7: Audit Reconciliation
The engine enforces mathematical equality:
$$\text{Total Billed} \equiv \text{Total Estimated Payable} + \text{Total Estimated Shortfall}$$

---

## 3. Database Design & Entity-Relationship Details

### Table: `policies`
- `id` (INTEGER, Primary Key, Auto Increment)
- `name` (VARCHAR(255), Not Null)
- `description` (TEXT)
- `sum_insured` (FLOAT, Default: 500,000.0)
- `room_rent_limit_type` (VARCHAR(50), e.g. "FIXED_AMOUNT")
- `room_rent_limit_amount` (FLOAT, Default: 3,000.0)
- `room_rent_limit_percentage` (FLOAT, Default: 1.0)
- `apply_proportionate_deduction` (BOOLEAN, Default: True)
- `copay_percentage` (FLOAT, Default: 0.0)
- `deductible_amount` (FLOAT, Default: 0.0)
- `non_payable_categories` (TEXT, e.g. "NON_PAYABLE_CONSUMABLE,NON_PAYABLE_ADMIN")
- `length_of_stay_days` (INTEGER, Default: 5)
- `is_default` (BOOLEAN)
- `created_at` / `updated_at` (DATETIME, UTC)

### Table: `audits`
- `id` (INTEGER, Primary Key, Auto Increment)
- `patient_name` (VARCHAR(255))
- `hospital_name` (VARCHAR(255))
- `bill_number` (VARCHAR(100))
- `policy_name` (VARCHAR(255))
- `policy_id` (INTEGER, Foreign Key -> `policies.id`, ON DELETE SET NULL)
- `total_billed` (FLOAT)
- `total_allowed` (FLOAT)
- `item_level_deductions` (FLOAT)
- `deductible_applied` (FLOAT)
- `copay_applied` (FLOAT)
- `copay_percentage` (FLOAT)
- `sum_insured_excess_applied` (FLOAT)
- `total_estimated_payable` (FLOAT)
- `total_estimated_shortfall` (FLOAT)
- `status` (VARCHAR(50), "AUDIT_CLEAN" or "AUDIT_FLAGGED_FOR_REVIEW")
- `length_of_stay_days` (INTEGER)
- `proportionate_ratio_applied` (FLOAT)
- `assumptions_json` (TEXT)
- `flags_json` (TEXT)
- `source_document_name` (VARCHAR(255))
- `created_at` (DATETIME, UTC)

### Table: `audit_items`
- `id` (INTEGER, Primary Key, Auto Increment)
- `audit_id` (INTEGER, Foreign Key -> `audits.id`, ON DELETE CASCADE)
- `description` (VARCHAR(255), Not Null)
- `category` (VARCHAR(50), Not Null)
- `category_label` (VARCHAR(100))
- `billed_amount` (FLOAT)
- `allowed_amount` (FLOAT)
- `deduction_amount` (FLOAT)
- `payable_amount` (FLOAT)
- `deduction_reason` (TEXT)
- `is_non_payable` (BOOLEAN)
- `is_proportionate_deduction` (BOOLEAN)
- `is_room_rent_excess` (BOOLEAN)
- `requires_review` (BOOLEAN)
- `review_reason` (TEXT)

---

## 4. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check & service metadata |
| `GET` | `/api/policies` | List all saved insurance policies (seeds defaults if empty) |
| `POST` | `/api/policies` | Create a new custom policy |
| `GET` | `/api/policies/{id}` | Get specific policy details |
| `DELETE`| `/api/policies/{id}` | Delete a custom policy |
| `POST` | `/api/documents/upload` | Upload PDF/image bill for automatic text & table parsing |
| `GET` | `/api/documents/ocr-status` | Check local Tesseract OCR availability and instructions |
| `POST` | `/api/audits/preview` | In-memory calculation preview without database persistence |
| `POST` | `/api/audits` | Calculate and persist audit & line items to SQLite |
| `GET` | `/api/audits` | List all past audits (ordered newest first) |
| `GET` | `/api/audits/{id}` | Get complete audit record with all line items and rules |
| `DELETE`| `/api/audits/{id}` | Delete an audit record (cascades to items) |
| `GET` | `/api/audits/{id}/report-pdf` | Download official vector PDF audit report |
| `GET` | `/api/audits/dashboard/stats` | Aggregated dashboard metrics computed from real database data |
| `GET` | `/api/demo/data` | Returns raw sample data for the Section 7 viva demo case |
| `POST` | `/api/demo/run` | Executes the Section 7 demonstration case and saves it to DB |
| `GET` | `/api/ai/status` | Returns optional AI configuration and provider status |

---

## 5. Security & Privacy Safeguards

1. **File Upload Restrictions**: Maximum upload size enforced at 15 MB. Extension white-listing permits only `.pdf`, `.png`, `.jpg`, `.jpeg`.
2. **Deterministic Fallback**: If an external LLM API key is invalid or unavailable, the application functions with zero degradation via local heuristics.
3. **No Secret Leaks**: API keys are read strictly from backend environment variables (`GEMINI_API_KEY`, `OPENAI_API_KEY`) and are never exposed to client-side frontend code.
4. **Data Isolation**: All storage is local in `hospital_auditor.db` without unconsented external data sharing.

---

## 6. College Viva Q&A — Top 10 Technical Questions & Answers

### Q1: Why did you choose Python for the backend and React for the frontend?
**Answer**: Python was chosen because it has the most robust ecosystem for financial calculations (`Decimal`), local PDF parsing (`PyMuPDF`), OCR (`pytesseract`), and PDF generation (`ReportLab`). FastAPI provides native Pydantic type validation and automatic Swagger documentation. React with Vite and TypeScript was chosen for the frontend to create a responsive, single-page application where doctors, patients, or auditors can interactively edit line items and receive instant recalculation previews.

### Q2: What is the Proportionate Deduction rule in Indian health insurance?
**Answer**: Most health insurance policies cap eligible room rent at a fixed amount (e.g. ₹3,000/day) or 1% of Sum Insured. If a patient opts for a higher category room (e.g. ₹5,000/day), insurers do not just deduct the ₹2,000/day room rent difference; they apply a proportionate deduction across all associated medical services (consultant charges, surgeon fees, OT charges, nursing charges). The allowed percentage is calculated as `Allowed Room Rent / Actual Billed Room Rent`. In our Section 7 viva demo, this ratio is `₹3,000 / ₹5,000 = 60%`.

### Q3: Why did you not use Python's standard `float` for monetary amounts?
**Answer**: Floating-point numbers implement IEEE-754 binary representation, which cannot precisely represent many decimal fractions (e.g., `0.1 + 0.2 = 0.30000000000000004`). In insurance claims, financial reconciliation requires exact arithmetic. Python's `Decimal` module allows arbitrary-precision decimal arithmetic with strict `ROUND_HALF_UP` quantization, ensuring that `Total Billed == Estimated Payable + Estimated Shortfall` to the exact paise.

### Q4: How does your application extract items from hospital bill PDFs?
**Answer**: We use PyMuPDF (`fitz`), which parses the PDF's text layer and table structures locally in milliseconds. The text parser identifies item descriptions, quantities, rates, and amounts using sequential tabular pattern matching and regex heuristics. Descriptions are then automatically categorized into standard IRDAI categories (Room Rent, Associate Medical, Pharmacy, Diagnostics, Consumables) using keyword classifiers.

### Q5: What happens if someone uploads a scanned bill without a text layer?
**Answer**: The system detects that the text layer is empty (`confidence: SCANNED_IMAGE_DETECTED`). It checks whether local Tesseract OCR is available. If available, it converts the PDF pages to high-DPI images and extracts text using `pytesseract`. If Tesseract is not installed on the host system, the application does not crash; instead, it informs the user and allows them to enter or correct items in the editable table.

### Q6: Can AI alter the financial calculation results?
**Answer**: **No.** In our architecture, AI integration is strictly optional, decoupled, and sandboxed. AI is only permitted to suggest candidate categories for ambiguous descriptions or generate plain-English summaries. All financial totals and deductions are executed exclusively by the deterministic Python Decimal Rule Engine.

### Q7: What are Non-Payable items in health insurance?
**Answer**: Under IRDAI guidelines, items considered non-medical consumables (gloves, PPE kits, masks, cotton, sanitizers, thermometer, wipes) and administrative charges (registration fees, admission fees, medical record fees) are non-payable by insurers. Our rule engine identifies these items and assigns them a 100% deduction.

### Q8: What database schema did you design, and why SQLite?
**Answer**: We designed a 3-table relational schema: `policies`, `audits`, and `audit_items` with a foreign key relationship (`audit_id` with `CASCADE` delete). SQLite was selected because it is a lightweight, zero-configuration embedded relational database that requires no external database server to run, making it ideal for a reproducible college project demonstration while supporting full SQL querying.

### Q9: How are the downloadable PDF reports generated?
**Answer**: We use ReportLab to dynamically construct multi-page vector PDF documents. The generator formats patient metadata, high-level financial summary cards, itemized tables with deduction justifications, applied policy assumptions, and mandatory statutory notices.

### Q10: How do you verify the correctness of the financial calculations?
**Answer**: We created an automated test suite with 18 tests executed via `pytest`. The test suite includes unit tests for room rent limits, proportionate deductions, non-payable consumables, co-pays, deductibles, sum insured capping, input validation (rejecting negative numbers and invalid percentages), PDF extraction, and the Section 7 demonstration case.

