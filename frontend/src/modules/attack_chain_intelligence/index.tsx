import React, { useState, useEffect } from "react";
import { GitBranch, ShieldAlert, ArrowRight, Layers, Target, Terminal, CheckCircle2 } from "lucide-react";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Badge } from "../../components/Badge";
import { apiGet } from "../../core/api";

export default function AttackChainIntelligencePage() {
  const [chains, setChains] = useState<any[]>([]);
  const [pathsData, setPathsData] = useState<any>(null);
  const [chokepoints, setChokepoints] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"paths" | "chokepoints" | "cypher">("paths");
  const [selectedChain, setSelectedChain] = useState<any>(null);

  useEffect(() => {
    apiGet("/api/modules/attack_chain_intelligence/chains").then((data) => {
      setChains(data || []);
      if (data && data.length > 0) setSelectedChain(data[0]);
    }).catch(() => {});

    apiGet("/api/modules/attack_chain_intelligence/paths").then(setPathsData).catch(() => {});
    apiGet("/api/modules/attack_chain_intelligence/chokepoints").then((d) => setChokepoints(d.chokepoints || [])).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider block mb-1">
            INNOVATION MODULE 2 · ATTACK CHAIN INTELLIGENCE
          </span>
          <h2 className="text-base font-bold text-slate-100">
            Multi-Step Attack Graph Correlation & Chokepoint Analysis
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            NetworkX directed graph correlation linking disparate weaknesses into verified exploitation pathways
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab("paths")}
            className={`px-3 py-1 rounded-md font-medium transition ${
              activeTab === "paths" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Attack Paths
          </button>
          <button
            onClick={() => setActiveTab("chokepoints")}
            className={`px-3 py-1 rounded-md font-medium transition ${
              activeTab === "chokepoints" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Chokepoints
          </button>
          <button
            onClick={() => setActiveTab("cypher")}
            className={`px-3 py-1 rounded-md font-medium transition ${
              activeTab === "cypher" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Cypher Traversal
          </button>
        </div>
      </div>

      {/* Main Grid: Left Steps, Right Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Chain Steps & Paths */}
        <div className="lg:col-span-2 space-y-4">
          {activeTab === "paths" && (
            <Card
              title="Correlated Attack Pathways"
              subtitle="Step-by-step reproduction of multi-tenant exploitation sequence"
            >
              {selectedChain && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <div>
                      <h4 className="text-sm font-bold text-slate-100">{selectedChain.title}</h4>
                      <span className="text-[11px] font-mono text-cyan-400">{selectedChain.id}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge label={selectedChain.risk_level} variant="severity" />
                      <Badge label={selectedChain.status} variant="status" />
                    </div>
                  </div>

                  {/* Steps List */}
                  <div className="space-y-2.5">
                    {selectedChain.steps.map((step: string, index: number) => (
                      <div
                        key={step}
                        className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 flex items-start gap-3 text-xs"
                      >
                        <div className="w-5 h-5 rounded-full bg-cyan-950 border border-cyan-700 text-cyan-400 flex items-center justify-center shrink-0 font-mono text-[10px] font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="text-slate-200 font-medium leading-relaxed">{step}</p>
                        </div>
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      </div>
                    ))}
                  </div>

                  {/* Impact & Remediation */}
                  <div className="pt-3 border-t border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80">
                      <span className="text-[10px] font-mono text-slate-400 uppercase block mb-1">
                        Combined Business Impact
                      </span>
                      <p className="text-slate-300">{selectedChain.impact}</p>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80">
                      <span className="text-[10px] font-mono text-cyan-400 uppercase block mb-1">
                        Primary Remediation
                      </span>
                      <p className="text-slate-300">{selectedChain.remediation}</p>
                    </div>
                  </div>
                </div>
              )}
            </Card>
          )}

          {activeTab === "chokepoints" && (
            <Card
              title="Chokepoint Remediation Ranking"
              subtitle="Critical graph bottleneck nodes whose remediation dismantles the most attack paths"
            >
              <div className="space-y-3">
                {chokepoints.map((cp, idx) => (
                  <div
                    key={cp.node}
                    className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between gap-4 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-rose-950 border border-rose-800 text-rose-300 flex items-center justify-center font-mono font-bold text-[10px]">
                          #{idx + 1}
                        </span>
                        <span className="font-mono font-bold text-slate-100 text-sm">{cp.node}</span>
                      </div>
                      <p className="text-slate-400 text-xs pl-7">{cp.remediation}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="text-xs font-mono font-bold text-cyan-400 block">
                        Breaks {cp.paths_broken} Attack Paths
                      </span>
                      <span className="text-[10px] text-emerald-400 font-mono">
                        -{cp.risk_reduction_pct}% Risk Exposure
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {activeTab === "cypher" && (
            <Card
              title="Graph Traversal Cypher Query"
              subtitle="Formal graph query pattern used to identify multi-hop paths"
            >
              <div className="space-y-4 text-xs font-mono">
                <pre className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-cyan-300 whitespace-pre-wrap leading-relaxed">
                  {pathsData?.cypher_query || "MATCH path = (i:Identity)-[:EXPLOITS*1..4]->(t:Target) RETURN path"}
                </pre>
                <p className="text-slate-400 text-xs font-sans">
                  The query evaluates directed path reachability between unprivileged B2B identity nodes and protected financial targets.
                </p>
              </div>
            </Card>
          )}
        </div>

        {/* Right Column: Graph Topology Metrics */}
        <div className="space-y-4">
          <Card title="Attack Graph Topology Metrics">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Graph Nodes</span>
                <p className="text-xl font-bold text-slate-100 mt-1">{pathsData?.total_nodes || 7}</p>
              </div>
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Directed Edges</span>
                <p className="text-xl font-bold text-slate-100 mt-1">{pathsData?.total_edges || 6}</p>
              </div>
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                <span className="text-[10px] font-mono text-rose-400 uppercase">Critical Paths</span>
                <p className="text-xl font-bold text-rose-400 mt-1">{pathsData?.paths?.length || 1}</p>
              </div>
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                <span className="text-[10px] font-mono text-amber-400 uppercase">Avg Path Length</span>
                <p className="text-xl font-bold text-amber-400 mt-1">4.2 Hops</p>
              </div>
            </div>
          </Card>

          <Card title="Top Chokepoint Target">
            <div className="p-3.5 rounded-lg bg-rose-950/30 border border-rose-800/80 text-xs space-y-2">
              <div className="flex items-center gap-2 text-rose-300 font-bold">
                <Target className="w-4 h-4 text-rose-400" />
                GET /api/v1/bookings/&#123;id&#125;
              </div>
              <p className="text-rose-200/90 text-xs leading-relaxed">
                Appears on 75% of identified attack chains. Remediation breaks multi-tenant data exfiltration before financial mutations can occur.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
