import React, { useEffect, useState } from 'react';
import {
  FileDown,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  Building,
  User,
  Calendar,
  Layers,
} from 'lucide-react';
import { SavedAuditResponse, CATEGORY_INFO, BillCategory } from '../types';
import { api } from '../services/api';
import { formatINR, formatPercent, formatDate } from '../utils/formatters';
import { StatusBadge } from './StatusBadge';

interface AuditReportProps {
  auditId: number;
  onBack: () => void;
}

export const AuditReport: React.FC<AuditReportProps> = ({ auditId, onBack }) => {
  const [audit, setAudit] = useState<SavedAuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .getAuditById(auditId)
      .then((data) => setAudit(data))
      .catch((err) => setError(err.message || 'Failed to load audit record'))
      .finally(() => setLoading(false));
  }, [auditId]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600 mb-4" />
        <p className="text-slate-500 text-sm">Generating comprehensive audit report...</p>
      </div>
    );
  }

  if (error || !audit) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-200 text-sm">
          {error || 'Audit not found'}
        </div>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  const coverageRatio =
    audit.total_billed > 0 ? (audit.total_estimated_payable / audit.total_billed) * 100 : 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors"
            title="Back"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">Pre-Claim Audit Report</h1>
              <StatusBadge status={audit.status} />
            </div>
            <p className="text-xs text-slate-500">
              Audit Ref: AUD-{audit.id} &nbsp;•&nbsp; Generated: {formatDate(audit.created_at)}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={api.getAuditPdfUrl(audit.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs bg-sky-600 hover:bg-sky-500 text-white shadow-md shadow-sky-600/20 transition-all hover:scale-[1.02]"
          >
            <FileDown className="w-4 h-4" />
            <span>Download PDF Report</span>
          </a>
        </div>
      </div>

      {/* Audit Metadata Card */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80 grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
        <div className="flex items-start gap-3">
          <User className="w-4 h-4 text-sky-600 mt-0.5" />
          <div>
            <span className="text-xs text-slate-400 block font-medium">Patient Name</span>
            <span className="font-semibold text-slate-800">{audit.patient_name || 'Patient'}</span>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Building className="w-4 h-4 text-indigo-600 mt-0.5" />
          <div>
            <span className="text-xs text-slate-400 block font-medium">Hospital Provider</span>
            <span className="font-semibold text-slate-800">{audit.hospital_name || 'Hospital'}</span>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <ShieldCheck className="w-4 h-4 text-emerald-600 mt-0.5" />
          <div>
            <span className="text-xs text-slate-400 block font-medium">Policy Applied</span>
            <span className="font-semibold text-slate-800">{audit.policy_name}</span>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Calendar className="w-4 h-4 text-cyan-600 mt-0.5" />
          <div>
            <span className="text-xs text-slate-400 block font-medium">Length of Stay</span>
            <span className="font-semibold text-slate-800">{audit.length_of_stay_days} Days</span>
          </div>
        </div>
      </div>

      {/* Summary Financial Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80">
          <span className="text-xs uppercase font-bold text-slate-500 tracking-wider">
            Total Billed Amount
          </span>
          <div className="text-2xl font-black mt-2 text-slate-900">
            {formatINR(audit.total_billed)}
          </div>
          <p className="text-xs text-slate-500 mt-1">Gross medical charges submitted</p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-emerald-200 bg-emerald-50/20">
          <span className="text-xs uppercase font-bold text-emerald-700 tracking-wider">
            Estimated Payable
          </span>
          <div className="text-2xl font-black mt-2 text-emerald-600">
            {formatINR(audit.total_estimated_payable)}
          </div>
          <p className="text-xs text-emerald-700/80 mt-1">
            Eligible insurance claim payout
          </p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-rose-200 bg-rose-50/20">
          <span className="text-xs uppercase font-bold text-rose-700 tracking-wider">
            Potential Shortfall
          </span>
          <div className="text-2xl font-black mt-2 text-rose-600">
            {formatINR(audit.total_estimated_shortfall)}
          </div>
          <p className="text-xs text-rose-700/80 mt-1">Patient out-of-pocket share</p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80">
          <span className="text-xs uppercase font-bold text-sky-700 tracking-wider">
            Est. Coverage Ratio
          </span>
          <div className="text-2xl font-black mt-2 text-sky-600">
            {formatPercent(coverageRatio)}
          </div>
          <p className="text-xs text-slate-500 mt-1">Share of bill covered by policy</p>
        </div>
      </div>

      {/* Line Items Audit Breakdown Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200/80 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/60">
          <h2 className="text-base font-bold text-slate-900">
            Itemized Audit Breakdown & Deduction Reasoning
          </h2>
          <p className="text-xs text-slate-500">
            Deterministic rule application per line item. Every adjustment is traceable to specific policy clauses.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 text-xs uppercase font-semibold">
              <tr>
                <th className="px-4 py-3 w-12 text-center">#</th>
                <th className="px-4 py-3">Description</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3 text-right">Billed (₹)</th>
                <th className="px-4 py-3 text-right">Payable (₹)</th>
                <th className="px-4 py-3 text-right">Deduction (₹)</th>
                <th className="px-4 py-3">Audit Rule & Explanation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {audit.items.map((item, idx) => {
                const cat = item.category as BillCategory;
                const catInfo = CATEGORY_INFO[cat] || CATEGORY_INFO['AMBIGUOUS_UNCATEGORIZED'];
                return (
                  <tr key={item.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3.5 text-center text-xs font-medium text-slate-400">
                      {idx + 1}
                    </td>
                    <td className="px-4 py-3.5 font-semibold text-slate-900">
                      {item.description}
                    </td>
                    <td className="px-4 py-3.5">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold border ${catInfo.badgeColor}`}
                      >
                        {item.category_label || catInfo.label}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-right font-medium text-slate-800">
                      {formatINR(item.billed_amount)}
                    </td>
                    <td className="px-4 py-3.5 text-right font-bold text-emerald-600">
                      {formatINR(item.payable_amount)}
                    </td>
                    <td className="px-4 py-3.5 text-right font-bold text-rose-600">
                      {item.deduction_amount > 0 ? `-${formatINR(item.deduction_amount)}` : '₹0.00'}
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-600 leading-relaxed max-w-xs">
                      {item.deduction_reason}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Applied Policy Assumptions & Tracing */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/80 space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-600" />
            Applied Insurance Rules & Assumptions
          </h3>
          <ul className="space-y-2 text-xs text-slate-600">
            {audit.assumptions && audit.assumptions.length > 0 ? (
              audit.assumptions.map((ass, i) => (
                <li key={i} className="flex items-start gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                  <span>{ass}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-400">Standard terms applied without special assumptions.</li>
            )}
          </ul>
        </div>

        {/* Policy-level Deductions Breakdown Card */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/80 space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            Policy-Level Deductions
          </h3>
          <div className="divide-y divide-slate-100 text-xs">
            <div className="py-2.5 flex items-center justify-between">
              <span className="text-slate-600 font-medium">Item-Level Deductions:</span>
              <span className="font-bold text-rose-600">
                {audit.item_level_deductions > 0 ? `-${formatINR(audit.item_level_deductions)}` : '₹0.00'}
              </span>
            </div>
            <div className="py-2.5 flex items-center justify-between">
              <span className="text-slate-600 font-medium">Policy Deductible Applied:</span>
              <span className="font-bold text-rose-600">
                {audit.deductible_applied > 0 ? `-${formatINR(audit.deductible_applied)}` : '₹0.00'}
              </span>
            </div>
            <div className="py-2.5 flex items-center justify-between">
              <span className="text-slate-600 font-medium">
                Co-Payment ({audit.copay_percentage}%):
              </span>
              <span className="font-bold text-rose-600">
                {audit.copay_applied > 0 ? `-${formatINR(audit.copay_applied)}` : '₹0.00'}
              </span>
            </div>
            <div className="py-2.5 flex items-center justify-between">
              <span className="text-slate-600 font-medium">Sum Insured Excess:</span>
              <span className="font-bold text-rose-600">
                {audit.sum_insured_excess_applied > 0
                  ? `-${formatINR(audit.sum_insured_excess_applied)}`
                  : '₹0.00'}
              </span>
            </div>
            <div className="pt-3 flex items-center justify-between font-bold text-sm">
              <span className="text-slate-900">Total Estimated Shortfall:</span>
              <span className="text-rose-600">{formatINR(audit.total_estimated_shortfall)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Flags & Ambiguous Warnings (if any) */}
      {audit.flags && audit.flags.length > 0 && (
        <div className="bg-amber-50 rounded-xl p-5 border border-amber-200 text-amber-900 space-y-3">
          <div className="flex items-center gap-2 font-bold text-sm text-amber-800">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            Items Requiring Attention or Manual Clarification
          </div>
          <ul className="list-disc list-inside text-xs space-y-1">
            {audit.flags.map((fl, i) => (
              <li key={i}>{fl}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Statutory Disclaimer */}
      <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-600 leading-relaxed">
        <p className="font-bold text-slate-700 mb-1">STATUTORY NOTICE:</p>
        <p>
          This audit is an automated pre-claim estimation. It is NOT an official insurer claim settlement,
          claim approval guarantee, or legal advice. Final admissible claim disbursement is determined by your
          health insurer's claims department upon submission of original bills, discharge summary, and medical reports.
        </p>
      </div>
    </div>
  );
};
