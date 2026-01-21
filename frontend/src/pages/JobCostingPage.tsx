import { useMemo, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Pie, PieChart, Cell } from "recharts";
import { useJobCosting } from "../api/hooks";
import { Card, Input, formatINR } from "../components/ui";

const COLORS = ["#16a34a", "#7c3aed", "#2563eb", "#f97316", "#64748b"];

function formatPct(v: number | null | undefined) {
  if (v === null || v === undefined || Number.isNaN(v)) return "-";
  return `${v.toFixed(2)}%`;
}

export default function JobCostingPage({ projectId }: { projectId: number | null }) {
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const q = useJobCosting(projectId, fromDate || undefined, toDate || undefined);
  const data = q.data;

  const pieData = useMemo(() => {
    if (!data) return [];
    return data.categories.map((c) => ({ name: c.category, value: c.actual_cost, pct: c.percent_of_total_actual }));
  }, [data]);

  const barData = useMemo(() => {
    if (!data) return [];
    return data.categories.map((c) => ({
      category: c.category,
      planned: c.planned_cost,
      actual: c.actual_cost
    }));
  }, [data]);

  if (!projectId) return <div className="text-sm text-slate-600">Select a project first.</div>;
  if (q.isLoading) return <div className="text-sm text-slate-600">Loading…</div>;
  if (q.error) return <div className="text-sm text-rose-700">Failed: {(q.error as Error).message}</div>;
  if (!data) return null;

  const asOf = data.to_date || new Date().toISOString().slice(0, 10);

  const overUnder = data.percent_over_under_budget;
  const overUnderText = overUnder === null || overUnder === undefined ? "-" : `${overUnder.toFixed(2)}%`;
  const overUnderClass = (overUnder || 0) > 0 ? "text-rose-700" : "text-emerald-700";

  return (
    <div className="grid gap-4">
      <Card title="Job Costing Dashboard (₹ INR)">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <div className="text-xs font-semibold text-slate-600">Project</div>
            <div className="mt-1 text-sm font-semibold text-slate-900">{data.project_name}</div>
            <div className="mt-1 text-xs text-slate-600">
              {data.client} • {data.location}
            </div>
          </div>
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <div className="text-xs font-semibold text-slate-600">Date</div>
            <div className="mt-1 text-sm font-semibold text-slate-900">{asOf}</div>
            <div className="mt-2 grid gap-2 md:grid-cols-2">
              <Input label="From" type="date" value={fromDate} onChange={setFromDate} />
              <Input label="To" type="date" value={toDate} onChange={setToDate} />
            </div>
          </div>
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <div className="grid gap-2">
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-slate-600">Total Budget (Planned)</div>
                <div className="text-sm font-extrabold">{formatINR(data.total_planned_cost)}</div>
              </div>
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-slate-600">Total Job Cost (Actual)</div>
                <div className="text-sm font-extrabold">{formatINR(data.total_actual_cost)}</div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid gap-3 md:grid-cols-6">
        {data.categories.map((c) => (
          <Card key={c.category} title={`Total ${c.category} Cost`}>
            <div className="text-lg font-extrabold">{formatINR(c.actual_cost)}</div>
            <div className="mt-1 text-xs text-slate-600">
              Planned: <span className="font-semibold">{formatINR(c.planned_cost)}</span>
            </div>
          </Card>
        ))}
        <Card title="Percentage Over/Under Budget">
          <div className={`text-lg font-extrabold ${overUnderClass}`}>{overUnderText}</div>
          <div className="mt-1 text-xs text-slate-600">Based on total planned vs total actual</div>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Percentage of Budget (Actual cost share)">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={110}>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(v, _n, p) => {
                    const vv = Number(v);
                    const payload = (p as any)?.payload as { pct?: number };
                    return `${formatINR(vv)} (${(payload?.pct ?? 0).toFixed(2)}%)`;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 grid gap-1 text-xs text-slate-600">
            {data.categories.map((c) => (
              <div key={c.category} className="flex items-center justify-between">
                <span>{c.category}</span>
                <span className="font-semibold">{formatPct(c.percent_of_total_actual)}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Planned vs. Actual">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <XAxis dataKey="category" />
                <YAxis tickFormatter={(v) => `${Math.round(Number(v) / 100000)}L`} />
                <Tooltip formatter={(v) => formatINR(Number(v))} />
                <Bar dataKey="planned" name="Planned Cost" fill="#94a3b8" />
                <Bar dataKey="actual" name="Actual Cost" fill="#4f46e5" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card title="Cost Breakdown Table">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-xs uppercase text-slate-600">
                <th className="py-2 pr-3">Category</th>
                <th className="py-2 pr-3">Hours / Quantity</th>
                <th className="py-2 pr-3">Unit Cost</th>
                <th className="py-2 pr-3">Total Cost</th>
                <th className="py-2 pr-3">Percentage of Budget</th>
                <th className="py-2 pr-3">Over/Under</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.categories.map((c) => (
                <tr key={c.category}>
                  <td className="py-2 pr-3 font-semibold">{c.category}</td>
                  <td className="py-2 pr-3">
                    {c.quantity ? `${c.quantity.toFixed(2)} ${c.uom || ""}`.trim() : "-"}
                  </td>
                  <td className="py-2 pr-3">{c.unit_cost ? formatINR(c.unit_cost) : "-"}</td>
                  <td className="py-2 pr-3 font-semibold">{formatINR(c.actual_cost)}</td>
                  <td className="py-2 pr-3">{formatPct(c.percent_of_total_actual)}</td>
                  <td className="py-2 pr-3">{formatPct(c.percent_over_under_budget)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

