import React, { useState, useEffect } from "react";
import { Download, FileText, ShieldCheck, Printer, CheckCircle2 } from "lucide-react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Badge } from "../components/Badge";
import { apiGet, API_BASE } from "../core/api";

export const Reports: React.FC = () => {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    apiGet("/api/reports")
      .then(setReport)
      .finally(() => setLoading(false));
  }, []);

  const handlePrint = () => {
    window.open(`${API_BASE}/api/reports/pdf`, "_blank");
  };

  const handleDownloadJson = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sentinelai-security-report-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header Strip */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider block mb-1">
            DAST ASSESSMENT ARTIFACT · DEMO / SIMULATED
          </span>
          <h2 className="text-base font-bold text-slate-100">
            Travel Platform Security Audit Report
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Target: VoyageSim B2B Platform · Generated: {report?.generated_at ? new Date(report.generated_at).toLocaleString() : "Live"}
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleDownloadJson}
            icon={<Download className="w-3.5 h-3.5" />}
          >
            Export JSON
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handlePrint}
            icon={<Printer className="w-3.5 h-3.5" />}
          >
            Print / Save PDF
          </Button>
        </div>
      </div>

      {/* Executive Summary Card */}
      <Card title="Executive Summary">
        <p className="text-sm text-slate-300 leading-relaxed">
          {report?.executive_summary}
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5 pt-4 border-t border-slate-800">
          <div>
            <span className="text-[10px] font-mono text-slate-400 uppercase">Total Discovered APIs</span>
            <p className="text-xl font-bold text-slate-100 mt-0.5">{report?.metrics?.total_apis || 0}</p>
          </div>
          <div>
            <span className="text-[10px] font-mono text-slate-400 uppercase">Total Findings</span>
            <p className="text-xl font-bold text-slate-100 mt-0.5">{report?.metrics?.vulnerabilities || 0}</p>
          </div>
          <div>
            <span className="text-[10px] font-mono text-rose-400 uppercase">Critical Severity</span>
            <p className="text-xl font-bold text-rose-400 mt-0.5">{report?.metrics?.critical || 0}</p>
          </div>
          <div>
            <span className="text-[10px] font-mono text-emerald-400 uppercase">Independently Verified</span>
            <p className="text-xl font-bold text-emerald-400 mt-0.5">{report?.metrics?.verified || 0}</p>
          </div>
        </div>
      </Card>

      {/* Verified Findings in Report */}
      <Card title="Detailed Verified Findings in Scope">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                <th className="pb-3">Code</th>
                <th className="pb-3">Title</th>
                <th className="pb-3">Severity</th>
                <th className="pb-3">Affected Endpoint</th>
                <th className="pb-3">Tenant Scope</th>
                <th className="pb-3">Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(report?.findings || []).map((f: any) => (
                <tr key={f.id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 font-mono text-cyan-400 font-bold">{f.code}</td>
                  <td className="py-2.5 font-semibold text-slate-200">{f.title}</td>
                  <td className="py-2.5">
                    <Badge label={f.severity} variant="severity" />
                  </td>
                  <td className="py-2.5 font-mono text-slate-300">{f.endpoint}</td>
                  <td className="py-2.5 text-slate-400">{f.tenant}</td>
                  <td className="py-2.5">
                    <Badge label={f.status} variant="status" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
