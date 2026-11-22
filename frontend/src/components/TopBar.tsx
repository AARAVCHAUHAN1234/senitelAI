import React from "react";
import { Search, Radio, Sparkles, Shield, User } from "lucide-react";
import { Button } from "./Button";

interface TopBarProps {
  currentTab: string;
  connected: boolean;
  onRunAll: () => void;
  runningAll: boolean;
  onSearchChange: (q: string) => void;
  searchQuery: string;
}

export const TopBar: React.FC<TopBarProps> = ({
  currentTab,
  connected,
  onRunAll,
  runningAll,
  onSearchChange,
  searchQuery
}) => {
  return (
    <header className="h-14 bg-slate-900/90 backdrop-blur-xs border-b border-slate-800 sticky top-0 z-20 px-5 flex items-center justify-between gap-4">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs font-medium">
        <span className="text-slate-400">SentinelAI</span>
        <span className="text-slate-600">/</span>
        <span className="text-cyan-400 font-semibold">{currentTab}</span>
      </div>

      {/* Center Search */}
      <div className="flex-1 max-w-md relative hidden md:block">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Search endpoints, findings, agents, or tenant logs..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full bg-slate-950/60 border border-slate-800 rounded-lg pl-9 pr-3.5 py-1.5 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition font-sans"
        />
      </div>

      {/* Right Actions & Status */}
      <div className="flex items-center gap-3">
        {/* SSE Stream status */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-[11px] font-mono">
          <Radio className={`w-3.5 h-3.5 ${connected ? "text-emerald-400 animate-pulse" : "text-amber-400"}`} />
          <span className={connected ? "text-emerald-300" : "text-amber-300"}>
            {connected ? "LIVE EVENT BUS" : "RECONNECTING"}
          </span>
        </div>

        {/* Mode Pill */}
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-700/60">
          <Shield className="w-3 h-3 text-cyan-400" />
          DEMO / SIMULATED
        </span>

        {/* Run All Scenarios Button */}
        <Button
          variant="primary"
          size="sm"
          onClick={onRunAll}
          loading={runningAll}
          icon={<Sparkles className="w-3.5 h-3.5" />}
        >
          Run Scenarios
        </Button>

        {/* User Chip */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
          <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-200">
            JD
          </div>
          <div className="hidden lg:block text-left">
            <span className="text-xs font-medium text-slate-200 block leading-tight">Jordan Davis</span>
            <span className="text-[10px] text-slate-400 block font-mono">Security Admin</span>
          </div>
        </div>
      </div>
    </header>
  );
};
