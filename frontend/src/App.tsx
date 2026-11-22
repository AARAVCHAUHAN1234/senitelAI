import React, { useState, useEffect, useCallback } from "react";
import { Sidebar } from "./components/Sidebar";
import { TopBar } from "./components/TopBar";
import { LoadingState } from "./components/LoadingState";
import { Overview } from "./pages/Overview";
import { SecurityGraph } from "./pages/SecurityGraph";
import { AgentCenter } from "./pages/AgentCenter";
import { ApiDiscovery } from "./pages/ApiDiscovery";
import { Findings } from "./pages/Findings";
import { Reports } from "./pages/Reports";
import { AuditLogs } from "./pages/AuditLogs";
import { Settings } from "./pages/Settings";

// Innovation Modules
import BusinessLogicBrainPage from "./modules/business_logic_brain";
import AttackChainIntelligencePage from "./modules/attack_chain_intelligence";
import TenantRoleMatrixPage from "./modules/tenant_role_matrix";
import PredictiveImpactPage from "./modules/predictive_impact";
import SecurityMemoryPage from "./modules/security_memory";
import SafeAttackSandboxPage from "./modules/safe_attack_sandbox";

import { apiGet, apiPost } from "./core/api";
import { useEvents, SystemEvent } from "./core/useEvents";
import { CheckCircle2, AlertTriangle, X } from "lucide-react";

export function App() {
  const [currentTab, setCurrentTab] = useState("Overview");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "info" | "success" | "error" } | null>(null);

  const refreshDashboard = useCallback(async () => {
    try {
      const data = await apiGet("/api/dashboard");
      setDashboardData(data);
    } catch {
      // Ignore initial connection errors
    } finally {
      setLoading(false);
    }
  }, []);

  // Real-time SSE subscription: whenever an event arrives, refresh dashboard
  const handleLiveEvent = useCallback((event: SystemEvent) => {
    refreshDashboard();
    if (event.kind.includes("verified") || event.kind.includes("detected") || event.kind.includes("completed")) {
      setToast({ message: event.message, type: "success" });
    }
  }, [refreshDashboard]);

  const { connected } = useEvents(handleLiveEvent);

  useEffect(() => {
    refreshDashboard();
    // Poll every 10 seconds as safety net
    const interval = setInterval(refreshDashboard, 10000);
    return () => clearInterval(interval);
  }, [refreshDashboard]);

  // Auto-dismiss toast
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const handleRunScenario = async (key: string) => {
    setBusy(true);
    try {
      await apiPost(`/api/demo/run/${key}`);
      setToast({ message: `Executing scenario: ${key.toUpperCase()}`, type: "info" });
      await refreshDashboard();
    } catch (e: any) {
      setToast({ message: e.message, type: "error" });
    } finally {
      setBusy(false);
    }
  };

  const handleRunAll = async () => {
    setBusy(true);
    try {
      await apiPost("/api/demo/run-all");
      setToast({ message: "All six synthetic scenarios queued for execution", type: "success" });
      await refreshDashboard();
    } catch (e: any) {
      setToast({ message: e.message, type: "error" });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans">
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        criticalCount={dashboardData?.metrics?.critical || 0}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col transition-all duration-200 ${
          sidebarCollapsed ? "pl-16" : "pl-64"
        }`}
      >
        {/* TopBar */}
        <TopBar
          currentTab={currentTab}
          connected={connected}
          onRunAll={handleRunAll}
          runningAll={busy}
          onSearchChange={setSearchQuery}
          searchQuery={searchQuery}
        />

        {/* Toast Notification */}
        {toast && (
          <div className="fixed bottom-5 right-5 z-50 flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-slate-900 border border-cyan-800 text-xs shadow-2xl animate-in slide-in-from-bottom duration-200">
            {toast.type === "error" ? (
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
            )}
            <span className="text-slate-200">{toast.message}</span>
            <button onClick={() => setToast(null)} className="text-slate-400 hover:text-slate-200 p-0.5 rounded">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* View Router */}
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {loading && !dashboardData ? (
            <LoadingState message="Connecting to SentinelAI autonomous security engine..." />
          ) : currentTab === "Overview" ? (
            <Overview
              data={dashboardData}
              onNavigate={setCurrentTab}
              onRunScenario={handleRunScenario}
              onRunAll={handleRunAll}
              busy={busy}
            />
          ) : currentTab === "Live Security Graph" ? (
            <SecurityGraph />
          ) : currentTab === "Agent Control Center" ? (
            <AgentCenter
              agents={dashboardData?.agents || []}
              onRefresh={refreshDashboard}
            />
          ) : currentTab === "API Discovery" ? (
            <ApiDiscovery />
          ) : currentTab === "Vulnerability Findings" ? (
            <Findings />
          ) : currentTab === "Business Logic Intelligence" ? (
            <BusinessLogicBrainPage />
          ) : currentTab === "Attack Chain Intelligence" ? (
            <AttackChainIntelligencePage />
          ) : currentTab === "Tenant & Role Matrix" ? (
            <TenantRoleMatrixPage />
          ) : currentTab === "Predictive Security Impact" ? (
            <PredictiveImpactPage />
          ) : currentTab === "Security Memory" ? (
            <SecurityMemoryPage />
          ) : currentTab === "Safe Attack Sandbox" ? (
            <SafeAttackSandboxPage />
          ) : currentTab === "Reports & Evidence" ? (
            <Reports />
          ) : currentTab === "Audit Logs" ? (
            <AuditLogs />
          ) : currentTab === "Settings" ? (
            <Settings />
          ) : (
            <div>Page Not Found</div>
          )}
        </main>

        {/* Footer */}
        <footer className="h-10 border-t border-slate-800/80 px-6 flex items-center justify-between text-[11px] text-slate-400 font-mono bg-slate-950/40">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>VoyageSim Isolated Enclave Protected</span>
          </div>
          <div>SentinelAI DAST Platform · TBO Security Hackathon 2026</div>
        </footer>
      </div>
    </div>
  );
}

export default App;
