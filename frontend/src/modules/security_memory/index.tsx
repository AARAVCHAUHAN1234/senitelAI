import React, { useState, useEffect } from "react";
import { Database, ShieldCheck, History, AlertTriangle, ArrowUpRight, TrendingUp } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  AreaChart,
  Area
} from "recharts";
import { Card } from "../../components/Card";
import { MetricCard } from "../../components/MetricCard";
import { Badge } from "../../components/Badge";
import { apiGet } from "../../core/api";

export default function SecurityMemoryPage() {
  const [kpis, setKpis] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [trends, setTrends] = useState<any>(null);

  useEffect(() => {
    apiGet("/api/modules/security_memory/kpis").then(setKpis).catch(() => {});
    apiGet("/api/modules/security_memory/history").then(setHistory).catch(() => {});
    apiGet("/api/modules/security_memory/remediation-trends").then(setTrends).catch(() => {});
  }, []);

  const openOverTime = trends?.open_findings_over_time || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider block mb-1">
            INNOVATION MODULE 5 · SECURITY MEMORY
          </span>
          <h2 className="text-base font-bold text-slate-100">
            Historical Context, Regressions & Remediation Memory
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Maintains cross-assessment memory to boost test priority on historically vulnerable surfaces and detect regressions
          </p>
        </div>
      </div>

      {/* KPI Row (as in ref-08) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Open Findings"
          value={kpis?.total_open_findings || 4}
          subtext={`${kpis?.critical_high_open || 4} Critical / High`}
          icon={<AlertTriangle className="w-4 h-4" />}
          accentColor="text-rose-400"
        />
        <MetricCard
          label="Mitigated in SLA"
          value={`${kpis?.mitigated_within_sla_pct || 87.5}%`}
          subtext="Target SLA: 90%"
          icon={<ShieldCheck className="w-4 h-4" />}
          accentColor="text-emerald-400"
        />
        <MetricCard
          label="Historical Regressions"
          value={kpis?.historical_regressions || 2}
          subtext="Remediated flaws re-detected"
          icon={<History className="w-4 h-4" />}
          accentColor="text-amber-400"
        />
        <MetricCard
          label="Pattern Clusters"
          value={kpis?.patterns_tracked || 5}
          subtext="Recurring root causes tracked"
          icon={<Database className="w-4 h-4" />}
          accentColor="text-cyan-400"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Open Findings Over Time */}
        <Card title="Historical Findings Trajectory" subtitle="Open findings by severity over past 7 cycles">
          <div className="h-60 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={openOverTime} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" vertical={false} />
                <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "#f8fafc"
                  }}
                />
                <Area type="monotone" dataKey="Critical" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} />
                <Area type="monotone" dataKey="High" stackId="1" stroke="#f97316" fill="#f97316" fillOpacity={0.6} />
                <Area type="monotone" dataKey="Medium" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Time to Remediation by Severity (strictly valid positive hours) */}
        <Card title="Average Time to Remediation (Hours)" subtitle="Computed strictly from valid non-negative event timestamps">
          <div className="space-y-4 pt-3 text-xs">
            {trends?.averages_hours &&
              Object.entries(trends.averages_hours).map(([sev, hrs]: any) => (
                <div key={sev} className="space-y-1">
                  <div className="flex justify-between font-mono">
                    <span className="text-slate-300 font-semibold">{sev} Severity</span>
                    <span className="text-cyan-400 font-bold">{hrs} Hours</span>
                  </div>
                  <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-cyan-500 h-full rounded-full"
                      style={{ width: `${Math.min(100, (hrs / 80) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </Card>
      </div>

      {/* Regressions and Historical Records Table */}
      <Card title="Historical Findings & Regressions Ledger" subtitle="Cross-assessment memory log">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                <th className="pb-3">Code</th>
                <th className="pb-3">Title</th>
                <th className="pb-3">Severity</th>
                <th className="pb-3">Pattern Cluster</th>
                <th className="pb-3">Event Type</th>
                <th className="pb-3">Regression</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {history.map((rec) => (
                <tr key={rec.id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 font-mono text-cyan-400 font-bold">{rec.finding_code}</td>
                  <td className="py-2.5 font-semibold text-slate-200">{rec.title}</td>
                  <td className="py-2.5">
                    <Badge label={rec.severity} variant="severity" />
                  </td>
                  <td className="py-2.5 text-slate-300">{rec.cluster_pattern}</td>
                  <td className="py-2.5 font-mono text-slate-400">{rec.event_type}</td>
                  <td className="py-2.5">
                    {rec.is_regression ? (
                      <span className="px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-rose-950 text-rose-300 border border-rose-800">
                        Regression Detected
                      </span>
                    ) : (
                      <span className="text-slate-500 font-mono text-[10px]">Baseline</span>
                    )}
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
