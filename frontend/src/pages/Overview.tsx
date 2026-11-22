import React from "react";
import {
  Globe,
  ShieldCheck,
  AlertTriangle,
  Gauge,
  Bot,
  Play,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Cpu
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell
} from "recharts";
import { Card } from "../components/Card";
import { MetricCard } from "../components/MetricCard";
import { Badge } from "../components/Badge";
import { Button } from "../components/Button";

interface OverviewProps {
  data: any;
  onNavigate: (tab: string) => void;
  onRunScenario: (key: string) => void;
  onRunAll: () => void;
  busy: boolean;
}

const SEVERITY_COLORS: Record<string, string> = {
  Critical: "#ef4444",
  High: "#f97316",
  Medium: "#f59e0b",
  Low: "#10b981",
  Informational: "#64748b"
};

export const Overview: React.FC<OverviewProps> = ({
  data,
  onNavigate,
  onRunScenario,
  onRunAll,
  busy
}) => {
  const metrics = data?.metrics || {};
  const severityDist = data?.severity || [];
  const activityData = data?.activity || [];
  const recentFindings = data?.findings || [];
  const agents = data?.agents || [];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 rounded-2xl p-6 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 font-semibold mb-1">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            AUTONOMOUS DAST ACTIVE · MULTI-TENANT TRAVEL SOC
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-100 tracking-tight">
            Travel Platform Security Posture
          </h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1 max-w-2xl">
            Continuous real-time security assessment protecting 3 B2B agency tenants against IDOR,
            fare tampering, duplicate refunds, and multi-step attack chains.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button
            variant="secondary"
            size="md"
            onClick={() => onRunScenario("idor")}
            disabled={busy}
            icon={<Play className="w-4 h-4 text-cyan-400" />}
          >
            Start IDOR Test
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={onRunAll}
            disabled={busy}
            icon={<Sparkles className="w-4 h-4" />}
          >
            Run All Scenarios
          </Button>
        </div>
      </div>

      {/* Critical Alert Strip if critical findings exist */}
      {metrics.critical > 0 && (
        <div className="bg-rose-950/40 border border-rose-800/80 rounded-xl p-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-rose-900/60 text-rose-300">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-rose-200">
                {metrics.critical} Critical Vulnerabilities Require Immediate Remediation
              </h4>
              <p className="text-xs text-rose-300/80 mt-0.5">
                Cross-tenant IDOR enables Agency A accounts to exfiltrate passenger booking metadata.
              </p>
            </div>
          </div>
          <Button
            variant="danger"
            size="sm"
            onClick={() => onNavigate("Vulnerability Findings")}
          >
            Review Findings
          </Button>
        </div>
      )}

      {/* Key Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="APIs Discovered"
          value={metrics.total_apis ?? 0}
          subtext={`Active: ${metrics.active_apis ?? 0} · Zombie: ${metrics.zombie_apis ?? 0} · Shadow: ${metrics.shadow_apis ?? 0}`}
          icon={<Globe className="w-4 h-4" />}
          accentColor="text-cyan-400"
          trend="+2 New"
        />
        <MetricCard
          label="Verified Findings"
          value={metrics.verified ?? 0}
          subtext="Independently reproduced in sandbox"
          icon={<ShieldCheck className="w-4 h-4" />}
          accentColor="text-emerald-400"
        />
        <MetricCard
          label="Critical & High"
          value={(metrics.critical ?? 0) + (metrics.high ?? 0)}
          subtext={`${metrics.critical ?? 0} Critical · ${metrics.high ?? 0} High`}
          icon={<AlertTriangle className="w-4 h-4" />}
          accentColor="text-rose-400"
        />
        <MetricCard
          label="Security Risk Score"
          value={`${metrics.risk_score ?? 75}/100`}
          subtext="Elevated multi-tenant risk"
          icon={<Gauge className="w-4 h-4" />}
          accentColor="text-amber-400"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Real-Time Security Activity Graph */}
        <div className="lg:col-span-2">
          <Card
            title="Real-Time Security Activity Stream"
            subtitle="Autonomous agent executions, test verifications, and state mutations"
            action={
              <span className="flex items-center gap-1.5 text-xs font-mono text-cyan-400 font-semibold">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                STREAMING
              </span>
            }
          >
            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={activityData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="eventColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" vertical={false} />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={10} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#334155",
                      borderRadius: "8px",
                      fontSize: "12px",
                      color: "#f8fafc"
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#06b6d4"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#eventColor)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        {/* Severity Distribution Donut Chart */}
        <div>
          <Card
            title="Vulnerability Severity Distribution"
            subtitle="Current open verified findings"
            action={
              <button
                onClick={() => onNavigate("Vulnerability Findings")}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-medium inline-flex items-center gap-1"
              >
                All Findings <ArrowRight className="w-3 h-3" />
              </button>
            }
          >
            <div className="h-44 flex items-center justify-center relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityDist}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={4}
                    stroke="none"
                  >
                    {severityDist.map((entry: any) => (
                      <Cell key={entry.name} fill={SEVERITY_COLORS[entry.name] || "#64748b"} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#334155",
                      borderRadius: "8px",
                      fontSize: "12px",
                      color: "#f8fafc"
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute flex flex-col items-center justify-center pointer-events-none">
                <span className="text-xl font-bold text-slate-100">{metrics.vulnerabilities ?? 0}</span>
                <span className="text-[10px] text-slate-400 uppercase font-mono tracking-wider">Total</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-slate-800 text-xs">
              {severityDist.map((item: any) => (
                <div key={item.name} className="flex items-center justify-between text-slate-300">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: SEVERITY_COLORS[item.name] }} />
                    <span>{item.name}</span>
                  </div>
                  <span className="font-mono font-semibold">{item.value}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Lower Row: Recent Verified Findings & Autonomous Agents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Findings Table */}
        <div className="lg:col-span-2">
          <Card
            title="Recent Verified Security Findings"
            subtitle="Independently tested against VoyageSim synthetic platform"
            action={
              <button
                onClick={() => onNavigate("Vulnerability Findings")}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-medium inline-flex items-center gap-1"
              >
                View all ({metrics.vulnerabilities ?? 0}) <ArrowRight className="w-3 h-3" />
              </button>
            }
          >
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                    <th className="pb-2.5">Finding</th>
                    <th className="pb-2.5">Severity</th>
                    <th className="pb-2.5">Endpoint</th>
                    <th className="pb-2.5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {recentFindings.slice(0, 5).map((f: any) => (
                    <tr
                      key={f.id}
                      onClick={() => onNavigate("Vulnerability Findings")}
                      className="hover:bg-slate-800/40 cursor-pointer transition"
                    >
                      <td className="py-2.5 pr-3">
                        <span className="font-semibold text-slate-200 block">{f.title}</span>
                        <span className="font-mono text-[10px] text-slate-400">{f.code}</span>
                      </td>
                      <td className="py-2.5 pr-3">
                        <Badge label={f.severity} variant="severity" />
                      </td>
                      <td className="py-2.5 pr-3 font-mono text-slate-300 text-[11px]">
                        {f.endpoint}
                      </td>
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

        {/* Autonomous Agents Status Card */}
        <div>
          <Card
            title="Autonomous Agents Activity"
            subtitle={`${metrics.agents_running ?? 0} active security agents`}
            action={
              <button
                onClick={() => onNavigate("Agent Control Center")}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-medium inline-flex items-center gap-1"
              >
                Control Center <ArrowRight className="w-3 h-3" />
              </button>
            }
          >
            <div className="space-y-3">
              {agents.slice(0, 5).map((agent: any) => (
                <div
                  key={agent.id}
                  className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-800/60 flex items-center justify-between gap-3 text-xs"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="w-7 h-7 rounded-md bg-cyan-950/60 border border-cyan-800/50 flex items-center justify-center text-cyan-400 shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="truncate">
                      <span className="font-medium text-slate-200 block truncate">{agent.name}</span>
                      <span className="text-[10px] text-slate-400 block truncate">{agent.task || "Standing by"}</span>
                    </div>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium ${
                      agent.status === "Running"
                        ? "bg-cyan-950 text-cyan-300 border border-cyan-700 animate-pulse"
                        : agent.status === "Completed"
                        ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {agent.status}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
