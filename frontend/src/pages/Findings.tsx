import React, { useState, useEffect, useCallback } from "react";
import { ShieldAlert, CheckCircle2, RefreshCw, Search, Filter, ShieldCheck, AlertTriangle } from "lucide-react";
import { Card } from "../components/Card";
import { Badge } from "../components/Badge";
import { Button } from "../components/Button";
import { Drawer } from "../components/Drawer";
import { apiGet, apiPost } from "../core/api";

export const Findings: React.FC = () => {
  const [findings, setFindings] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [selectedFinding, setSelectedFinding] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [verifyingId, setVerifyingId] = useState<number | null>(null);

  const loadFindings = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet(`/api/findings?q=${encodeURIComponent(query)}`);
      setFindings(data || []);
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    loadFindings();
  }, [loadFindings]);

  const handleVerify = async (id: number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setVerifyingId(id);
    try {
      const updated = await apiPost(`/api/findings/${id}/verify`);
      setFindings((prev) => prev.map((f) => (f.id === id ? updated : f)));
      if (selectedFinding?.id === id) setSelectedFinding(updated);
    } catch {
      // Ignore
    } finally {
      setVerifyingId(null);
    }
  };

  const handleRetest = async (id: number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setVerifyingId(id);
    try {
      const updated = await apiPost(`/api/findings/${id}/retest`);
      setFindings((prev) => prev.map((f) => (f.id === id ? updated : f)));
      if (selectedFinding?.id === id) setSelectedFinding(updated);
    } catch {
      // Ignore
    } finally {
      setVerifyingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search & Stats Strip */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search findings by title, endpoint, or code..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="text-rose-400 font-bold">
            {findings.filter((f) => f.severity === "Critical").length} Critical
          </span>
          <span className="text-orange-400 font-bold">
            {findings.filter((f) => f.severity === "High").length} High
          </span>
          <span className="text-emerald-400 font-bold">
            {findings.filter((f) => f.status === "Verified").length} Verified
          </span>
        </div>
      </div>

      {/* Findings Table */}
      <Card title={`Vulnerability Findings (${findings.length})`} subtitle="Independently tested against VoyageSim synthetic platform">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                <th className="pb-3">Code</th>
                <th className="pb-3">Title</th>
                <th className="pb-3">Severity</th>
                <th className="pb-3">Confidence</th>
                <th className="pb-3">Affected Endpoint</th>
                <th className="pb-3">Tenant Scope</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {findings.map((f) => (
                <tr
                  key={f.id}
                  onClick={() => setSelectedFinding(f)}
                  className="hover:bg-slate-800/40 cursor-pointer transition"
                >
                  <td className="py-3 pr-2 font-mono text-[11px] text-cyan-400 font-bold">
                    {f.code}
                  </td>
                  <td className="py-3 pr-3 font-semibold text-slate-200">
                    {f.title}
                  </td>
                  <td className="py-3 pr-3">
                    <Badge label={f.severity} variant="severity" />
                  </td>
                  <td className="py-3 pr-3 font-mono text-slate-300">
                    {f.confidence}%
                  </td>
                  <td className="py-3 pr-3 font-mono text-slate-300 text-[11px]">
                    {f.endpoint}
                  </td>
                  <td className="py-3 pr-3 text-slate-400">
                    {f.tenant || "GlobalTrips B2B"}
                  </td>
                  <td className="py-3 pr-3">
                    <Badge label={f.status} variant="status" />
                  </td>
                  <td className="py-3 text-right space-x-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={(e) => handleVerify(f.id, e)}
                      loading={verifyingId === f.id}
                      icon={<CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                    >
                      Verify
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={(e) => handleRetest(f.id, e)}
                      loading={verifyingId === f.id}
                      icon={<RefreshCw className="w-3.5 h-3.5 text-cyan-400" />}
                    >
                      Retest
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Finding Details Slide-in Drawer */}
      <Drawer
        isOpen={Boolean(selectedFinding)}
        onClose={() => setSelectedFinding(null)}
        title={selectedFinding?.title || "Vulnerability Details"}
        subtitle={`${selectedFinding?.code} · ${selectedFinding?.endpoint}`}
      >
        {selectedFinding && (
          <div className="space-y-5">
            <div className="flex items-center gap-3">
              <Badge label={selectedFinding.severity} variant="severity" />
              <Badge label={selectedFinding.status} variant="status" />
              <span className="text-xs font-mono text-slate-400">
                Confidence: {selectedFinding.confidence}%
              </span>
            </div>

            <div>
              <h4 className="text-[10px] font-mono uppercase text-slate-400 mb-1">
                Affected Endpoint & Tenant
              </h4>
              <p className="font-mono text-xs bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-cyan-300">
                {selectedFinding.endpoint}
              </p>
              <span className="text-xs text-slate-400 mt-1 block">
                Tenant: {selectedFinding.tenant} · Agent: {selectedFinding.agent_name}
              </span>
            </div>

            <div>
              <h4 className="text-[10px] font-mono uppercase text-slate-400 mb-1">
                Business & Financial Impact
              </h4>
              <p className="bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-slate-200 leading-relaxed text-xs">
                {selectedFinding.impact}
              </p>
            </div>

            <div>
              <h4 className="text-[10px] font-mono uppercase text-slate-400 mb-1">
                Sanitized Proof-of-Exploit Evidence
              </h4>
              <pre className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-emerald-400 font-mono text-xs overflow-x-auto whitespace-pre-wrap leading-relaxed">
                {selectedFinding.evidence}
              </pre>
            </div>

            <div>
              <h4 className="text-[10px] font-mono uppercase text-slate-400 mb-1">
                Actionable Remediation Guidance
              </h4>
              <p className="bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-cyan-200 leading-relaxed text-xs">
                {selectedFinding.remediation}
              </p>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[10px] font-mono text-slate-500 uppercase">
                Environment: DEMO / SIMULATED
              </span>
              <div className="flex gap-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleVerify(selectedFinding.id)}
                  loading={verifyingId === selectedFinding.id}
                  icon={<CheckCircle2 className="w-3.5 h-3.5" />}
                >
                  Independently Verify
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleRetest(selectedFinding.id)}
                  loading={verifyingId === selectedFinding.id}
                  icon={<RefreshCw className="w-3.5 h-3.5" />}
                >
                  Execute Retest
                </Button>
              </div>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};
