import React, { useEffect, useState } from 'react';
import {
  Plus,
  Trash2,
  AlertCircle,
} from 'lucide-react';
import { PolicyConfig, RoomRentLimitType } from '../types';
import { api } from '../services/api';
import { formatINR } from '../utils/formatters';

export const PolicyManager: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New policy form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [sumInsured, setSumInsured] = useState(500000);
  const [roomRentType, setRoomRentType] = useState<RoomRentLimitType>('FIXED_AMOUNT');
  const [roomRentLimitAmount, setRoomRentLimitAmount] = useState(3000);
  const [roomRentLimitPct, setRoomRentLimitPct] = useState(1.0);
  const [applyProportionate, setApplyProportionate] = useState(true);
  const [copayPct, setCopayPct] = useState(0);
  const [deductible, setDeductible] = useState(0);
  const [stayDays, setStayDays] = useState(5);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getPolicies();
      setPolicies(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch policy configurations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleCreatePolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Policy name is required.');
      return;
    }

    try {
      setError(null);
      await api.createPolicy({
        name,
        description,
        sum_insured: sumInsured,
        room_rent_limit_type: roomRentType,
        room_rent_limit_amount: roomRentLimitAmount,
        room_rent_limit_percentage: roomRentLimitPct,
        apply_proportionate_deduction: applyProportionate,
        copay_percentage: copayPct,
        deductible_amount: deductible,
        length_of_stay_days: stayDays,
        non_payable_categories: ['NON_PAYABLE_CONSUMABLE', 'NON_PAYABLE_ADMIN'],
      });
      setShowCreateModal(false);
      setName('');
      setDescription('');
      fetchPolicies();
    } catch (err: any) {
      setError(err.message || 'Failed to create policy');
    }
  };

  const handleDeletePolicy = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this policy configuration?')) return;
    try {
      await api.deletePolicy(id);
      fetchPolicies();
    } catch (err: any) {
      setError(err.message || 'Failed to delete policy');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Health Insurance Policy Rules</h1>
          <p className="text-sm text-slate-500">
            Define sum insured caps, room rent limits, proportionate deduction ratios, and co-payment terms.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Add Custom Policy</span>
        </button>
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

      {/* Policies Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 bg-white rounded-xl shadow-sm border border-slate-200 animate-pulse p-5" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {policies.map((p) => (
            <div
              key={p.id}
              className={`bg-white rounded-xl p-6 shadow-sm border transition-shadow ${
                p.is_default
                  ? 'border-sky-300 ring-1 ring-sky-200'
                  : 'border-slate-200/80 hover:shadow-md'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  {p.is_default && (
                    <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-sky-100 text-sky-800 mb-2">
                      Default Demo Policy
                    </span>
                  )}
                  <h3 className="font-bold text-slate-900 text-base">{p.name}</h3>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                    {p.description || 'Standard insurance policy rule configuration.'}
                  </p>
                </div>

                {!p.is_default && p.id && (
                  <button
                    onClick={() => handleDeletePolicy(p.id!)}
                    className="text-slate-400 hover:text-red-600 p-1 rounded transition-colors"
                    title="Delete policy"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>

              <div className="mt-5 space-y-2.5 text-xs border-t border-slate-100 pt-4">
                <div className="flex justify-between">
                  <span className="text-slate-500 font-medium">Sum Insured:</span>
                  <span className="font-bold text-slate-900">{formatINR(p.sum_insured)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 font-medium">Room Rent Limit:</span>
                  <span className="font-semibold text-slate-800">
                    {p.room_rent_limit_type === 'FIXED_AMOUNT'
                      ? `₹${p.room_rent_limit_amount}/day`
                      : p.room_rent_limit_type === 'PERCENTAGE_OF_SI'
                      ? `${p.room_rent_limit_percentage}% of SI/day`
                      : 'No Limit'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 font-medium">Proportionate Deduction:</span>
                  <span className="font-semibold text-slate-800">
                    {p.apply_proportionate_deduction ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 font-medium">Co-Payment / Deductible:</span>
                  <span className="font-semibold text-slate-800">
                    {p.copay_percentage}% / ₹{p.deductible_amount}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Policy Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 sm:p-8 space-y-6 border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <h3 className="text-lg font-bold text-slate-900">Add New Insurance Policy</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreatePolicy} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Policy Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Star Health Family Optima"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description / Notes</label>
                <textarea
                  rows={2}
                  placeholder="Policy clauses, sublimits or network hospital notes"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Sum Insured (₹)</label>
                  <input
                    type="number"
                    min="1000"
                    step="1000"
                    value={sumInsured}
                    onChange={(e) => setSumInsured(Number(e.target.value))}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Room Rent Cap Type</label>
                  <select
                    value={roomRentType}
                    onChange={(e) => setRoomRentType(e.target.value as RoomRentLimitType)}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  >
                    <option value="FIXED_AMOUNT">Fixed Daily Limit (₹)</option>
                    <option value="PERCENTAGE_OF_SI">% of Sum Insured</option>
                    <option value="NO_LIMIT">No Room Cap (Unlimited)</option>
                  </select>
                </div>
              </div>

              {roomRentType === 'FIXED_AMOUNT' && (
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Daily Room Limit Amount (₹)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="500"
                    value={roomRentLimitAmount}
                    onChange={(e) => setRoomRentLimitAmount(Number(e.target.value))}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  />
                </div>
              )}

              {roomRentType === 'PERCENTAGE_OF_SI' && (
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Daily Room Limit (% of Sum Insured)
                  </label>
                  <input
                    type="number"
                    min="0.1"
                    max="10"
                    step="0.1"
                    value={roomRentLimitPct}
                    onChange={(e) => setRoomRentLimitPct(Number(e.target.value))}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  />
                </div>
              )}

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="prop_ded"
                  checked={applyProportionate}
                  onChange={(e) => setApplyProportionate(e.target.checked)}
                  className="rounded text-sky-600 focus:ring-sky-500 h-4 w-4"
                />
                <label htmlFor="prop_ded" className="font-semibold text-slate-700 cursor-pointer">
                  Apply Proportionate Deduction on Associate Charges
                </label>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Co-Payment (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={copayPct}
                    onChange={(e) => setCopayPct(Number(e.target.value))}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Deductible (₹)</label>
                  <input
                    type="number"
                    min="0"
                    step="1000"
                    value={deductible}
                    onChange={(e) => setDeductible(Number(e.target.value))}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Default Length of Stay (Days)</label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={stayDays}
                  onChange={(e) => setStayDays(Number(e.target.value))}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg font-semibold hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg font-bold shadow-sm"
                >
                  Save Policy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
