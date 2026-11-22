import React from "react";
import {
  LayoutDashboard,
  Network,
  Bot,
  Globe,
  ShieldAlert,
  Workflow,
  GitBranch,
  Users,
  Zap,
  Database,
  LockKeyhole,
  FileText,
  Terminal,
  Settings as SettingsIcon,
  ChevronLeft,
  ChevronRight,
  ShieldCheck
} from "lucide-react";

export interface NavItem {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

export const navSections: NavSection[] = [
  {
    title: "COMMAND & SURFACE",
    items: [
      { id: "Overview", name: "Overview", icon: LayoutDashboard },
      { id: "Live Security Graph", name: "Live Security Graph", icon: Network },
      { id: "Agent Control Center", name: "Agent Control Center", icon: Bot },
      { id: "API Discovery", name: "API Discovery", icon: Globe },
      { id: "Vulnerability Findings", name: "Findings", icon: ShieldAlert }
    ]
  },
  {
    title: "SECURITY INTELLIGENCE",
    items: [
      { id: "Business Logic Intelligence", name: "Business Logic Brain", icon: Workflow },
      { id: "Attack Chain Intelligence", name: "Attack Chains", icon: GitBranch },
      { id: "Tenant & Role Matrix", name: "Tenant & Role Matrix", icon: Users },
      { id: "Predictive Security Impact", name: "Predictive Impact", icon: Zap },
      { id: "Security Memory", name: "Security Memory", icon: Database }
    ]
  },
  {
    title: "OPERATIONS & SYSTEM",
    items: [
      { id: "Safe Attack Sandbox", name: "Safe Attack Sandbox", icon: LockKeyhole },
      { id: "Reports & Evidence", name: "Reports & Evidence", icon: FileText },
      { id: "Audit Logs", name: "Audit Logs", icon: Terminal },
      { id: "Settings", name: "Settings", icon: SettingsIcon }
    ]
  }
];

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  criticalCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  collapsed,
  onToggleCollapse,
  criticalCount = 0
}) => {
  return (
    <aside
      className={`fixed top-0 left-0 bottom-0 z-30 bg-slate-900 border-r border-slate-800 transition-all duration-200 flex flex-col ${
        collapsed ? "w-16" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div className="h-14 border-b border-slate-800 flex items-center justify-between px-3.5">
        <div className="flex items-center gap-2.5 overflow-hidden">
          <div className="w-8 h-8 rounded-lg bg-cyan-600/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          {!collapsed && (
            <div className="truncate">
              <span className="font-bold text-slate-100 tracking-tight text-sm">SentinelAI</span>
              <span className="block text-[10px] text-cyan-400 font-mono tracking-wider uppercase font-semibold">
                Autonomous DAST
              </span>
            </div>
          )}
        </div>
        <button
          onClick={onToggleCollapse}
          className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto p-2.5 space-y-5">
        {navSections.map((section) => (
          <div key={section.title}>
            {!collapsed && (
              <h4 className="text-[10px] font-semibold text-slate-400 tracking-wider px-2.5 mb-1.5 uppercase font-mono">
                {section.title}
              </h4>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon;
                const active = currentTab === item.id;
                const hasCritical = item.id === "Vulnerability Findings" && criticalCount > 0;

                return (
                  <button
                    key={item.id}
                    onClick={() => onSelectTab(item.id)}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition select-none cursor-pointer text-left ${
                      active
                        ? "bg-cyan-950/50 text-cyan-300 border-l-2 border-cyan-500 shadow-inner"
                        : "text-slate-300 hover:text-slate-100 hover:bg-slate-800/60"
                    }`}
                    title={collapsed ? item.name : undefined}
                  >
                    <Icon className={`w-4 h-4 shrink-0 ${active ? "text-cyan-400" : "text-slate-400"}`} />
                    {!collapsed && (
                      <span className="truncate flex-1">{item.name}</span>
                    )}
                    {!collapsed && hasCritical && (
                      <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-900 text-rose-200">
                        {criticalCount}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Workspace Footer */}
      {!collapsed && (
        <div className="p-3 border-t border-slate-800 bg-slate-900/60 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-slate-300 font-medium truncate">VoyageSim Staging</span>
          </div>
          <span className="text-[10px] text-slate-400 block mt-0.5 font-mono">Policy Boundary: Isolated</span>
        </div>
      )}
    </aside>
  );
};
