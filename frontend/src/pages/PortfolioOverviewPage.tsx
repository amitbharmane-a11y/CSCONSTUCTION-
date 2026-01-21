import { useMemo } from "react";
import { Pie, PieChart, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from "recharts";
import { usePortfolioOverview } from "../api/hooks";
import { Card, formatINR } from "../components/ui";

const COLORS = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

export default function PortfolioOverviewPage() {
  const { data, isLoading, error } = usePortfolioOverview();

  const clientData = useMemo(() => {
    if (!data) return [];
    return Object.entries(data.projects_by_client)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8);
  }, [data]);

  const statusData = useMemo(() => {
    if (!data) return [];
    return Object.entries(data.projects_by_status)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [data]);

  if (isLoading) return <div className="text-sm text-slate-600">Loading portfolio overview…</div>;
  if (error) return <div className="text-sm text-rose-700">Failed: {(error as Error).message}</div>;
  if (!data) return null;

  return (
    <div className="grid gap-6">
      <div className="text-2xl font-bold text-slate-900">Portfolio Overview</div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card title="Total Projects">
          <div className="text-3xl font-extrabold text-indigo-600">{data.total_projects}</div>
          <div className="mt-1 text-xs text-slate-600">{data.active_projects} active</div>
        </Card>

        <Card title="Contract Value">
          <div className="text-2xl font-extrabold">{formatINR(data.total_contract_value)}</div>
          <div className="mt-1 text-xs text-slate-600">Total portfolio value</div>
        </Card>

        <Card title="Billed Value">
          <div className="text-2xl font-extrabold text-emerald-600">{formatINR(data.total_billed_value)}</div>
          <div className="mt-1 text-xs text-slate-600">Total billed to date</div>
        </Card>

        <Card title="Overall Progress">
          <div className="text-3xl font-extrabold text-blue-600">{data.overall_progress.toFixed(1)}%</div>
          <div className="mt-1 text-xs text-slate-600">Portfolio completion</div>
        </Card>
      </div>

      {/* Issues & Risks */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card title="Delayed Projects" className="border-amber-200 bg-amber-50">
          <div className="text-2xl font-extrabold text-amber-700">{data.delayed_projects}</div>
          <div className="mt-1 text-xs text-slate-600">Projects behind schedule</div>
        </Card>

        <Card title="Safety Incidents" className="border-rose-200 bg-rose-50">
          <div className="text-2xl font-extrabold text-rose-700">{data.safety_incidents_total}</div>
          <div className="mt-1 text-xs text-slate-600">Total incidents this year</div>
        </Card>

        <Card title="Quality NCRs" className="border-orange-200 bg-orange-50">
          <div className="text-2xl font-extrabold text-orange-700">{data.quality_ncrs_total}</div>
          <div className="mt-1 text-xs text-slate-600">Non-conformance reports</div>
        </Card>
      </div>

      {/* Visual Analytics */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Projects by Client">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={clientData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={100}
                  innerRadius={50}
                  label={({ percent }) => `${(percent * 100).toFixed(1)}%`}
                >
                  {clientData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => `${v} projects`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 grid gap-1 text-xs text-slate-600">
            {clientData.map((d, i) => (
              <div key={d.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: COLORS[i % COLORS.length] }}
                  />
                  <span className="truncate">{d.name}</span>
                </div>
                <span className="font-semibold">{d.value} projects</span>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Projects by Status">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip formatter={(v) => `${v} projects`} />
                <Bar dataKey="value" fill="#4f46e5" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-xs text-slate-600">
            Project status distribution across portfolio
          </div>
        </Card>
      </div>

      {/* Recent Activity Summary */}
      <Card title="Portfolio Health Summary">
        <div className="grid gap-4 md:grid-cols-3 text-sm">
          <div className="space-y-2">
            <div className="font-semibold text-slate-900">Financial Health</div>
            <div className="text-slate-600">
              <div>Billing Progress: {(data.total_billed_value / data.total_contract_value * 100).toFixed(1)}%</div>
              <div>Outstanding: {formatINR(data.total_contract_value - data.total_billed_value)}</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="font-semibold text-slate-900">Project Health</div>
            <div className="text-slate-600">
              <div>On-Time Projects: {data.total_projects - data.delayed_projects}</div>
              <div>Delayed Projects: {data.delayed_projects}</div>
              <div>Avg Progress: {data.overall_progress.toFixed(1)}%</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="font-semibold text-slate-900">Quality & Safety</div>
            <div className="text-slate-600">
              <div>Incidents/Month: {(data.safety_incidents_total / 12).toFixed(1)}</div>
              <div>NCRs/Project: {(data.quality_ncrs_total / data.total_projects).toFixed(1)}</div>
              <div>LTIFR: {((data.safety_incidents_total * 1000000) / (data.total_projects * 500)).toFixed(2)}</div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}