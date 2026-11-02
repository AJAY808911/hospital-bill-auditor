import React, { useEffect, useState } from 'react';
import {
  FileText,
  Search,
  FileDown,
  Trash2,
  Eye,
  RefreshCw,
  AlertCircle,
  User,
} from 'lucide-react';
import { SavedAuditResponse } from '../types';
import { api } from '../services/api';
import { formatINR, formatDate } from '../utils/formatters';
import { StatusBadge } from './StatusBadge';

interface AuditHistoryProps {
  onViewAudit: (id: number) => void;
  onNewAudit: () => void;
}

export const AuditHistory: React.FC<AuditHistoryProps> = ({ onViewAudit, onNewAudit }) => {
  const [audits, setAudits] = useState<SavedAuditResponse[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAudits = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getAudits();
      setAudits(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudits();
  }, []);

  const handleDeleteAudit = async (id: number) => {
    if (!window.confirm(`Delete audit record AUD-${id}?`)) return;
    try {
      await api.deleteAudit(id);
      fetchAudits();
    } catch (err: any) {
      setError(err.message || 'Failed to delete audit');
    }
  };

  const filtered = audits.filter((a) => {
    const q = search.toLowerCase();
    return (
      (a.patient_name || '').toLowerCase().includes(q) ||
      (a.hospital_name || '').toLowerCase().includes(q) ||
      a.policy_name.toLowerCase().includes(q) ||
      (a.bill_number || '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Audit History & Records</h1>
          <p className="text-sm text-slate-500">
            Persistent database archive of pre-claim audits, item deductions, and downloadable reports.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchAudits}
            className="p-2 border border-slate-200 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-50 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={onNewAudit}
            className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-all"
          >
            + New Audit
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-600" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-xs font-bold underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
        <input
          type="text"
          placeholder="Search by patient, hospital, or policy..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 text-sm bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none shadow-sm"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200/80 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm animate-pulse">
            Loading persistent audit records from SQLite database...
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <FileText className="w-10 h-10 text-slate-300 mx-auto" />
            <h3 className="text-sm font-semibold text-slate-800">No Audits Found</h3>
            <p className="text-xs text-slate-500">
              {search ? 'No matching audit records for your search query.' : 'No audit records saved yet.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 text-xs uppercase font-semibold">
                <tr>
                  <th className="px-6 py-3.5">Ref / Patient</th>
                  <th className="px-6 py-3.5">Hospital & Policy</th>
                  <th className="px-6 py-3.5">Billed</th>
                  <th className="px-6 py-3.5">Est. Payable</th>
                  <th className="px-6 py-3.5">Shortfall</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5">Audit Date</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-slate-900">AUD-{a.id}</div>
                      <div className="text-xs text-slate-600 flex items-center gap-1 mt-0.5">
                        <User className="w-3 h-3 text-slate-400" />
                        <span>{a.patient_name || 'Patient'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-800">{a.hospital_name || 'Hospital'}</div>
                      <div className="text-xs text-slate-500 mt-0.5">{a.policy_name}</div>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-900">
                      {formatINR(a.total_billed)}
                    </td>
                    <td className="px-6 py-4 font-bold text-emerald-600">
                      {formatINR(a.total_estimated_payable)}
                    </td>
                    <td className="px-6 py-4 font-semibold text-rose-600">
                      {formatINR(a.total_estimated_shortfall)}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={a.status} />
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">
                      {formatDate(a.created_at)}
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button
                        onClick={() => onViewAudit(a.id)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-sky-600 bg-sky-50 hover:bg-sky-100 rounded-lg transition-colors"
                        title="View Report"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View</span>
                      </button>
                      <a
                        href={api.getAuditPdfUrl(a.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-2 py-1 text-xs font-medium text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                        title="Download PDF"
                      >
                        <FileDown className="w-3.5 h-3.5" />
                      </a>
                      <button
                        onClick={() => handleDeleteAudit(a.id)}
                        className="inline-flex items-center px-2 py-1 text-xs font-medium text-rose-600 hover:text-rose-800 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors"
                        title="Delete Record"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
