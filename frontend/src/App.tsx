import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './components/Dashboard';
import { NewAudit } from './components/NewAudit';
import { AuditReport } from './components/AuditReport';
import { PolicyManager } from './components/PolicyManager';
import { AuditHistory } from './components/AuditHistory';
import { DemoWalkthrough } from './components/DemoWalkthrough';
import { VivaDocumentation } from './components/VivaDocumentation';
import { api } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [selectedAuditId, setSelectedAuditId] = useState<number | null>(null);
  const [isDemoRunning, setIsDemoRunning] = useState<boolean>(false);

  // Quick 1-click viva demo execution from anywhere
  const handleQuickDemo = async () => {
    try {
      setIsDemoRunning(true);
      const res = await api.runDemoAudit();
      setSelectedAuditId(res.id);
      setActiveTab('report');
    } catch (err: any) {
      alert(`Demo execution failed: ${err.message}`);
    } finally {
      setIsDemoRunning(false);
    }
  };

  const handleViewAudit = (id: number) => {
    setSelectedAuditId(id);
    setActiveTab('report');
  };

  const handleAuditSaved = (id: number) => {
    setSelectedAuditId(id);
    setActiveTab('report');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
      {/* Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onQuickDemo={handleQuickDemo}
        isDemoLoading={isDemoRunning}
      />

      {/* Main View Router */}
      <main className="flex-1 pb-16">
        {activeTab === 'dashboard' && (
          <Dashboard
            onStartAudit={() => setActiveTab('new-audit')}
            onViewAudit={handleViewAudit}
            onGoToPolicies={() => setActiveTab('policies')}
            onGoToDocs={() => setActiveTab('viva-guide')}
            onQuickDemo={handleQuickDemo}
          />
        )}

        {activeTab === 'new-audit' && (
          <NewAudit
            onAuditSaved={handleAuditSaved}
            onCancel={() => setActiveTab('dashboard')}
          />
        )}

        {activeTab === 'report' && selectedAuditId && (
          <AuditReport
            auditId={selectedAuditId}
            onBack={() => setActiveTab('dashboard')}
          />
        )}

        {activeTab === 'policies' && <PolicyManager />}

        {activeTab === 'history' && (
          <AuditHistory
            onViewAudit={handleViewAudit}
            onNewAudit={() => setActiveTab('new-audit')}
          />
        )}

        {activeTab === 'demo-showcase' && (
          <DemoWalkthrough
            onDemoExecuted={(id) => {
              setSelectedAuditId(id);
              setActiveTab('report');
            }}
          />
        )}

        {activeTab === 'viva-guide' && <VivaDocumentation />}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 py-6 text-xs text-center">
        <div className="max-w-7xl mx-auto px-4 space-y-2">
          <p className="font-semibold text-slate-300">
            Hospital Bill Auditor — Computer Science College Final Project
          </p>
          <p className="text-slate-500 max-w-xl mx-auto">
            Deterministic health insurance pre-claim calculation engine built with FastAPI, SQLite, PyMuPDF, ReportLab, and React.
          </p>
          <p className="text-slate-600">
            Estimates only. Not official insurance claim settlement advice.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

