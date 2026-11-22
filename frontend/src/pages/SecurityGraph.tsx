import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  Search,
  Layers,
  Filter,
  ShieldAlert,
  ArrowRight,
  Database,
  Globe,
  Radio,
  X
} from "lucide-react";
import { apiGet } from "../core/api";
import { Button } from "../components/Button";
import { Badge } from "../components/Badge";

export const SecurityGraph: React.FC = () => {
  const [view, setView] = useState<"architecture" | "attack_path">("architecture");
  const [filterType, setFilterType] = useState<string>("All");
  const [search, setSearch] = useState("");
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);

  const loadGraph = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet(`/api/graph/topology?view=${view}`);
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
    } catch {
      // Ignore network errors in demo
    } finally {
      setLoading(false);
    }
  }, [view, setNodes, setEdges]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  const onNodeClick = useCallback((_: any, node: any) => {
    setSelectedNode(node);
  }, []);

  const filteredNodes = useMemo(() => {
    return nodes.map((n) => {
      const label = n.data?.label ? String(n.data.label).toLowerCase() : "";
      const matchesSearch = !search || label.includes(search.toLowerCase());
      const isHidden = !matchesSearch;
      return {
        ...n,
        hidden: isHidden
      };
    });
  }, [nodes, search]);

  return (
    <div className="space-y-4">
      {/* Graph Control Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center rounded-lg bg-slate-950 border border-slate-800 p-0.5">
            <button
              onClick={() => setView("architecture")}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
                view === "architecture"
                  ? "bg-cyan-600 text-white shadow-xs"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Architecture View
            </button>
            <button
              onClick={() => setView("attack_path")}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
                view === "attack_path"
                  ? "bg-rose-700 text-white shadow-xs"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Attack Path View
            </button>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter graph nodes..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 w-44"
            />
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs text-slate-400 font-mono">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-blue-600" />
            App
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-slate-800 border border-slate-600" />
            API
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-600" />
            Database
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-orange-600" />
            Agency
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-rose-600 animate-pulse" />
            Vulnerability
          </span>
        </div>
      </div>

      {/* React Flow Canvas Shell */}
      <div className="relative h-[620px] w-full rounded-2xl border border-slate-800 bg-[#090d16] overflow-hidden shadow-inner">
        <ReactFlow
          nodes={filteredNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          fitView
          fitViewOptions={{ padding: 0.2 }}
        >
          <Background color="#1e293b" gap={20} size={1} />
          <Controls className="bg-slate-900! border-slate-800! text-slate-200! rounded-lg! shadow-lg!" />
          <MiniMap
            nodeColor={(n: any) => {
              if (n.className?.includes("vuln")) return "#ef4444";
              if (n.className?.includes("app")) return "#3b82f6";
              if (n.className?.includes("db")) return "#10b981";
              if (n.className?.includes("agency")) return "#f97316";
              return "#475569";
            }}
            maskColor="rgba(9, 13, 22, 0.75)"
            className="bg-slate-950! border-slate-800! rounded-lg!"
          />
        </ReactFlow>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="absolute top-4 right-4 z-20 w-80 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 rounded-xl p-4 shadow-2xl text-xs space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-mono text-[10px] text-cyan-400 uppercase font-semibold">
                NODE METADATA · {selectedNode.data?.category || "Resource"}
              </span>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-slate-200 p-0.5 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-100">
                {selectedNode.data?.label}
              </h4>
              {selectedNode.data?.endpoint && (
                <p className="font-mono text-slate-400 mt-0.5">{selectedNode.data.endpoint}</p>
              )}
            </div>

            {selectedNode.data?.severity && (
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block mb-1">Severity</span>
                <Badge label={selectedNode.data.severity} variant="severity" />
              </div>
            )}

            {selectedNode.data?.risk !== undefined && (
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block mb-1">Risk Score</span>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-cyan-500 h-full rounded-full"
                      style={{ width: `${selectedNode.data.risk}%` }}
                    />
                  </div>
                  <span className="font-mono font-bold text-slate-200">{selectedNode.data.risk}/100</span>
                </div>
              </div>
            )}

            {selectedNode.data?.impact && (
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block mb-0.5">Business Impact</span>
                <p className="text-slate-300 leading-relaxed">{selectedNode.data.impact}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
