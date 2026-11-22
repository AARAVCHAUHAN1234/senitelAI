import React, { useState, useEffect } from "react";
import { Terminal, Search, Clock, Shield } from "lucide-react";
import { Card } from "../components/Card";
import { apiGet } from "../core/api";

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [filterAction, setFilterAction] = useState("");

  useEffect(() => {
    apiGet(`/api/audit?action=${encodeURIComponent(filterAction)}`).then(setLogs).catch(() => {});
  }, [filterAction]);

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-100">
            Immutable Security Audit Trail
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Cryptographically tracked records of autonomous actions, test executions, and administrative interventions
          </p>
        </div>

        <div className="relative w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Filter audit actions..."
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      <Card title={`Audit Events (${logs.length})`}>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                <th className="pb-3">Timestamp</th>
                <th className="pb-3">Action</th>
                <th className="pb-3">Actor</th>
                <th className="pb-3">Payload Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 text-slate-400 whitespace-nowrap">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </td>
                  <td className="py-2.5 font-bold text-cyan-400 whitespace-nowrap">
                    {log.action}
                  </td>
                  <td className="py-2.5 text-slate-300 whitespace-nowrap">
                    {log.actor || "System"}
                  </td>
                  <td className="py-2.5 text-slate-400 truncate max-w-md">
                    {log.detail}
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
