import React, { useState } from 'react';
import {
  HelpCircle,
  Code,
  Database,
  Server,
  BookOpen,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';

export const VivaDocumentation: React.FC = () => {
  const [activeDocTab, setActiveDocTab] = useState<'viva-qa' | 'architecture' | 'database' | 'algorithms'>('viva-qa');
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const vivaQuestions = [
    {
      q: 'Q1: What is the main problem your project solves, and why is pre-claim auditing important?',
      a: 'When patients are hospitalized in India, they often assume their health insurance will cover 100% of the hospital bill. However, upon discharge or claim settlement, insurers deduct significant amounts due to room-rent caps, proportionate deductions, non-payable consumables (IRDAI list), and co-payments. Our project, "Hospital Bill Auditor", provides patients with a transparent, explainable pre-claim audit of their hospital bill before submitting claims, calculating the exact estimated payable amount and potential shortfall, tracing every single deduction to specific policy clauses.'
    },
    {
      q: 'Q2: Explain the Proportionate Deduction algorithm implemented in your rule engine.',
      a: 'If a patient chooses a hospital room whose daily rate exceeds their policy room-rent limit (e.g. ₹5,000/day vs ₹3,000/day limit), insurers penalize not just the room rent, but all associated medical charges (doctor visits, surgeon fees, OT charges, nursing fees) proportionally. The mathematical formula is: Proportionate Ratio = min(1.0, Allowed Room Rent Rate / Actual Billed Room Rent Rate). In our Section 7 demo case, Ratio = ₹3,000 / ₹5,000 = 0.60 (60%). Doctor & OT charges of ₹60,000 are therefore reduced to ₹60,000 × 0.60 = ₹36,000, creating a ₹24,000 deduction.'
    },
    {
      q: 'Q3: Why did you choose Python Decimal instead of floating-point numbers (float)?',
      a: 'IEEE 754 floating-point arithmetic introduces binary representation errors in financial calculations (e.g., 0.1 + 0.2 = 0.30000000000000004). In insurance financial auditing, every single rupee and paise must balance exactly. Python\'s Decimal class provides arbitrary-precision fixed-point decimal arithmetic, allowing exact round-half-up operations and guaranteeing financial reconciliation: Total Billed == Estimated Payable + Estimated Shortfall without any fractional discrepancy.'
    },
    {
      q: 'Q4: How does your application handle PDF bill parsing and OCR?',
      a: 'For digital text PDFs, we use PyMuPDF (fitz) to extract text streams and tabular blocks locally in under 50 milliseconds using regex pattern recognition. For scanned image bills, we integrated a local Tesseract OCR pipeline via pytesseract and Pillow. If Tesseract is not installed on the host system, the backend gracefully catches the dependency, warns the user with clear installation instructions, and allows immediate manual editing or correction in the editable data table.'
    },
    {
      q: 'Q5: How is AI integrated, and what safeguards prevent hallucinations in financial figures?',
      a: 'AI integration is strictly optional and completely decoupled. We follow an architectural principle: AI assists with text normalization and category suggestions for ambiguous bill item descriptions, but AI is NEVER permitted to calculate or alter financial amounts. All financial calculations are executed by the deterministic Python Decimal Rule Engine with zero external network dependencies.'
    },
    {
      q: 'Q6: What database design and ORM did you implement?',
      a: 'We use SQLite with SQLAlchemy 2.0 ORM. The relational schema consists of: (1) `policies` table storing policy configurations, sum insured limits, and deduction rules; (2) `audits` table storing audit metadata, financial summaries, and assumptions; and (3) `audit_items` table with foreign key `audit_id` (CASCADE delete) storing normalized line items, category labels, billed amount, allowed amount, deduction amount, and deduction reason.'
    },
    {
      q: 'Q7: How do you handle non-payable items according to IRDAI guidelines?',
      a: 'The Insurance Regulatory and Development Authority of India (IRDAI) specifies a list of non-payable items, primarily consumables (gloves, PPE kits, cotton, gauze, sanitizers, thermometer, wipes) and administrative charges (registration fees, admission fees, record keeping). Our rule engine automatically classifies these via keyword heuristic normalization and deducts 100% of their billed cost from the eligible claim.'
    },
    {
      q: 'Q8: What is the sequence of policy-level deductions in your engine?',
      a: 'The sequence is strictly defined: Step 1: Item-level admissibility (Room rent cap, non-payables, associate proportionate deductions). Step 2: Deductible deduction (mandatory out-of-pocket amount subtracted from admissible expenses). Step 3: Co-payment deduction (% patient share applied to balance). Step 4: Sum Insured capping (if total eligible exceeds remaining policy sum insured, it caps at sum insured). This explicit ordering prevents double deduction ambiguities.'
    },
    {
      q: 'Q9: What happens if an item is ambiguous or unclassified?',
      a: 'The engine tags the item with category `AMBIGUOUS_UNCATEGORIZED` and sets `requires_review = True`. The overall audit status transitions from `AUDIT_CLEAN` to `AUDIT_FLAGGED_FOR_REVIEW`, and the report explicitly lists these items under "Items Requiring Review" so patients or hospital billing executives can manually clarify the charge before claim submission.'
    },
    {
      q: 'Q10: How are PDF audit reports generated?',
      a: 'The backend uses ReportLab to dynamically construct structured, multi-page vector PDF reports. The generated report includes metadata headers, formatted currency cards, itemized tables with deduction justifications, applied policy assumptions, and the required statutory disclaimer.'
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="border-b border-slate-200 pb-5">
        <h1 className="text-2xl font-bold text-slate-900">Project Viva Defense & Technical Documentation</h1>
        <p className="text-sm text-slate-500">
          Comprehensive college viva presentation guide, architectural explanations, algorithms, and database design.
        </p>

        {/* Sub-tabs */}
        <div className="flex gap-2 mt-4">
          {[
            { id: 'viva-qa', label: 'Top 10 Viva Questions & Answers', icon: HelpCircle },
            { id: 'architecture', label: 'System Architecture & Tech Stack', icon: Server },
            { id: 'algorithms', label: 'Calculation Algorithms & Formulas', icon: Code },
            { id: 'database', label: 'Database Schema & Design', icon: Database },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeDocTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveDocTab(tab.id as any)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-sm'
                    : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab 1: Viva Q&A */}
      {activeDocTab === 'viva-qa' && (
        <div className="space-y-4">
          <div className="bg-sky-50 border border-sky-200 rounded-xl p-4 text-xs text-sky-900 flex items-start gap-2">
            <BookOpen className="w-4 h-4 text-sky-600 flex-shrink-0 mt-0.5" />
            <span>
              <strong>Tip for College Viva:</strong> Review these 10 core questions before your presentation. 
              The external examiner will test your understanding of why specific technologies were chosen, 
              how the proportionate deduction formula works, and how financial accuracy is guaranteed.
            </span>
          </div>

          <div className="space-y-3">
            {vivaQuestions.map((faq, index) => {
              const isOpen = openFaq === index;
              return (
                <div
                  key={index}
                  className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden"
                >
                  <button
                    onClick={() => setOpenFaq(isOpen ? null : index)}
                    className="w-full px-6 py-4 text-left flex items-center justify-between font-bold text-sm text-slate-900 hover:bg-slate-50 transition-colors"
                  >
                    <span>{faq.q}</span>
                    {isOpen ? (
                      <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-slate-400 flex-shrink-0" />
                    )}
                  </button>
                  {isOpen && (
                    <div className="px-6 pb-5 pt-1 text-xs text-slate-600 leading-relaxed border-t border-slate-100 bg-slate-50/40">
                      {faq.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 2: Architecture */}
      {activeDocTab === 'architecture' && (
        <div className="bg-white rounded-xl p-6 sm:p-8 shadow-sm border border-slate-200/80 space-y-6 text-sm">
          <h2 className="text-lg font-bold text-slate-900">System Architecture Overview</h2>
          
          <div className="bg-slate-900 text-slate-200 p-5 rounded-xl font-mono text-xs leading-relaxed overflow-x-auto">
            <pre>{`
+------------------------------------------------------------------------+
|                          REACT 18 FRONTEND (Vite + TypeScript + Tailwind)  |
|   Dashboard | New Bill Audit Wizard | Policy Rules | Viva Walkthrough  |
+------------------------------------------------------------------------+
                                  | (REST API via fetch)
                                  v
+------------------------------------------------------------------------+
|                          FASTAPI PYTHON BACKEND                        |
|  /api/audits  |  /api/policies  |  /api/documents  |  /api/demo       |
+------------------------------------------------------------------------+
       |                         |                          |
       v                         v                          v
+-------------------+   +--------------------+   +-----------------------+
|  DOCUMENT PARSER  |   |  DETERMINISTIC     |   | REPORTLAB GENERATOR   |
|  - PyMuPDF (Text) |   |  RULE ENGINE       |   | - Dynamic Vector PDF  |
|  - Local OCR      |   |  - Python Decimal  |   | - Itemized Tables     |
|    (Tesseract)    |   |  - Proportionate   |   | - Statutory Notice    |
|  - Category Regex |   |  - Capping & Copay |   +-----------------------+
+-------------------+   +--------------------+              |
                                 |                          v
                                 v                   (Download PDF)
                        +--------------------+
                        | SQLITE RELATIONAL  |
                        | DATABASE           |
                        | - Audits           |
                        | - Audit Items      |
                        | - Policy Configs   |
                        +--------------------+
`}</pre>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 text-xs">
            <div className="space-y-2">
              <h3 className="font-bold text-slate-900 text-sm">Why FastAPI?</h3>
              <p className="text-slate-600 leading-relaxed">
                FastAPI provides high performance asynchronous request handling, automatic interactive Swagger UI documentation at <code>/docs</code>, and strong Pydantic runtime validation, ensuring type safety between Python and TypeScript.
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="font-bold text-slate-900 text-sm">Why React with Vite?</h3>
              <p className="text-slate-600 leading-relaxed">
                Vite provides sub-second hot module reloading and fast compilation. TypeScript guarantees that line items, deduction amounts, and policy parameters match backend schemas precisely, preventing runtime UI bugs.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Algorithms */}
      {activeDocTab === 'algorithms' && (
        <div className="bg-white rounded-xl p-6 sm:p-8 shadow-sm border border-slate-200/80 space-y-6 text-sm">
          <h2 className="text-lg font-bold text-slate-900">Deterministic Calculation Algorithms</h2>

          <div className="space-y-4 text-xs text-slate-600">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <h3 className="font-bold text-slate-900 text-sm">Algorithm 1: Room Rent Capping</h3>
              <p>
                <code>allowed_room_rent = min(billed_room_rent, daily_cap × length_of_stay_days)</code><br />
                <code>room_rent_deduction = billed_room_rent - allowed_room_rent</code>
              </p>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <h3 className="font-bold text-slate-900 text-sm">Algorithm 2: Proportionate Deduction Ratio</h3>
              <p>
                If actual daily room rent &gt; daily cap:<br />
                <code>proportionate_ratio = daily_cap / actual_daily_room_rent</code><br />
                For every line item in ASSOCIATE_MEDICAL (Doctor, Nursing, OT, Surgery):<br />
                <code>item_allowed = item_billed × proportionate_ratio</code><br />
                <code>item_deduction = item_billed - item_allowed</code>
              </p>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <h3 className="font-bold text-slate-900 text-sm">Algorithm 3: Policy-Level Deductions & Capping</h3>
              <p>
                <code>step_1 = sum(item_allowed)</code><br />
                <code>step_2 = max(0, step_1 - deductible_amount)</code><br />
                <code>copay_amount = step_2 × (copay_percentage / 100)</code><br />
                <code>step_3 = step_2 - copay_amount</code><br />
                <code>final_payable = min(policy_sum_insured, step_3)</code><br />
                <code>final_shortfall = total_billed - final_payable</code><br />
                <code>Reconciliation Check: total_billed == final_payable + final_shortfall</code>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Database */}
      {activeDocTab === 'database' && (
        <div className="bg-white rounded-xl p-6 sm:p-8 shadow-sm border border-slate-200/80 space-y-6 text-sm">
          <h2 className="text-lg font-bold text-slate-900">Database Schema & Relational Design</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <h3 className="font-bold text-slate-900 text-sm">Table: policies</h3>
              <ul className="list-disc list-inside text-slate-600 space-y-1">
                <li><code>id</code> (PK, Integer)</li>
                <li><code>name</code> (String, Not Null)</li>
                <li><code>sum_insured</code> (Float, Not Null)</li>
                <li><code>room_rent_limit_type</code> (String)</li>
                <li><code>room_rent_limit_amount</code> (Float)</li>
                <li><code>copay_percentage</code> (Float)</li>
                <li><code>deductible_amount</code> (Float)</li>
                <li><code>is_default</code> (Boolean)</li>
              </ul>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <h3 className="font-bold text-slate-900 text-sm">Table: audits</h3>
              <ul className="list-disc list-inside text-slate-600 space-y-1">
                <li><code>id</code> (PK, Integer)</li>
                <li><code>patient_name</code> (String)</li>
                <li><code>hospital_name</code> (String)</li>
                <li><code>policy_name</code> (String)</li>
                <li><code>total_billed</code> (Float)</li>
                <li><code>total_estimated_payable</code> (Float)</li>
                <li><code>total_estimated_shortfall</code> (Float)</li>
                <li><code>status</code> (String)</li>
                <li><code>created_at</code> (DateTime)</li>
              </ul>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <h3 className="font-bold text-slate-900 text-sm">Table: audit_items</h3>
              <ul className="list-disc list-inside text-slate-600 space-y-1">
                <li><code>id</code> (PK, Integer)</li>
                <li><code>audit_id</code> (FK -&gt; audits.id, CASCADE)</li>
                <li><code>description</code> (String)</li>
                <li><code>category</code> (String)</li>
                <li><code>billed_amount</code> (Float)</li>
                <li><code>payable_amount</code> (Float)</li>
                <li><code>deduction_amount</code> (Float)</li>
                <li><code>deduction_reason</code> (Text)</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
