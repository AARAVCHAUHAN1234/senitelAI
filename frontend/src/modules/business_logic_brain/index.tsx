import React, { useState, useEffect } from "react";
import { Workflow, Play, ShieldCheck, AlertTriangle, ArrowRight, Layers, DollarSign, Users, CheckCircle2, XCircle } from "lucide-react";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Badge } from "../../components/Badge";
import { Drawer } from "../../components/Drawer";
import { apiGet, apiPost } from "../../core/api";

export default function BusinessLogicBrainPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [viewMode, setViewMode] = useState<"linear" | "swimlane" | "money_flow">("linear");
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [runningTests, setRunningTests] = useState(false);

  const loadData = async () => {
    try {
      const wData = await apiGet("/api/modules/business_logic_brain/workflows");
      setWorkflows(wData.workflows || []);
      const rData = await apiGet("/api/modules/business_logic_brain/results");
      setResults(rData || []);
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunAllTests = async () => {
    setRunningTests(true);
    try {
      await apiPost("/api/modules/business_logic_brain/run-tests");
      loadData();
    } catch {
      // Ignore
    } finally {
      setRunningTests(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls Strip */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider block mb-1">
            INNOVATION MODULE 1 · BUSINESS LOGIC BRAIN
          </span>
          <h2 className="text-base font-bold text-slate-100">
            Workflow State Machines & Security Invariants
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Formal state machine verification enforcing non-bypassable travel booking, payment, and refund invariants
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Switchable views */}
          <div className="flex items-center rounded-lg bg-slate-950 p-1 border border-slate-800 text-xs">
            <button
              onClick={() => setViewMode("linear")}
              className={`px-3 py-1 rounded-md font-medium transition ${
                viewMode === "linear" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Linear Flow
            </button>
            <button
              onClick={() => setViewMode("swimlane")}
              className={`px-3 py-1 rounded-md font-medium transition ${
                viewMode === "swimlane" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Actor Swimlane
            </button>
            <button
              onClick={() => setViewMode("money_flow")}
              className={`px-3 py-1 rounded-md font-medium transition ${
                viewMode === "money_flow" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Money Flow
            </button>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={handleRunAllTests}
            loading={runningTests}
            icon={<Play className="w-3.5 h-3.5" />}
          >
            Execute Invariants
          </Button>
        </div>
      </div>

      {/* View Mode 1: Linear Workflow Flow (Pastel rounded workflow cards) */}
      {viewMode === "linear" && (
        <Card title="Linear State Transitions" subtitle="Click any state node to inspect formal invariants and test logs">
          <div className="space-y-6">
            {workflows.map((wf) => (
              <div key={wf.id} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-semibold text-slate-200 text-sm">{wf.name} Lifecycle</span>
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="text-slate-400">{wf.tests_generated} generated tests</span>
                    {wf.violations > 0 ? (
                      <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 font-bold border border-rose-800">
                        {wf.violations} Invariant Violations
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 font-bold border border-emerald-800">
                        All Invariants Valid
                      </span>
                    )}
                  </div>
                </div>

                {/* State Transition Sequence */}
                <div className="flex flex-wrap items-center gap-2 pt-2">
                  {wf.states.map((state: string, idx: number) => {
                    const isViolated = wf.violations > 0 && (state === "Held" || state === "Refunded");
                    return (
                      <React.Fragment key={state}>
                        <button
                          onClick={() => setSelectedNode({ workflow: wf.name, state, rules: wf.rules, isViolated })}
                          className={`px-4 py-2 rounded-xl text-xs font-medium border transition flex items-center gap-2 ${
                            isViolated
                              ? "bg-rose-950/60 text-rose-200 border-rose-600 shadow-md shadow-rose-950/40"
                              : "bg-slate-900 text-slate-200 border-slate-700 hover:border-cyan-500 hover:bg-slate-800"
                          }`}
                        >
                          <span
                            className={`w-2 h-2 rounded-full ${
                              isViolated ? "bg-rose-500 animate-ping" : "bg-cyan-400"
                            }`}
                          />
                          {state}
                        </button>
                        {idx < wf.states.length - 1 && (
                          <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* View Mode 2: Actor Swimlane */}
      {viewMode === "swimlane" && (
        <Card title="Actor Swimlane Workflow Decomposition" subtitle="Multi-tier interactions across Traveller, API Gateway, and B2B Partner">
          <div className="space-y-4 text-xs font-mono">
            <div className="grid grid-cols-5 gap-2 p-2 bg-slate-950 rounded-lg text-slate-400 font-bold text-center">
              <div>1. Search</div>
              <div>2. Price Quote</div>
              <div>3. Book & Hold</div>
              <div>4. Ticket Issue</div>
              <div>5. Confirmation</div>
            </div>

            {/* Swimlane 1: Traveller / B2B Sub-agent */}
            <div className="p-3.5 bg-slate-950/40 rounded-xl border border-slate-800 flex items-center gap-4">
              <span className="w-28 text-cyan-400 font-semibold shrink-0">B2B Agent</span>
              <div className="flex-1 grid grid-cols-5 gap-2 text-center text-slate-300">
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Flight Query</div>
                <div className="p-2 bg-slate-900 rounded border border-rose-800/80 text-rose-300">
                  Fare Modification
                </div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Booking Intent</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800 opacity-40">—</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Receive Voucher</div>
              </div>
            </div>

            {/* Swimlane 2: API Gateway */}
            <div className="p-3.5 bg-slate-950/40 rounded-xl border border-slate-800 flex items-center gap-4">
              <span className="w-28 text-amber-400 font-semibold shrink-0">API Gateway</span>
              <div className="flex-1 grid grid-cols-5 gap-2 text-center text-slate-300">
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Route Request</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Unverified Header</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Session Guard</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Settlement Call</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Emit Invoice</div>
              </div>
            </div>

            {/* Swimlane 3: Core Settlement & Partner */}
            <div className="p-3.5 bg-slate-950/40 rounded-xl border border-slate-800 flex items-center gap-4">
              <span className="w-28 text-emerald-400 font-semibold shrink-0">Airline Partner</span>
              <div className="flex-1 grid grid-cols-5 gap-2 text-center text-slate-300">
                <div className="p-2 bg-slate-900 rounded border border-slate-800">GDS Availability</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Net Fare Lock</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">PNR Allocation</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">E-Ticket Issuance</div>
                <div className="p-2 bg-slate-900 rounded border border-slate-800">Manifest Sync</div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* View Mode 3: Money Flow */}
      {viewMode === "money_flow" && (
        <Card title="Financial Money-Flow Invariants" subtitle="Supplier Net Fare + Agency Markup vs Wallet Settlement Balance">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] font-mono text-cyan-400 uppercase">1. Supplier Net Fare</span>
              <p className="text-xl font-bold text-slate-100 mt-1">$450.00 USD</p>
              <span className="text-[10px] text-slate-400 mt-1 block">Contracted airline base rate</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] font-mono text-emerald-400 uppercase">2. Agency Markup (+15%)</span>
              <p className="text-xl font-bold text-emerald-400 mt-1">+$67.50 USD</p>
              <span className="text-[10px] text-slate-400 mt-1 block">B2B commercial commission</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] font-mono text-amber-400 uppercase">3. Customer Total Paid</span>
              <p className="text-xl font-bold text-amber-400 mt-1">$517.50 USD</p>
              <span className="text-[10px] text-slate-400 mt-1 block">Paid via B2B agency wallet</span>
            </div>
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800">
              <span className="text-[10px] font-mono text-rose-300 uppercase">4. Violated Fare Attack</span>
              <p className="text-xl font-bold text-rose-400 mt-1">$1.00 USD</p>
              <span className="text-[10px] text-rose-300 mt-1 block">Tampered client payload accepted!</span>
            </div>
          </div>
        </Card>
      )}

      {/* Evaluated Rules & Generated Tests Table */}
      <Card title="Business Invariant Evaluation Ledger" subtitle="Deterministic rule verification executed against live endpoints">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                <th className="pb-3">Workflow</th>
                <th className="pb-3">Rule Evaluated</th>
                <th className="pb-3">Test Name</th>
                <th className="pb-3">Result</th>
                <th className="pb-3">Business Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {results.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 font-bold text-slate-200">{r.workflow_name}</td>
                  <td className="py-2.5 text-slate-300 max-w-xs">{r.invariant_rule}</td>
                  <td className="py-2.5 font-mono text-[11px] text-cyan-400">{r.test_name}</td>
                  <td className="py-2.5">
                    {r.result === "Violated" ? (
                      <Badge label="Violated" variant="severity" />
                    ) : (
                      <Badge label="Passed" variant="status" />
                    )}
                  </td>
                  <td className="py-2.5 text-slate-400">{r.business_impact}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Node Details Drawer */}
      <Drawer
        isOpen={Boolean(selectedNode)}
        onClose={() => setSelectedNode(null)}
        title={selectedNode ? `${selectedNode.workflow} · ${selectedNode.state}` : ""}
        subtitle="Formal Invariants and Evaluated State Rules"
      >
        {selectedNode && (
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-[10px] font-mono text-slate-400 uppercase block mb-1">State Invariants</span>
              <ul className="list-disc list-inside space-y-1 text-slate-300 text-xs">
                {selectedNode.rules?.map((rule: string) => (
                  <li key={rule}>{rule}</li>
                ))}
              </ul>
            </div>

            {selectedNode.isViolated && (
              <div className="p-3 rounded-lg bg-rose-950/50 border border-rose-800 text-rose-200 text-xs space-y-1">
                <span className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                  Invariant Violation Detected
                </span>
                <p>
                  Observed state transition allowed duplicate liquidation or parameter tampering without enforcing
                  atomic signed rules.
                </p>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
}
