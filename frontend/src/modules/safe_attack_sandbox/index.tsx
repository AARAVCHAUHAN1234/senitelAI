import React, { useState, useEffect } from "react";
import { LockKeyhole, ShieldAlert, AlertTriangle, Play, RefreshCw, XCircle, CheckCircle2, ShieldCheck, Square } from "lucide-react";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Badge } from "../../components/Badge";
import { apiGet, apiPost } from "../../core/api";

export default function SafeAttackSandboxPage() {
  const [policy, setPolicy] = useState<any>(null);
  const [auditChain, setAuditChain] = useState<any[]>([]);
  const [actionLoading, setActionLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");

  const loadData = async () => {
    try {
      const p = await apiGet("/api/modules/safe_attack_sandbox/policy");
      setPolicy(p);
      const a = await apiGet("/api/modules/safe_attack_sandbox/audit-chain");
      setAuditChain(a || []);
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleEmergencyStop = async () => {
    setActionLoading(true);
    try {
      const res = await apiPost("/api/modules/safe_attack_sandbox/emergency-stop");
      setStatusMsg("EMERGENCY STOP ENGAGED: All autonomous testing halted immediately (<1s).");
      loadData();
    } catch (e: any) {
      setStatusMsg(`Error: ${e.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReleaseStop = async () => {
    setActionLoading(true);
    try {
      const res = await apiPost("/api/modules/safe_attack_sandbox/emergency-release");
      setStatusMsg("Emergency stop released. System ready for controlled testing.");
      loadData();
    } catch (e: any) {
      setStatusMsg(`Error: ${e.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReplay = async (id: number) => {
    try {
      const res = await apiPost(`/api/modules/safe_attack_sandbox/replay/${id}`);
      setStatusMsg(`Replayed audit request ${id} successfully (Status: ${res.simulated_response_status}, Hash Verified).`);
    } catch (e: any) {
      setStatusMsg(`Replay failed: ${e.message}`);
    }
  };

  const isStopEngaged = policy?.emergency_stop_engaged;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider block mb-1">
            INNOVATION MODULE 6 · SAFE ATTACK SANDBOX
          </span>
          <h2 className="text-base font-bold text-slate-100">
            PolicyGate Execution Bounds & Cryptographic Audit Trail
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Strict safety boundaries guaranteeing zero testing of unauthorized production domains or real financial transactions
          </p>
        </div>

        <div className="flex items-center gap-3">
          {isStopEngaged ? (
            <Button
              variant="secondary"
              size="sm"
              onClick={handleReleaseStop}
              loading={actionLoading}
              icon={<Play className="w-3.5 h-3.5 text-emerald-400" />}
            >
              Release Emergency Stop
            </Button>
          ) : (
            <Button
              variant="danger"
              size="sm"
              onClick={handleEmergencyStop}
              loading={actionLoading}
              icon={<Square className="w-3.5 h-3.5" />}
            >
              EMERGENCY STOP (1s)
            </Button>
          )}
        </div>
      </div>

      {statusMsg && (
        <div className="p-3 rounded-lg bg-cyan-950/60 border border-cyan-800 text-cyan-300 text-xs font-mono">
          {statusMsg}
        </div>
      )}

      {/* Blueprint Style Canvas (ref-11) */}
      <div className="relative rounded-2xl border-2 border-cyan-800/80 bg-[#071328] p-6 overflow-hidden shadow-2xl">
        {/* Blueprint Grid Background */}
        <div
          className="absolute inset-0 opacity-15 pointer-events-none"
          style={{
            backgroundImage: "linear-gradient(#06b6d4 1px, transparent 1px), linear-gradient(90deg, #06b6d4 1px, transparent 1px)",
            backgroundSize: "32px 32px"
          }}
        />

        <div className="relative z-10 space-y-6">
          <div className="flex items-center justify-between border-b border-cyan-800/50 pb-3">
            <span className="text-xs font-mono font-bold text-cyan-300 tracking-wider">
              [BLUEPRINT ARCHITECTURE: ISOLATED TESTING ENCLAVE]
            </span>
            <span className="text-[11px] font-mono text-emerald-400 font-bold">
              BOUNDARY: STRICT SYNTHETIC ENFORCED
            </span>
          </div>

          {/* Three-Box Flow: Agent Runner -> Policy Gate -> Isolated Sandbox */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            {/* Box 1: Autonomous Agent Runner */}
            <div className="p-4 rounded-xl border border-cyan-600/60 bg-slate-950/80 space-y-2">
              <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase block">
                1. Agent Test Runner
              </span>
              <p className="text-xs text-slate-200 font-medium">13 Autonomous Agents</p>
              <p className="text-[11px] text-slate-400">
                Synthesizes parameterized test requests (IDOR, fare, refund).
              </p>
              <div className="pt-2 border-t border-slate-800 flex justify-between text-[10px] font-mono text-cyan-300">
                <span>Concurrency: {policy?.max_concurrency || 5}</span>
                <span>Rate: {policy?.rate_limit_per_minute || 60}/min</span>
              </div>
            </div>

            {/* Box 2: Policy Gate */}
            <div className="p-4 rounded-xl border-2 border-cyan-400 bg-cyan-950/40 space-y-2 shadow-lg shadow-cyan-950/40">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-cyan-300 font-bold uppercase block">
                  2. Policy Gate Guard
                </span>
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
              </div>
              <p className="text-xs text-slate-100 font-bold">Inspection & Validation</p>
              <ul className="text-[10px] text-cyan-200/90 space-y-1 font-mono">
                <li>✓ Allowlist Target Verification</li>
                <li>✓ Token Bucket Rate Limiter</li>
                <li>✓ Destructive Action Block</li>
                <li>✓ Synthetic Account Guard</li>
              </ul>
            </div>

            {/* Box 3: Isolated Sandbox Target */}
            <div className="p-4 rounded-xl border border-emerald-600/60 bg-slate-950/80 space-y-2">
              <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase block">
                3. Isolated Target
              </span>
              <p className="text-xs text-slate-200 font-medium">VoyageSim Travel Platform</p>
              <p className="text-[11px] text-slate-400">
                Synthetic multi-tenant B2B target running on port 8001.
              </p>
              <div className="pt-2 border-t border-slate-800 flex justify-between text-[10px] font-mono text-emerald-400">
                <span>Real Transactions: BLOCKED</span>
                <span>Prod Access: REFUSED</span>
              </div>
            </div>
          </div>

          {/* Blocked Production Internet Visual Indicator */}
          <div className="p-3 rounded-lg border border-rose-900/80 bg-rose-950/30 flex items-center justify-between text-xs text-rose-300">
            <div className="flex items-center gap-2">
              <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>Public Internet & Production Systems: <b>Permanently Blocked by Policy Gate</b></span>
            </div>
            <span className="font-mono text-[10px] bg-rose-950 px-2 py-0.5 rounded border border-rose-800 text-rose-200">
              0.0.0.0/0 OUT-OF-SCOPE
            </span>
          </div>
        </div>
      </div>

      {/* Target Allowlist & Synthetic Identities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
        <Card title="Allowlisted Testing Targets">
          <ul className="space-y-2 font-mono text-xs">
            {(policy?.target_allowlist || ["http://localhost:8001/*"]).map((t: string) => (
              <li key={t} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-emerald-400 flex items-center justify-between">
                <span>{t}</span>
                <span className="text-[10px] text-slate-400">AUTHORIZED TARGET</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Restricted Synthetic Identities">
          <ul className="space-y-2 font-mono text-xs">
            {(policy?.synthetic_identities || []).map((id: string) => (
              <li key={id} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-cyan-300 flex items-center justify-between">
                <span>{id}</span>
                <span className="text-[10px] text-slate-400">SYNTHETIC TOKEN</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {/* Cryptographic Hash-Chained Audit Log */}
      <Card
        title="Append-Only Hash-Chained Audit Ledger"
        subtitle="Cryptographically chained SHA-256 audit log proving non-destructive test execution"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono text-[11px]">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                <th className="pb-3">Action</th>
                <th className="pb-3">Target URL</th>
                <th className="pb-3">Verdict</th>
                <th className="pb-3">SHA-256 Block Hash</th>
                <th className="pb-3 text-right">Replay</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {auditChain.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 font-bold text-cyan-400">{entry.action}</td>
                  <td className="py-2.5 text-slate-300">{entry.target_url}</td>
                  <td className="py-2.5">
                    {entry.policy_verdict === "ALLOWED" ? (
                      <span className="text-emerald-400 font-bold">ALLOWED</span>
                    ) : (
                      <span className="text-rose-400 font-bold">BLOCKED</span>
                    )}
                  </td>
                  <td className="py-2.5 text-slate-500 truncate max-w-xs">{entry.curr_hash}</td>
                  <td className="py-2.5 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleReplay(entry.id)}
                    >
                      Replay
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
