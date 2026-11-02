import React, { useState, useEffect } from 'react';
import {
  Upload,
  FileText,
  Plus,
  Trash2,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  Shield,
  ArrowRight,
  Info,
} from 'lucide-react';
import {
  BillCategory,
  BillItemInput,
  CATEGORY_INFO,
  PolicyConfig,
  AuditResult,
  OCRStatusResponse,
} from '../types';
import { api } from '../services/api';
import { formatINR } from '../utils/formatters';

interface NewAuditProps {
  onAuditSaved: (auditId: number) => void;
  onCancel: () => void;
}

export const NewAudit: React.FC<NewAuditProps> = ({ onAuditSaved, onCancel }) => {
  // Metadata state
  const [patientName, setPatientName] = useState('Ramesh Kumar');
  const [hospitalName, setHospitalName] = useState('Apollo Multispeciality Hospital');
  const [billNumber, setBillNumber] = useState('INV-2026-001');

  // Policy state
  const [policies, setPolicies] = useState<PolicyConfig[]>([]);
  const [selectedPolicyId, setSelectedPolicyId] = useState<number | undefined>(undefined);

  // Bill items state
  const [items, setItems] = useState<BillItemInput[]>([
    {
      id: 'item-1',
      original_description: 'Room rent (Deluxe Room - 5 Days)',
      category: 'ROOM_RENT',
      unit_price: 5000,
      quantity: 5,
      billed_amount: 25000,
      days_stay: 5,
    },
    {
      id: 'item-2',
      original_description: 'Doctor, nursing, and OT charges',
      category: 'ASSOCIATE_MEDICAL',
      unit_price: 60000,
      quantity: 1,
      billed_amount: 60000,
    },
    {
      id: 'item-3',
      original_description: 'Pharmacy medications and IV fluids',
      category: 'PHARMACY',
      unit_price: 30000,
      quantity: 1,
      billed_amount: 30000,
    },
    {
      id: 'item-4',
      original_description: 'Gloves, masks, and administrative fees',
      category: 'NON_PAYABLE_CONSUMABLE',
      unit_price: 8000,
      quantity: 1,
      billed_amount: 8000,
    },
    {
      id: 'item-5',
      original_description: 'Diagnostics and laboratory investigations',
      category: 'DIAGNOSTICS',
      unit_price: 27000,
      quantity: 1,
      billed_amount: 27000,
    },
  ]);

  // UI state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadWarning, setUploadWarning] = useState<string | null>(null);
  const [ocrStatus, setOcrStatus] = useState<OCRStatusResponse | null>(null);
  const [, setIsCalculating] = useState(false);
  const [previewResult, setPreviewResult] = useState<AuditResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetch policies on mount
  useEffect(() => {
    api.getPolicies().then((pols) => {
      setPolicies(pols);
      if (pols.length > 0) {
        const def = pols.find((p) => p.is_default) || pols[0];
        setSelectedPolicyId(def.id);
      }
    });
    api.getOCRStatus().then(setOcrStatus).catch(() => {});
  }, []);

  // Recalculate preview whenever items or policy changes
  useEffect(() => {
    if (items.length > 0 && selectedPolicyId) {
      calculatePreview();
    }
  }, [items, selectedPolicyId]);

  const calculatePreview = async () => {
    try {
      setIsCalculating(true);
      setError(null);
      const res = await api.previewAudit({
        items,
        policy_id: selectedPolicyId,
        patient_name: patientName,
        hospital_name: hospitalName,
        bill_number: billNumber,
      });
      setPreviewResult(res);
    } catch (err: any) {
      setError(err.message || 'Error calculating preview');
    } finally {
      setIsCalculating(false);
    }
  };

  // Handle PDF file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      setUploadWarning(null);
      setError(null);
      const data = await api.uploadDocument(file);

      if (data.metadata) {
        if (data.metadata.patient_name) setPatientName(data.metadata.patient_name);
        if (data.metadata.hospital_name) setHospitalName(data.metadata.hospital_name);
        if (data.metadata.bill_number) setBillNumber(data.metadata.bill_number);
        if (data.metadata.warnings && data.metadata.warnings.length > 0) {
          setUploadWarning(data.metadata.warnings.join(' '));
        }
      }

      if (data.items && data.items.length > 0) {
        setItems(data.items);
      } else {
        setUploadWarning(
          'Document uploaded, but no line items were detected automatically. Please add items manually below.'
        );
      }
    } catch (err: any) {
      setError(err.message || 'Failed to extract file text');
    } finally {
      setIsUploading(false);
    }
  };

  // Load Section 7 demo items
  const loadDemoItems = async () => {
    try {
      const demoData = await api.getDemoData();
      setPatientName(demoData.bill.patient_name);
      setHospitalName(demoData.bill.hospital_name);
      setBillNumber(demoData.bill.bill_number);
      setItems(demoData.bill.items);
    } catch {
      // fallback
    }
  };

  // Add Item Row
  const addItem = () => {
    const newItem: BillItemInput = {
      id: `item-${Date.now()}`,
      original_description: 'Medical charge',
      category: 'OTHER_MEDICAL',
      unit_price: 1000,
      quantity: 1,
      billed_amount: 1000,
    };
    setItems([...items, newItem]);
  };

  // Update Item Row
  const updateItem = (index: number, updates: Partial<BillItemInput>) => {
    const next = [...items];
    const current = { ...next[index], ...updates };

    // Automatically synchronize billed_amount if rate/qty changes
    if ('unit_price' in updates || 'quantity' in updates) {
      current.billed_amount = current.unit_price * current.quantity;
    }

    next[index] = current;
    setItems(next);
  };

  // Delete Item Row
  const deleteItem = (index: number) => {
    if (items.length <= 1) {
      setError('A bill must contain at least one line item.');
      return;
    }
    setItems(items.filter((_, i) => i !== index));
  };

  // Submit and save audit
  const handleSaveAudit = async () => {
    try {
      setError(null);
      const saved = await api.saveAudit({
        items,
        policy_id: selectedPolicyId,
        patient_name: patientName,
        hospital_name: hospitalName,
        bill_number: billNumber,
      });
      onAuditSaved(saved.id);
    } catch (err: any) {
      setError(err.message || 'Failed to save audit record');
    }
  };

  const totalBilled = items.reduce((sum, it) => sum + (Number(it.billed_amount) || 0), 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">New Hospital Bill Audit</h1>
          <p className="text-sm text-slate-500">
            Step 1: Upload or enter bill items &nbsp;•&nbsp; Step 2: Select policy &nbsp;•&nbsp; Step 3: Audit calculation
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadDemoItems}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-lg transition-colors"
          >
            <Sparkles className="w-4 h-4 text-emerald-600" />
            <span>Load ₹1,50,000 Demo Bill</span>
          </button>
          <button
            onClick={onCancel}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 bg-white border border-slate-300 rounded-lg"
          >
            Cancel
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 text-red-600" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-xs font-bold underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Bill Upload & Metadata Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Zone */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Upload className="w-4 h-4 text-sky-600" />
              Upload Digital or Scanned Bill
            </h3>
            <span className="text-[11px] text-slate-400">PDF, PNG, JPG (≤15MB)</span>
          </div>

          <label className="border-2 border-dashed border-slate-300 hover:border-sky-500 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer bg-slate-50 hover:bg-sky-50/40 transition-colors">
            <FileText className="w-8 h-8 text-slate-400 mb-2" />
            <span className="text-xs font-semibold text-slate-700">
              {isUploading ? 'Extracting text layer...' : 'Click to select bill file'}
            </span>
            <span className="text-[11px] text-slate-400 mt-1">
              PyMuPDF local extraction & OCR fallback
            </span>
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              className="hidden"
              onChange={handleFileUpload}
              disabled={isUploading}
            />
          </label>

          {uploadWarning && (
            <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-800 flex items-start gap-2">
              <Info className="w-4 h-4 flex-shrink-0 text-amber-600 mt-0.5" />
              <span>{uploadWarning}</span>
            </div>
          )}

          {ocrStatus && (
            <div className="text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="font-semibold text-slate-700">Local OCR Engine: </span>
              {ocrStatus.available ? (
                <span className="text-emerald-600 font-medium">Tesseract Active</span>
              ) : (
                <span className="text-slate-500">Not detected (Text PDF & Manual Mode Active)</span>
              )}
            </div>
          )}
        </div>

        {/* Bill Metadata */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80 space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-4 h-4 text-indigo-600" />
            Hospital & Patient Information
          </h3>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Patient Name
              </label>
              <input
                type="text"
                value={patientName}
                onChange={(e) => setPatientName(e.target.value)}
                className="w-full text-sm border border-slate-300 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Hospital / Provider Name
              </label>
              <input
                type="text"
                value={hospitalName}
                onChange={(e) => setHospitalName(e.target.value)}
                className="w-full text-sm border border-slate-300 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Bill / IPD Invoice Number
              </label>
              <input
                type="text"
                value={billNumber}
                onChange={(e) => setBillNumber(e.target.value)}
                className="w-full text-sm border border-slate-300 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Policy Selection */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80 space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-600" />
            Insurance Policy Configuration
          </h3>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Select Applicable Policy
              </label>
              <select
                value={selectedPolicyId || ''}
                onChange={(e) => setSelectedPolicyId(Number(e.target.value))}
                className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-sky-500 focus:outline-none"
              >
                {policies.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} (SI: {formatINR(p.sum_insured)})
                  </option>
                ))}
              </select>
            </div>

            {selectedPolicyId && (
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs text-slate-600 space-y-1">
                {(() => {
                  const p = policies.find((pol) => pol.id === selectedPolicyId);
                  if (!p) return null;
                  return (
                    <>
                      <div>
                        <b>Room Rent Limit:</b>{' '}
                        {p.room_rent_limit_type === 'FIXED_AMOUNT'
                          ? `₹${p.room_rent_limit_amount}/day`
                          : p.room_rent_limit_type === 'PERCENTAGE_OF_SI'
                          ? `${p.room_rent_limit_percentage}% of SI/day`
                          : 'No Limit'}
                      </div>
                      <div>
                        <b>Proportionate Deduction:</b>{' '}
                        {p.apply_proportionate_deduction ? 'Enabled' : 'Disabled'}
                      </div>
                      <div>
                        <b>Co-Pay:</b> {p.copay_percentage}% &nbsp;|&nbsp; <b>Deductible:</b> ₹{p.deductible_amount}
                      </div>
                    </>
                  );
                })()}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Editable Line Items Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200/80 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Bill Line Items & Categorization
            </h2>
            <p className="text-xs text-slate-500">
              Verify, edit, or categorize each charge. Negative or invalid monetary values are strictly prevented.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-500">
              Total Billed: <span className="text-slate-900 text-sm font-bold">{formatINR(totalBilled)}</span>
            </span>
            <button
              onClick={addItem}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition-colors shadow-sm"
            >
              <Plus className="w-4 h-4" />
              Add Item
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 text-xs uppercase font-semibold">
              <tr>
                <th className="px-4 py-3 w-12 text-center">#</th>
                <th className="px-4 py-3">Description</th>
                <th className="px-4 py-3 w-64">Category</th>
                <th className="px-4 py-3 w-28 text-right">Rate (₹)</th>
                <th className="px-4 py-3 w-24 text-right">Qty</th>
                <th className="px-4 py-3 w-32 text-right">Amount (₹)</th>
                <th className="px-4 py-3 w-16 text-center">Del</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((item, idx) => {
                const catMeta = CATEGORY_INFO[item.category] || CATEGORY_INFO['AMBIGUOUS_UNCATEGORIZED'];
                return (
                  <tr key={item.id || idx} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3 text-center text-xs font-medium text-slate-400">
                      {idx + 1}
                    </td>
                    <td className="px-4 py-3">
                      <input
                        type="text"
                        value={item.original_description}
                        onChange={(e) => updateItem(idx, { original_description: e.target.value })}
                        className="w-full text-sm font-medium text-slate-800 bg-transparent border-b border-transparent hover:border-slate-300 focus:border-sky-500 focus:outline-none px-1 py-0.5"
                      />
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={item.category}
                        onChange={(e) => updateItem(idx, { category: e.target.value as BillCategory })}
                        className={`w-full text-xs font-semibold px-2.5 py-1.5 rounded-lg border focus:ring-2 focus:ring-sky-500 focus:outline-none ${catMeta.badgeColor}`}
                      >
                        {Object.entries(CATEGORY_INFO).map(([key, info]) => (
                          <option key={key} value={key} className="bg-white text-slate-900 font-normal">
                            {info.label}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <input
                        type="number"
                        min="0"
                        step="any"
                        value={item.unit_price}
                        onChange={(e) => updateItem(idx, { unit_price: Math.max(0, parseFloat(e.target.value) || 0) })}
                        className="w-full text-right text-sm border-b border-transparent hover:border-slate-300 focus:border-sky-500 focus:outline-none px-1 py-0.5"
                      />
                    </td>
                    <td className="px-4 py-3 text-right">
                      <input
                        type="number"
                        min="0.01"
                        step="any"
                        value={item.quantity}
                        onChange={(e) => updateItem(idx, { quantity: Math.max(0.01, parseFloat(e.target.value) || 1) })}
                        className="w-full text-right text-sm border-b border-transparent hover:border-slate-300 focus:border-sky-500 focus:outline-none px-1 py-0.5"
                      />
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-slate-900">
                      <input
                        type="number"
                        min="0"
                        step="any"
                        value={item.billed_amount}
                        onChange={(e) => updateItem(idx, { billed_amount: Math.max(0, parseFloat(e.target.value) || 0) })}
                        className="w-full text-right text-sm font-bold text-slate-900 border-b border-transparent hover:border-slate-300 focus:border-sky-500 focus:outline-none px-1 py-0.5"
                      />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => deleteItem(idx)}
                        className="text-slate-400 hover:text-red-600 transition-colors p-1"
                        title="Remove line item"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Live Pre-Claim Calculation Preview */}
      {previewResult && (
        <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-2xl p-6 sm:p-8 shadow-xl border border-slate-800 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-500/20 text-sky-300 mb-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Deterministic Pre-Claim Estimate Preview
              </div>
              <h3 className="text-xl font-bold">Calculation Audit Summary</h3>
            </div>
            <button
              onClick={handleSaveAudit}
              className="flex items-center gap-2 px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl shadow-lg shadow-emerald-500/25 transition-all hover:scale-[1.02]"
            >
              <span>Save & View Full Audit Report</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="bg-slate-800/80 p-5 rounded-xl border border-slate-700">
              <span className="text-xs uppercase font-semibold text-slate-400">Total Billed</span>
              <div className="text-2xl font-bold mt-1 text-white">
                {formatINR(previewResult.summary.total_billed)}
              </div>
              <div className="text-xs text-slate-400 mt-1">Gross bill charges</div>
            </div>

            <div className="bg-slate-800/80 p-5 rounded-xl border border-emerald-500/30">
              <span className="text-xs uppercase font-semibold text-emerald-400">Estimated Payable</span>
              <div className="text-2xl font-bold mt-1 text-emerald-400">
                {formatINR(previewResult.summary.total_estimated_payable)}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Admissible insurer settlement estimate
              </div>
            </div>

            <div className="bg-slate-800/80 p-5 rounded-xl border border-rose-500/30">
              <span className="text-xs uppercase font-semibold text-rose-400">Estimated Shortfall</span>
              <div className="text-2xl font-bold mt-1 text-rose-400">
                {formatINR(previewResult.summary.total_estimated_shortfall)}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Out-of-pocket patient responsibility
              </div>
            </div>
          </div>

          {/* Quick deductions summary pills */}
          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/60 text-xs text-slate-300 space-y-2">
            <div className="font-semibold text-white">Key Audit Deductions Applied:</div>
            <div className="flex flex-wrap gap-2">
              {previewResult.summary.item_level_deductions > 0 && (
                <span className="px-2.5 py-1 rounded-md bg-rose-950/60 text-rose-300 border border-rose-800/60">
                  Item Deductions: -{formatINR(previewResult.summary.item_level_deductions)}
                </span>
              )}
              {previewResult.summary.copay_applied > 0 && (
                <span className="px-2.5 py-1 rounded-md bg-amber-950/60 text-amber-300 border border-amber-800/60">
                  Co-Pay ({previewResult.summary.copay_percentage}%): -{formatINR(previewResult.summary.copay_applied)}
                </span>
              )}
              {previewResult.summary.deductible_applied > 0 && (
                <span className="px-2.5 py-1 rounded-md bg-indigo-950/60 text-indigo-300 border border-indigo-800/60">
                  Deductible: -{formatINR(previewResult.summary.deductible_applied)}
                </span>
              )}
              {previewResult.summary.reconciliation_verified && (
                <span className="px-2.5 py-1 rounded-md bg-emerald-950/60 text-emerald-300 border border-emerald-800/60">
                  ✓ Reconciliation Verified: Billed = Payable + Shortfall
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
