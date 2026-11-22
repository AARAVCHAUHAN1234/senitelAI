import React, { useState } from "react";
import { Bot, Play, Pause, Square, Sparkles, CheckCircle2, AlertCircle } from "lucide-react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Badge } from "../components/Badge";
import { apiPost } from "../core/api";

interface AgentCenterProps {
  agents: any[];
  onRefresh: () => void;
}

export const AgentCenter: React.FC<AgentCenterProps> = ({ agents, onRefresh }) => {
  const [runningAction, setRunningAction] = useState<string | null>(null);

  const handleScanAction = async (action: "start" | "pause" | "resume" | "stop") => {
    setRunningAction(action);
    try {
      await apiPost(`/api/scan/${action}`);
      onRefresh();
    } catch {
      // Ignore
    } finally {
      setRunningAction(null);
    }
  };

  const handleRunAgent = async (agentName: string) => {
    const formatted = agentName.replace(/\s+/g, "_");
    setRunningAction(agentName);
    try {
      await apiPost(`/api/agents/${formatted}/run`);
      onRefresh();
    } catch {
      // Ignore
    } finally {
      setRunningAction(null);
    }
  };

  const runningCount = agents.filter((a) => a.status === "Running").length;
  const completedCount = agents.filter((a) => a.status === "Completed").length;

  return (
    <div className="space-y-6">
      {/* Control Strip */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-100 tracking-tight">
            Autonomous Agent Orchestration Center
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            13 specialized autonomous security agents executing real-time multi-tenant vulnerability checks
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => handleScanAction("pause")}
            loading={runningAction === "pause"}
            icon={<Pause className="w-3.5 h-3.5" />}
          >
            Pause
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => handleScanAction("resume")}
            loading={runningAction === "resume"}
            icon={<Play className="w-3.5 h-3.5" />}
          >
            Resume
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={() => handleScanAction("stop")}
            loading={runningAction === "stop"}
            icon={<Square className="w-3.5 h-3.5" />}
          >
            Stop
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => handleScanAction("start")}
            loading={runningAction === "start"}
            icon={<Sparkles className="w-3.5 h-3.5" />}
          >
            Run Full Assessment
          </Button>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <span className="text-[10px] font-mono text-slate-400 uppercase">Total Agents</span>
          <p className="text-xl font-bold text-slate-100">{agents.length}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <span className="text-[10px] font-mono text-cyan-400 uppercase">Running</span>
          <p className="text-xl font-bold text-cyan-400">{runningCount}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <span className="text-[10px] font-mono text-emerald-400 uppercase">Completed</span>
          <p className="text-xl font-bold text-emerald-400">{completedCount}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
          <span className="text-[10px] font-mono text-slate-400 uppercase">Total Tests</span>
          <p className="text-xl font-bold text-slate-100">
            {agents.reduce((acc, a) => acc + (a.tests_completed || 0), 0)}
          </p>
        </div>
      </div>

      {/* Agents Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => {
          const isRunning = agent.status === "Running";
          const isBusy = runningAction === agent.name;

          return (
            <div
              key={agent.id}
              className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition"
            >
              <div>
                <div className="flex items-center justify-between mb-2.5">
                  <div className="w-8 h-8 rounded-lg bg-cyan-950/60 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
                    <Bot className="w-4 h-4" />
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium ${
                      isRunning
                        ? "bg-cyan-950 text-cyan-300 border border-cyan-700 animate-pulse"
                        : agent.status === "Completed"
                        ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {agent.status}
                  </span>
                </div>

                <h3 className="font-semibold text-slate-200 text-sm">{agent.name}</h3>
                <p className="text-xs text-slate-400 mt-1 min-h-[32px] line-clamp-2">
                  {agent.task || "Standing by for autonomous execution"}
                </p>

                {/* Progress Bar */}
                <div className="mt-3">
                  <div className="flex justify-between text-[10px] font-mono text-slate-400 mb-1">
                    <span>Progress</span>
                    <span>{agent.progress || 0}%</span>
                  </div>
                  <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-cyan-500 h-full rounded-full transition-all duration-300"
                      style={{ width: `${agent.progress || 0}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="flex items-center justify-between pt-3 mt-4 border-t border-slate-800/80 text-xs text-slate-400">
                <span className="font-mono text-[11px]">
                  {agent.tests_completed || 0} tests · {agent.findings_generated || 0} findings
                </span>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleRunAgent(agent.name)}
                  loading={isBusy}
                  disabled={isRunning}
                  icon={<Play className="w-3 h-3 text-cyan-400" />}
                >
                  Run Agent
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
