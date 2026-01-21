import { useMemo } from "react";
import { Pie, PieChart, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, Legend } from "recharts";
import { useJobCosting } from "../api/hooks";
import { Card, formatINR } from "../components/ui";

const COLORS = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"];

const getAlertColor = (pct: number | null) => {
  if (!pct) return "text-slate-600";
  if (pct >= 90) return "text-rose-700"; // Red
  if (pct >= 75) return "text-amber-600"; // Yellow
  return "text-emerald-700"; // Green
};

const getCardAlertClass = (pct: number | null) => {
  if (!pct) return "";
  if (pct >= 90) return "border-rose-200 bg-rose-50";
  if (pct >= 75) return "border-amber-200 bg-amber-50";
  return "border-emerald-200 bg-emerald-50";
};

export default function DashboardPage({ projectId }: { projectId: number | null }) {
  const { data, isLoading, error } = useJobCosting(projectId);

  const pieData = useMemo(() => {
    if (!data) return [];
    return data.categories
      .filter(cat => cat.actual_cost > 0)
      .map((cat) => ({
        name: cat.category,
        value: cat.actual_cost,
        percent: cat.percent_of_total_actual
      }))
      .sort((a, b) => b.value - a.value);
  }, [data]);

  const barData = useMemo(() => {
    if (!data) return [];
    return data.categories.map((cat) => ({
      category: cat.category,
      planned: cat.planned_cost,
      actual: cat.actual_cost,
      variance: cat.percent_over_under_budget
    }));
  }, [data]);

  // Calculate profit margin (assuming 10% target margin)
  const profitMargin = useMemo(() => {
    if (!data) return null;
    const totalRevenue = data.total_planned_cost * 1.1; // Assuming 10% profit margin target
    const currentMargin = ((totalRevenue - data.total_actual_cost) / totalRevenue) * 100;
    return currentMargin;
  }, [data]);

  // Calculate days remaining (rough estimate based on project dates)
  const daysRemaining = useMemo(() => {
    if (!data) return null;
    // This is a placeholder - in real app you'd calculate from project end_date
    return 45; // Example: 45 days remaining
  }, [data]);

  if (!projectId) return <div className="text-sm text-slate-600">Create/select a project to view dashboard.</div>;
  if (isLoading) return <div className="text-sm text-slate-600">Loading…</div>;
  if (error) return <div className="text-sm text-rose-700">Failed: {(error as Error).message}</div>;
  if (!data) return null;

  const overallVariance = data.percent_over_under_budget;

  return (
    <div className="grid gap-6">
      {/* High-Level Financial Summaries */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card title="Total Budget" className={getCardAlertClass(overallVariance)}>
          <div className="text-2xl font-extrabold">{formatINR(data.total_planned_cost)}</div>
          <div className="mt-1 text-xs text-slate-600">Planned project budget</div>
        </Card>

        <Card title="Total Job Cost" className={getCardAlertClass(overallVariance)}>
          <div className="text-2xl font-extrabold">{formatINR(data.total_actual_cost)}</div>
          <div className="mt-1 text-xs text-slate-600">Actual costs incurred</div>
        </Card>

        <Card title="% Over/Under Budget" className={getCardAlertClass(overallVariance)}>
          <div className={`text-2xl font-extrabold ${getAlertColor(overallVariance)}`}>
            {overallVariance !== null ? `${overallVariance.toFixed(1)}%` : "N/A"}
          </div>
          <div className="mt-1 text-xs text-slate-600">
            {overallVariance !== null && overallVariance > 0 ? "Over budget" : "Under budget"}
          </div>
        </Card>

        <Card title="Profit Margin" className={getCardAlertClass(profitMargin !== null && profitMargin < 5 ? 90 : null)}>
          <div className={`text-2xl font-extrabold ${getAlertColor(profitMargin !== null && profitMargin < 5 ? 90 : null)}`}>
            {profitMargin !== null ? `${profitMargin.toFixed(1)}%` : "N/A"}
          </div>
          <div className="mt-1 text-xs text-slate-600">
            {daysRemaining !== null && `~${daysRemaining} days remaining`}
          </div>
        </Card>
      </div>

      {/* Categorized Totals */}
      <div className="grid gap-4 md:grid-cols-5">
        {data.categories.map((cat) => (
          <Card key={cat.category} title={cat.category} className={getCardAlertClass(cat.percent_over_under_budget)}>
            <div className="text-lg font-semibold">{formatINR(cat.actual_cost)}</div>
            <div className={`text-xs mt-1 ${getAlertColor(cat.percent_over_under_budget)}`}>
              {cat.percent_over_under_budget !== null
                ? `${cat.percent_over_under_budget > 0 ? '+' : ''}${cat.percent_over_under_budget.toFixed(1)}%`
                : "N/A"
              }
            </div>
          </Card>
        ))}
      </div>

      {/* Visual Data Representation */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Expense Allocation (% of Total Cost)">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={120}
                  innerRadius={60}
                  label={({ percent }) => `${(percent * 100).toFixed(1)}%`}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => formatINR(Number(v))} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid gap-2 text-sm">
            {pieData.map((d, i) => (
              <div key={d.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: COLORS[i % COLORS.length] }}
                  />
                  <span className="truncate">{d.name}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{formatINR(d.value)}</div>
                  <div className="text-xs text-slate-600">{d.percent.toFixed(1)}%</div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Planned vs Actual by Category">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <XAxis dataKey="category" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(v) => `${Math.round(Number(v) / 100000)}L`} />
                <Tooltip formatter={(v) => formatINR(Number(v))} />
                <Legend />
                <Bar dataKey="planned" fill="#94a3b8" name="Planned" />
                <Bar dataKey="actual" fill="#4f46e5" name="Actual" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-xs text-slate-600">
            Green bars = planned budget, Blue bars = actual costs
          </div>
        </Card>
      </div>

      {/* Granular Cost Breakdown Table */}
      <Card title="Detailed Cost Breakdown">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200">
              <tr className="text-left">
                <th className="pb-2 font-semibold">Category</th>
                <th className="pb-2 font-semibold text-right">Qty/Hours</th>
                <th className="pb-2 font-semibold text-right">UOM</th>
                <th className="pb-2 font-semibold text-right">Unit Rate</th>
                <th className="pb-2 font-semibold text-right">Total Cost</th>
                <th className="pb-2 font-semibold text-right">% of Total</th>
                <th className="pb-2 font-semibold text-right">Variance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.categories.map((cat) => (
                <tr key={cat.category} className="hover:bg-slate-50">
                  <td className="py-3 font-medium">{cat.category}</td>
                  <td className="py-3 text-right">
                    {cat.quantity ? cat.quantity.toLocaleString() : "-"}
                  </td>
                  <td className="py-3 text-right">{cat.uom || "-"}</td>
                  <td className="py-3 text-right">
                    {cat.unit_cost ? formatINR(cat.unit_cost) : "-"}
                  </td>
                  <td className="py-3 text-right font-semibold">{formatINR(cat.actual_cost)}</td>
                  <td className="py-3 text-right">{cat.percent_of_total_actual.toFixed(1)}%</td>
                  <td className={`py-3 text-right font-semibold ${getAlertColor(cat.percent_over_under_budget)}`}>
                    {cat.percent_over_under_budget !== null
                      ? `${cat.percent_over_under_budget > 0 ? '+' : ''}${cat.percent_over_under_budget.toFixed(1)}%`
                      : "N/A"
                    }
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="border-t border-slate-200 font-semibold">
              <tr>
                <td className="py-3">TOTAL</td>
                <td className="py-3 text-right">-</td>
                <td className="py-3 text-right">-</td>
                <td className="py-3 text-right">-</td>
                <td className="py-3 text-right">{formatINR(data.total_actual_cost)}</td>
                <td className="py-3 text-right">100.0%</td>
                <td className={`py-3 text-right ${getAlertColor(overallVariance)}`}>
                  {overallVariance !== null
                    ? `${overallVariance > 0 ? '+' : ''}${overallVariance.toFixed(1)}%`
                    : "N/A"
                  }
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </Card>

      {/* Alert System Summary */}
      <Card title="Budget Alerts" className="border-amber-200 bg-amber-50">
        <div className="grid gap-2 md:grid-cols-3 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-rose-500 rounded"></div>
            <span>≥90% of budget: Critical</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-amber-500 rounded"></div>
            <span>75-89% of budget: Warning</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-emerald-500 rounded"></div>
            <span>&lt;75% of budget: Good</span>
          </div>
        </div>
        <div className="mt-3 text-xs text-slate-600">
          Categories highlighted in colors based on budget utilization. Monitor closely and adjust spending as needed.
        </div>
      </Card>
    </div>
  );
}

