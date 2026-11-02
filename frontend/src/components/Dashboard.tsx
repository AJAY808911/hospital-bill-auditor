import React, { useEffect, useState } from 'react';
import {
  FileText,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  PlusCircle,
  ArrowRight,
  ShieldCheck,
  FileDown,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { DashboardStatsResponse } from '../types';
import { api } from '../services/api';
import { formatINR, formatPercent, formatDate } from '../utils/formatters';
import { StatusBadge } from './StatusBadge';

interface DashboardProps {
  onStartAudit: () => void;
  onViewAudit: (id: number) => void;
  onGoToPolicies: () => void;
  onGoToDocs: () => void;
  onQuickDemo: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  onStartAudit,
  onViewAudit,
  onGoToPolicies,
  onGoToDocs,
  onQuickDemo,
}) => {
  const [stats, setStats] = useState<DashboardStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Header & Quick Actions */}
      <div className="bg-gradient-to-r from-slate-900 via-sky-950 to-indigo-950 rounded-2xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden border border-slate-800">
        <div className="absolute right-0 top-0 -mt-8 -mr-8 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/20 text-sky-300 border border-sky-400/30">
              <Sparkles className="w-3.5 h-3.5" />
              Pre-Claim Transparency for Indian Health Insurance
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Hospital Bill Pre-Claim Auditor
            </h1>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              Eliminate unexpected out-of-pocket medical bill deductions. Upload or enter hospital bills, 
              apply configurable insurance rules (room rent caps, proportionate deductions, non-payable consumables), 
              and calculate estimated insurer settlements before filing claims.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={onStartAudit}
              className="flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm bg-sky-500 hover:bg-sky-400 text-slate-950 shadow-lg shadow-sky-500/25 transition-all hover:scale-[1.02]"
            >
              <PlusCircle className="w-5 h-5 text-slate-950" />
              <span>New Bill Audit</span>
            </button>
            <button
              onClick={onQuickDemo}
              className="flex items-center gap-2 px-4 py-3 rounded-xl font-semibold text-sm bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 transition-all"
            >
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span>Section 7 Demo</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-white rounded-xl shadow-sm border border-slate-200 animate-pulse p-5" />
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between text-red-700">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5" />
            <span className="text-sm">{error}</span>
          </div>
          <button
            onClick={fetchStats}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-white border border-red-300 rounded-lg shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Total Audits */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Audits Completed
              </span>
              <div className="w-8 h-8 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center">
                <FileText className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-slate-900">
                {stats?.total_audits_count || 0}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Persistent records in local database
            </p>
          </div>

          {/* Total Billed Volume */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Total Billed Volume
              </span>
              <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                <TrendingUp className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-slate-900">
                {formatINR(stats?.total_billed_volume)}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Aggregated gross hospital charges
            </p>
          </div>

          {/* Estimated Payable */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">
                Est. Insurer Payable
              </span>
              <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <CheckCircle2 className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-emerald-600">
                {formatINR(stats?.total_estimated_payable_volume)}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Avg. coverage:{' '}
              <span className="font-semibold text-emerald-600">
                {formatPercent(stats?.average_payable_percentage)}
              </span>
            </p>
          </div>

          {/* Potential Shortfall */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200/80 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-rose-700 uppercase tracking-wider">
                Est. Patient Shortfall
              </span>
              <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
                <AlertCircle className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-rose-600">
                {formatINR(stats?.total_shortfall_volume)}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Deductions, caps & non-payables
            </p>
          </div>
        </div>
      )}

      {/* Recent Audits Table & Navigation Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Audits List (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200/80 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900">Recent Bill Audits</h2>
              <p className="text-xs text-slate-500">Latest pre-claim evaluation records</p>
            </div>
            <button
              onClick={fetchStats}
              className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
              title="Refresh audits"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {loading ? (
            <div className="p-8 text-center text-slate-400 text-sm animate-pulse">
              Loading recent audits...
            </div>
          ) : !stats?.recent_audits || stats.recent_audits.length === 0 ? (
            <div className="p-12 text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-semibold text-slate-800">No Audits Run Yet</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Run the college viva demo case or upload a hospital bill to start estimating insurance deductions.
              </p>
              <div className="pt-2">
                <button
                  onClick={onQuickDemo}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-sky-600 text-white hover:bg-sky-500"
                >
                  Run Section 7 Demo
                </button>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-100 text-left text-sm">
                <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-medium">
                  <tr>
                    <th className="px-6 py-3">Patient / Bill</th>
                    <th className="px-6 py-3">Billed</th>
                    <th className="px-6 py-3">Est. Payable</th>
                    <th className="px-6 py-3">Shortfall</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-normal">
                  {stats.recent_audits.map((a) => (
                    <tr key={a.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-slate-900">
                          {a.patient_name || 'Patient'}
                        </div>
                        <div className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                          <span>{a.policy_name}</span>
                          <span>•</span>
                          <span>{formatDate(a.created_at)}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-medium text-slate-900">
                        {formatINR(a.total_billed)}
                      </td>
                      <td className="px-6 py-4 font-semibold text-emerald-600">
                        {formatINR(a.total_estimated_payable)}
                      </td>
                      <td className="px-6 py-4 font-medium text-rose-600">
                        {formatINR(a.total_estimated_shortfall)}
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={a.status} />
                      </td>
                      <td className="px-6 py-4 text-right space-x-2">
                        <button
                          onClick={() => onViewAudit(a.id)}
                          className="px-2.5 py-1 text-xs font-semibold text-sky-600 hover:text-sky-700 bg-sky-50 hover:bg-sky-100 rounded-md transition-colors"
                        >
                          View
                        </button>
                        <a
                          href={api.getAuditPdfUrl(a.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-2 py-1 text-xs font-medium text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors"
                          title="Download PDF Report"
                        >
                          <FileDown className="w-3.5 h-3.5" />
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Feature Navigation / System Health Sidebar (1 col) */}
        <div className="space-y-6">
          {/* Quick Setup Card */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200/80 p-6 space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Project Modules</h3>
            
            <div
              onClick={onGoToPolicies}
              className="group p-3.5 rounded-xl border border-slate-200 hover:border-sky-500 bg-slate-50 hover:bg-sky-50/50 cursor-pointer transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center group-hover:bg-sky-500 group-hover:text-white transition-colors">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-900">Insurance Policies</h4>
                    <p className="text-xs text-slate-500">Configure room rent caps & co-pays</p>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-sky-600 group-hover:translate-x-0.5 transition-all" />
              </div>
            </div>

            <div
              onClick={onGoToDocs}
              className="group p-3.5 rounded-xl border border-slate-200 hover:border-indigo-500 bg-slate-50 hover:bg-indigo-50/50 cursor-pointer transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-900">Viva Guide & Architecture</h4>
                    <p className="text-xs text-slate-500">Algorithms, formulas & viva defense Q&A</p>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-0.5 transition-all" />
              </div>
            </div>
          </div>

          {/* Statutory Disclaimer Card */}
          <div className="bg-amber-50/60 rounded-xl border border-amber-200 p-4 text-xs text-amber-900 leading-relaxed space-y-2">
            <div className="font-semibold flex items-center gap-1.5 text-amber-800">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              Statutory Educational Disclaimer
            </div>
            <p>
              This application provides preliminary pre-claim financial estimates based on defined rules.
              It does not guarantee insurer claim approvals, nor does it constitute legal or official underwriting advice.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

