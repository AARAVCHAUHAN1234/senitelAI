import React, { useState, useEffect, useCallback } from "react";
import { Download, Upload, Search, Filter, Globe, Plus, Sparkles } from "lucide-react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Badge } from "../components/Badge";
import { apiGet, apiPost, API_BASE } from "../core/api";

export const ApiDiscovery: React.FC = () => {
  const [apis, setApis] = useState<any[]>([]);
  const [filter, setFilter] = useState("All");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [showIngest, setShowIngest] = useState(false);
  const [seedInput, setSeedInput] = useState(42);
  const [ingestStatus, setIngestStatus] = useState("");

  const loadApis = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet(`/api/apis?q=${encodeURIComponent(query)}&category=${encodeURIComponent(filter)}`);
      setApis(data || []);
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  }, [query, filter]);

  useEffect(() => {
    loadApis();
  }, [loadApis]);

  const handleExportOpenApi = () => {
    window.open(`${API_BASE}/api/apis/openapi`, "_blank");
  };

  const handleGenerateSynthetic = async () => {
    setIngestStatus("Generating synthetic dataset...");
    try {
      const res = await apiPost("/api/ingest/synthetic-dataset", { seed: seedInput });
      setIngestStatus(`Success: ${res.new_endpoints_created} new endpoints generated (Seed ${seedInput})`);
      loadApis();
    } catch (e: any) {
      setIngestStatus(`Error: ${e.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Controls Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search endpoints..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 w-52"
            />
          </div>

          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
            {["All", "Active", "Zombie", "Shadow", "New"].map((cat) => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  filter === cat ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowIngest(!showIngest)}
            icon={<Upload className="w-3.5 h-3.5" />}
          >
            Ingest Data
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleExportOpenApi}
            icon={<Download className="w-3.5 h-3.5" />}
          >
            Export OpenAPI 3.1
          </Button>
        </div>
      </div>

      {/* Dynamic Data Ingestion Drawer / Panel */}
      {showIngest && (
        <Card
          title="Runtime Data Ingestion & Synthetic Generation"
          subtitle="Add runtime traffic, HAR dumps, or generate new parameterized datasets without code changes"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
            <div className="space-y-3">
              <h4 className="font-semibold text-slate-200">Generate New Synthetic Dataset (Rule 1)</h4>
              <p className="text-slate-400">
                Supply a custom integer seed to deterministically synthesize new API endpoints, agencies, and traffic routes.
              </p>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={seedInput}
                  onChange={(e) => setSeedInput(parseInt(e.target.value) || 0)}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 w-28 focus:outline-none focus:border-cyan-500 font-mono"
                />
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleGenerateSynthetic}
                  icon={<Sparkles className="w-3.5 h-3.5" />}
                >
                  Generate Dataset
                </Button>
              </div>
              {ingestStatus && (
                <p className="text-xs font-mono text-cyan-400 bg-cyan-950/40 p-2 rounded border border-cyan-800/40">
                  {ingestStatus}
                </p>
              )}
            </div>

            <div className="space-y-3 border-t md:border-t-0 md:border-l border-slate-800 md:pl-6 pt-4 md:pt-0">
              <h4 className="font-semibold text-slate-200">HAR / Traffic Log Ingestion</h4>
              <p className="text-slate-400">
                Simulate ingestion of production network captures to immediately classify active vs shadow endpoints.
              </p>
              <Button
                variant="secondary"
                size="sm"
                onClick={async () => {
                  setIngestStatus("Ingesting simulated HAR capture...");
                  await apiPost("/api/ingest/har", {
                    log: {
                      entries: [
                        { request: { method: "GET", url: "http://travel.internal/api/v2/flights/stream" }, response: { status: 200 } },
                        { request: { method: "POST", url: "http://travel.internal/api/v2/settlement/payout" }, response: { status: 201 } }
                      ]
                    }
                  });
                  setIngestStatus("HAR capture ingested. New endpoints mapped to inventory.");
                  loadApis();
                }}
              >
                Simulate HAR Traffic Ingest
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Discovered APIs Table */}
      <Card title={`Discovered API Inventory (${apis.length})`} subtitle="Cataloged across 90-day traffic window">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[10px] uppercase">
                <th className="pb-3">Method</th>
                <th className="pb-3">Endpoint</th>
                <th className="pb-3">Classification</th>
                <th className="pb-3">Auth</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">Requests</th>
                <th className="pb-3">Risk</th>
                <th className="pb-3">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {apis.map((a) => (
                <tr key={a.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-2.5 pr-2">
                    <Badge label={a.method} variant="method" />
                  </td>
                  <td className="py-2.5 pr-3 font-mono font-medium text-slate-200 text-[11px]">
                    {a.endpoint}
                  </td>
                  <td className="py-2.5 pr-3">
                    <Badge label={a.category} variant="classification" />
                  </td>
                  <td className="py-2.5 pr-3">
                    {a.auth_required ? (
                      <span className="text-[11px] font-mono text-emerald-400">Bearer Auth</span>
                    ) : (
                      <span className="text-[11px] font-mono text-rose-400">None</span>
                    )}
                  </td>
                  <td className="py-2.5 pr-3 font-mono text-slate-300">
                    {a.status_code || 200}
                  </td>
                  <td className="py-2.5 pr-3 font-mono text-slate-400">
                    {(a.frequency || 0).toLocaleString()}
                  </td>
                  <td className="py-2.5 pr-3">
                    <span
                      className={`font-mono font-bold ${
                        a.risk >= 70 ? "text-rose-400" : a.risk >= 40 ? "text-amber-400" : "text-emerald-400"
                      }`}
                    >
                      {a.risk}/100
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-400">
                    {a.source}
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
