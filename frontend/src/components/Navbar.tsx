import React from 'react';
import {
  ShieldCheck,
  History,
  HelpCircle,
  PlayCircle,
  PlusCircle,
  Activity,
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onQuickDemo: () => void;
  isDemoLoading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onQuickDemo,
  isDemoLoading,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'new-audit', label: 'New Audit', icon: PlusCircle },
    { id: 'history', label: 'Audit History', icon: History },
    { id: 'policies', label: 'Policy Rules', icon: ShieldCheck },
    { id: 'demo-showcase', label: 'Section 7 Demo', icon: PlayCircle },
    { id: 'viva-guide', label: 'Viva Guide & Docs', icon: HelpCircle },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-900 text-white shadow-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Branding */}
          <div
            className="flex items-center space-x-3 cursor-pointer"
            onClick={() => setActiveTab('dashboard')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-white">
                  Hospital Bill Auditor
                </span>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-sky-950 text-sky-400 border border-sky-800">
                  Pre-Claim Engine
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Health Insurance Eligibility & Deduction Estimator
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-sky-600 text-white shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* 1-Click Quick Demo CTA */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onQuickDemo}
              disabled={isDemoLoading}
              className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm hover:shadow transition-all disabled:opacity-50"
              title="Runs the required ₹1,50,000 Section 7 college viva demo case with one click"
            >
              <PlayCircle className="w-4 h-4" />
              <span>{isDemoLoading ? 'Running...' : 'Run Viva Demo'}</span>
            </button>
          </div>
        </div>

        {/* Mobile menu bar */}
        <div className="md:hidden flex space-x-1 py-2 overflow-x-auto border-t border-slate-800 scrollbar-none">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-md text-xs whitespace-nowrap font-medium ${
                  isActive
                    ? 'bg-sky-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
