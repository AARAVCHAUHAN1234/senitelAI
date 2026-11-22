import React, { useState, useEffect } from "react";
import { Settings as SettingsIcon, RotateCcw, Trash2, Shield, Radio, CheckCircle2 } from "lucide-react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { apiGet, apiPost } from "../core/api";

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<any>(null);
  const [statusMsg, setStatusMsg] = useState("");
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  const loadSettings = () => {
    apiGet("/api/settings").then(setSettings).catch(() => {});
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleDemoAction = async (action: string) => {
    setLoadingAction(action);
    setStatusMsg("");
    try {
      await apiPost(`/api/demo/${action}`);
      setStatusMsg(`Demo action completed: ${action}`);
      loadSettings();
    } catch (e: any) {
      setStatusMsg(`Error: ${e.message}`);
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <Card title="DAST Operating Mode" subtitle="Strict separation between simulated sandbox and live targets">
        <div className="space-y-4 text-xs">
          <div className="flex items-center justify-between p-3.5 rounded-lg bg-slate-950 border border-slate-800">
            <div>
              <span className="font-semibold text-slate-100 block">Current Operating Mode</span>
              <span className="text-slate-400 mt-0.5 block">
                All security agent executions are strictly bound to VoyageSim synthetic travel portal.
              </span>
            </div>
            <span className="px-3 py-1 rounded-md text-xs font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-700">
              DEMO / SIMULATED
            </span>
          </div>

          <div className="flex items-center justify-between p-3.5 rounded-lg bg-slate-950 border border-slate-800">
            <div>
              <span className="font-semibold text-slate-100 block">Live Target Testing</span>
              <span className="text-slate-400 mt-0.5 block">
                Requires explicit customer authorization and valid domain cryptographic ownership challenge.
              </span>
            </div>
            <span className="px-3 py-1 rounded-md text-xs font-mono text-slate-500 bg-slate-900 border border-slate-800">
              UNCONFIGURED
            </span>
          </div>
        </div>
      </Card>

      <Card title="VoyageSim Target Configuration" subtitle="Target connection and module discovery status">
        <div className="space-y-3 text-xs">
          <div className="flex justify-between py-2 border-b border-slate-800">
            <span className="text-slate-400">VoyageSim Endpoint URL:</span>
            <span className="font-mono text-slate-200">{settings?.voyagesim_url || "http://localhost:8001"}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-800">
            <span className="text-slate-400">Database Engine:</span>
            <span className="font-mono text-slate-200">{settings?.database_url}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-800">
            <span className="text-slate-400">Enabled Modules:</span>
            <span className="font-mono text-cyan-400">
              {Array.isArray(settings?.enabled_modules) ? settings.enabled_modules.join(", ") : "all"}
            </span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-slate-400">AI Assistance Provider:</span>
            <span className="font-mono text-emerald-400">Deterministic Rule Engine (Fallback Active)</span>
          </div>
        </div>
      </Card>

      <Card title="Demo Controls & Seed Reset" subtitle="Restore baseline synthetic dataset or clear generated findings">
        <div className="space-y-4">
          <p className="text-xs text-slate-400 leading-relaxed">
            Use these controls to reset the platform state during live demonstrations or clear dynamically generated findings.
          </p>
          <div className="flex items-center gap-3">
            <Button
              variant="danger"
              size="sm"
              onClick={() => handleDemoAction("reset")}
              loading={loadingAction === "reset"}
              icon={<RotateCcw className="w-3.5 h-3.5" />}
            >
              Reset to Baseline Seed
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handleDemoAction("clear-findings")}
              loading={loadingAction === "clear-findings"}
              icon={<Trash2 className="w-3.5 h-3.5" />}
            >
              Clear Findings
            </Button>
          </div>
          {statusMsg && (
            <p className="text-xs font-mono text-cyan-400 bg-cyan-950/40 p-2.5 rounded-lg border border-cyan-800/40">
              {statusMsg}
            </p>
          )}
        </div>
      </Card>
    </div>
  );
};
