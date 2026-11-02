import React, { useState } from 'react';
import {
  PlayCircle,
  Sparkles,
  FileCheck,
} from 'lucide-react';
import { api } from '../services/api';

interface DemoWalkthroughProps {
  onDemoExecuted: (auditId: number) => void;
}

export const DemoWalkthrough: React.FC<DemoWalkthroughProps> = ({ onDemoExecuted }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runDemo = async () => {
    try {
      setIsRunning(true);
      setError(null);
      const res = await api.runDemoAudit();
      onDemoExecuted(res.id);
    } catch (err: any) {
      setError(err.message || 'Failed to execute demo audit');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-xl border border-emerald-800 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
          <Sparkles className="w-3.5 h-3.5" />
          Mandatory College Project Viva Case (Section 7)
        </div>
        <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
          Required Viva Demonstration Case: ₹1,50,000 Audit
        </h1>
        <p className="text-slate-300 text-sm sm:text-base max-w-3xl leading-relaxed">
          This demonstration showcases the deterministic insurance rule engine applying room-rent caps, 
          proportionate deductions, non-payable consumable exclusions, and financial reconciliation.
        </p>

        <div className="pt-2">
          <button
            onClick={runDemo}
            disabled={isRunning}
            className="flex items-center gap-2 px-6 py-3.5 bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-bold rounded-xl shadow-lg shadow-emerald-500/30 transition-all hover:scale-[1.02] disabled:opacity-50"
          >
            <PlayCircle className="w-5 h-5 text-slate-950" />
            <span>{isRunning ? 'Calculating & Saving...' : 'Run Live Demonstration Audit Now'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-800 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* Demonstration Case Structure */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Bill Inputs Card */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/80 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-xs font-bold">1</span>
              Submitted Hospital Bill Items (₹1,50,000)
            </h3>
            <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-md">
              Total: ₹1,50,000
            </span>
          </div>

          <div className="divide-y divide-slate-100 text-sm">
            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">1. Room Rent (Deluxe)</span>
                <span className="text-xs text-slate-400 block">5 days @ ₹5,000/day</span>
              </div>
              <span className="font-bold text-slate-900">₹25,000</span>
            </div>

            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">2. Doctor, Nursing & OT</span>
                <span className="text-xs text-slate-400 block">Associate medical charges</span>
              </div>
              <span className="font-bold text-slate-900">₹60,000</span>
            </div>

            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">3. Pharmacy</span>
                <span className="text-xs text-slate-400 block">Medicines and IV infusions</span>
              </div>
              <span className="font-bold text-slate-900">₹30,000</span>
            </div>

            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">4. Gloves, Masks & Admin Fees</span>
                <span className="text-xs text-slate-400 block">Consumables and hospital admin</span>
              </div>
              <span className="font-bold text-slate-900">₹8,000</span>
            </div>

            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">5. Diagnostics & Lab</span>
                <span className="text-xs text-slate-400 block">Pathology and imaging</span>
              </div>
              <span className="font-bold text-slate-900">₹27,000</span>
            </div>
          </div>
        </div>

        {/* Expected Results Card */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-emerald-200 bg-emerald-50/10 space-y-4">
          <div className="flex items-center justify-between border-b border-emerald-100 pb-3">
            <h3 className="font-bold text-slate-900 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-xs font-bold">2</span>
              Expected Audit Calculations
            </h3>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2.5 py-1 rounded-md">
              Target: ₹1,08,000 Payable
            </span>
          </div>

          <div className="divide-y divide-slate-100 text-sm">
            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">Room Rent Payable</span>
                <span className="text-xs text-rose-600 block">Deduction: -₹10,000 (Capped at ₹3k/day × 5d)</span>
              </div>
              <span className="font-bold text-emerald-600">₹15,000</span>
            </div>

            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">Doctor & OT Payable</span>
                <span className="text-xs text-rose-600 block">Deduction: -₹24,000 (60% proportionate ratio)</span>
              </div>
              <span className="font-bold text-emerald-600">₹36,000</span>
            </div>

            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">Pharmacy Payable</span>
                <span className="text-xs text-emerald-600 block">Deduction: ₹0 (100% eligible)</span>
              </div>
              <span className="font-bold text-emerald-600">₹30,000</span>
            </div>

            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">Consumables & Admin Fees</span>
                <span className="text-xs text-rose-600 block">Deduction: -₹8,000 (Non-payable schedule)</span>
              </div>
              <span className="font-bold text-slate-400">₹0</span>
            </div>

            <div className="py-2.5 flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">Diagnostics Payable</span>
                <span className="text-xs text-emerald-600 block">Deduction: ₹0 (100% eligible)</span>
              </div>
              <span className="font-bold text-emerald-600">₹27,000</span>
            </div>
          </div>
        </div>
      </div>

      {/* Mathematical Breakdown Callout Box */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 sm:p-8 space-y-4 border border-slate-800">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <FileCheck className="w-5 h-5 text-sky-400" />
          The Exact Mathematical Proof (For College Viva Defense)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs text-slate-300">
          <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700 space-y-2">
            <h4 className="font-bold text-sky-400">1. Room Rent Cap</h4>
            <p>
              Billed = ₹25,000 for 5 days = ₹5,000/day.<br />
              Policy Cap = ₹3,000/day.<br />
              Allowed = 5 × ₹3,000 = <strong className="text-white">₹15,000</strong>.<br />
              Deduction = ₹25,000 - ₹15,000 = <strong className="text-rose-400">₹10,000</strong>.
            </p>
          </div>

          <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700 space-y-2">
            <h4 className="font-bold text-indigo-400">2. Proportionate Ratio</h4>
            <p>
              Ratio = Allowed Daily Room Rate / Actual Billed Room Rate<br />
              Ratio = ₹3,000 / ₹5,000 = <strong className="text-white">0.60 (60%)</strong>.<br />
              Doctor & OT Allowed = ₹60,000 × 0.60 = <strong className="text-white">₹36,000</strong>.<br />
              Deduction = ₹60,000 - ₹36,000 = <strong className="text-rose-400">₹24,000</strong>.
            </p>
          </div>

          <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700 space-y-2">
            <h4 className="font-bold text-emerald-400">3. Non-Payables & Total</h4>
            <p>
              Consumables & Admin = Non-Payable = <strong className="text-rose-400">-₹8,000</strong>.<br />
              Total Payable = 15k + 36k + 30k + 0 + 27k = <strong className="text-emerald-400">₹1,08,000</strong>.<br />
              Total Shortfall = 10k + 24k + 8k = <strong className="text-rose-400">₹42,000</strong>.<br />
              Reconciliation: 1,08,000 + 42,000 = <strong className="text-white">₹1,50,000</strong>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
