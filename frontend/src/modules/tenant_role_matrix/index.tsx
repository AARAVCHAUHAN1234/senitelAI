import React, { useState, useEffect } from "react";
import { Users, Check, X, AlertTriangle, Shield, Play, Download, Search } from "lucide-react";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Badge } from "../../components/Badge";
import { Drawer } from "../../components/Drawer";
import { apiGet, apiPost, API_BASE } from "../../core/api";

export default function TenantRoleMatrixPage() {
  const [matrixData, setMatrixData] = useState<any>(null);
  const [selectedTenant, setSelectedTenant] = useState("Agency A");
  const [selectedCell, setSelectedCell] = useState<any>(null);
  const [running, setRunning] = useState(false);

  const loadMatrix = async (tenant: string) => {
    try {
      const data = await apiGet(`/api/modules/tenant_role_matrix/matrix?tenant=${encodeURIComponent(tenant)}`);
      setMatrixData(data);
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    loadMatrix(selectedTenant);
  }, [selectedTenant]);

  const handleRunFull = async () => {
    setRunning(true);
    try {
      await apiPost("/api/modules/tenant_role_matrix/run-full");
      loadMatrix(selectedTenant);
    } catch {
      // Ignore
    } finally {
      setRunning(false);
    }
  };

  const handleExportCsv = () => {
    window.open(`${API_BASE}/api/modules/tenant_role_matrix/export-csv`, "_blank");
  };

  const roles = matrixData?.roles || ["Administrator", "Manager", "Agent", "Sub-agent", "Read-only"];
  const cells = matrixData?.cells || [];

  return (
    <div className="space-y-6">
      {/* Header Strip */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider block mb-1">
            INNOVATION MODULE 3 · TENANT & ROLE MATRIX
          </span>
          <h2 className="text-base font-bold text-slate-100">
            Cross-Tenant & Role Authorization Audit Matrix
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Systematic expected vs actual permission evaluation highlighting unauthorized privilege escalations and IDOR leakage
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Tenant Switcher */}
          <div className="flex items-center rounded-lg bg-slate-950 p-1 border border-slate-800 text-xs">
            {["Agency A", "Agency B", "Agency C"].map((t) => (
              <button
                key={t}
                onClick={() => setSelectedTenant(t)}
                className={`px-3 py-1 rounded-md font-medium transition ${
                  selectedTenant === t ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={handleExportCsv}
            icon={<Download className="w-3.5 h-3.5" />}
          >
            Export CSV
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleRunFull}
            loading={running}
            icon={<Play className="w-3.5 h-3.5" />}
          >
            Run Full Matrix
          </Button>
        </div>
      </div>

      {/* Matrix Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <span className="text-[10px] font-mono text-slate-400 uppercase">Coverage</span>
          <p className="text-xl font-bold text-cyan-400 mt-0.5">{matrixData?.coverage_pct || 0}%</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <span className="text-[10px] font-mono text-slate-400 uppercase">Evaluated Cells</span>
          <p className="text-xl font-bold text-slate-100 mt-0.5">{matrixData?.total_evaluated || 0}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <span className="text-[10px] font-mono text-rose-400 uppercase">Mismatches</span>
          <p className="text-xl font-bold text-rose-400 mt-0.5">{matrixData?.mismatches || 0}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <span className="text-[10px] font-mono text-emerald-400 uppercase">Tenants Scoped</span>
          <p className="text-xl font-bold text-emerald-400 mt-0.5">3 Active</p>
        </div>
      </div>

      {/* Permissions Matrix Table */}
      <Card
        title={`Authorization Matrix for ${selectedTenant}`}
        subtitle="Click any cell to inspect expected vs observed execution tokens and evidence"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                <th className="pb-3 w-48">Resource / Operation</th>
                {roles.map((r: string) => (
                  <th key={r} className="pb-3 text-center">
                    {r}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {cells.map((cell: any) => {
                const isMismatch = cell.result !== "Allowed" && cell.result !== "Denied";
                const isDenied = cell.result === "Denied";

                return (
                  <tr
                    key={cell.id}
                    onClick={() => setSelectedCell(cell)}
                    className="hover:bg-slate-800/30 cursor-pointer transition"
                  >
                    <td className="py-3 font-semibold text-slate-200">
                      {cell.resource}
                    </td>
                    <td colSpan={roles.length} className="py-3">
                      <div className="flex items-center justify-between px-4 py-1.5 rounded-lg bg-slate-950/60 border border-slate-800">
                        <span className="font-mono text-slate-400 text-[11px]">Role: {cell.role}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-[11px] text-slate-400">
                            Expected: <b className="text-slate-200">{cell.expected}</b>
                          </span>
                          <span className="text-[11px] text-slate-400">
                            Observed: <b className={isMismatch ? "text-rose-400" : "text-emerald-400"}>{cell.actual}</b>
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                              isMismatch
                                ? "bg-rose-950 text-rose-300 border border-rose-700 animate-pulse"
                                : isDenied
                                ? "bg-slate-800 text-slate-400"
                                : "bg-emerald-950 text-emerald-300 border border-emerald-800"
                            }`}
                          >
                            {cell.result}
                          </span>
                        </div>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Cell Evidence Drawer */}
      <Drawer
        isOpen={Boolean(selectedCell)}
        onClose={() => setSelectedCell(null)}
        title={selectedCell ? `${selectedCell.tenant} · ${selectedCell.role}` : ""}
        subtitle={selectedCell?.resource}
      >
        {selectedCell && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Expected Access</span>
                <p className="font-bold text-slate-200 mt-1">{selectedCell.expected}</p>
              </div>
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Observed Access</span>
                <p
                  className={`font-bold mt-1 ${
                    selectedCell.result !== "Allowed" && selectedCell.result !== "Denied"
                      ? "text-rose-400"
                      : "text-emerald-400"
                  }`}
                >
                  {selectedCell.actual}
                </p>
              </div>
            </div>

            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs">
              <span className="text-[10px] font-mono text-cyan-400 uppercase block mb-1">
                Authorization Test Evidence
              </span>
              <p className="text-slate-300 leading-relaxed font-mono text-[11px]">{selectedCell.evidence}</p>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
