import React, { useState, useEffect } from "react";
import { Zap, GitCommit, Layers, ArrowRight, Play, Upload, CheckCircle2, Clock } from "lucide-react";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Badge } from "../../components/Badge";
import { apiGet, apiPost } from "../../core/api";

export default function PredictiveImpactPage() {
  const [changes, setChanges] = useState<any[]>([]);
  const [graphData, setGraphData] = useState<any>(null);
  const [simulating, setSimulating] = useState(false);

  const loadData = async () => {
    try {
      const c = await apiGet("/api/modules/predictive_impact/changes");
      setChanges(c || []);
      const g = await apiGet("/api/modules/predictive_impact/dependency-graph");
      setGraphData(g);
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSimulateDeployment = async () => {
    setSimulating(true);
    try {
      await apiPost("/api/modules/predictive_impact/simulate-deployment", {
        service: "Pricing Service v3.1"
      });
      loadData();
    } catch {
      // Ignore
    } finally {
      setSimulating(false);
    }
  };

  const pipelineStages = graphData?.pipeline_stages || [
    { id: "code", label: "Write code", status: "completed" },
    { id: "push", label: "Push", status: "completed" },
    { id: "ci", label: "CI build & tests", status: "completed" },
    { id: "deploy_staging", label: "Deploy to staging", status: "completed" },
    { id: "dast_scan", label: "DAST scan", status: "active" },
    { id: "decision", label: "Policy gate", status: "pending" },
    { id: "deploy_prod", label: "Deploy to prod", status: "pending" },
    { id: "monitor", label: "Monitor", status: "pending" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider block mb-1">
            INNOVATION MODULE 4 · PREDICTIVE SECURITY IMPACT ENGINE
          </span>
          <h2 className="text-base font-bold text-slate-100">
            Change Impact Analysis & Test Prioritization
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Predicts which endpoints and business workflows code changes impact to focus security testing before execution
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="primary"
            size="sm"
            onClick={handleSimulateDeployment}
            loading={simulating}
            icon={<Play className="w-3.5 h-3.5" />}
          >
            Simulate Deployment Event
          </Button>
        </div>
      </div>

      {/* CI/CD Pipeline Strip (as in ref-07) */}
      <Card title="Automated CI/CD Security Pipeline Pipeline Strip" subtitle="Live advancement across deployment gating checkpoints">
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2">
          {pipelineStages.map((st: any, idx: number) => {
            const isActive = st.status === "active";
            const isCompleted = st.status === "completed";

            return (
              <React.Fragment key={st.id}>
                <div
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-mono font-medium border transition ${
                    isActive
                      ? "bg-cyan-950 text-cyan-300 border-cyan-500 shadow-md shadow-cyan-950/50"
                      : isCompleted
                      ? "bg-slate-900/90 text-emerald-400 border-emerald-900/50"
                      : "bg-slate-950 text-slate-500 border-slate-800/80"
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  ) : isActive ? (
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                  ) : (
                    <Clock className="w-3.5 h-3.5 text-slate-600" />
                  )}
                  <span>{st.label}</span>
                </div>
                {idx < pipelineStages.length - 1 && (
                  <ArrowRight className="w-3 h-3 text-slate-700 hidden sm:block" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </Card>

      {/* Ranked Predicted Risks Table */}
      <Card
        title={`Ranked Predicted Impact Surfaces (${changes.length})`}
        subtitle="Ranked hypotheses combining auth changes, workflow criticality, and regression memory"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                <th className="pb-3">API Surface</th>
                <th className="pb-3">Change Class</th>
                <th className="pb-3">Service</th>
                <th className="pb-3">Risk Priority</th>
                <th className="pb-3">Affected Workflows</th>
                <th className="pb-3">Recommended Security Test</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {changes.map((c) => (
                <tr key={c.id} className="hover:bg-slate-800/30">
                  <td className="py-3 font-mono font-bold text-cyan-400 text-[11px]">
                    {c.endpoint}
                  </td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                      {c.change_type}
                    </span>
                  </td>
                  <td className="py-3 text-slate-300">{c.service}</td>
                  <td className="py-3 font-mono font-bold text-rose-400">
                    {c.risk_priority}/100
                  </td>
                  <td className="py-3 text-slate-300">
                    {Array.isArray(c.affected_workflows) ? c.affected_workflows.join(", ") : c.affected_workflows}
                  </td>
                  <td className="py-3 text-slate-400 max-w-xs">{c.recommended_test}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
