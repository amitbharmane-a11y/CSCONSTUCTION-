import { useMemo } from "react";
import { Pie, PieChart, Cell, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import { useQualityTests, useNCRs, useSafetyIncidents, useProjectMilestones } from "../api/hooks";
import { Card, formatINR } from "../components/ui";

const COLORS = ["#10b981", "#ef4444", "#f59e0b", "#8b5cf6", "#06b6d4"];

export default function QualitySafetyPage({ projectId }: { projectId: number | null }) {
  const qualityTestsQ = useQualityTests(projectId);
  const ncrsQ = useNCRs(projectId);
  const safetyIncidentsQ = useSafetyIncidents(projectId);
  const milestonesQ = useProjectMilestones(projectId);

  const qualityTests = useMemo(() => qualityTestsQ.data || [], [qualityTestsQ.data]);
  const ncrs = useMemo(() => ncrsQ.data || [], [ncrsQ.data]);
  const safetyIncidents = useMemo(() => safetyIncidentsQ.data || [], [safetyIncidentsQ.data]);
  const milestones = useMemo(() => milestonesQ.data || [], [milestonesQ.data]);

  // Calculate KPIs
  const qualityKPIs = useMemo(() => {
    const totalPlanned = qualityTests.reduce((sum, test) => sum + test.planned_tests, 0);
    const totalConducted = qualityTests.reduce((sum, test) => sum + test.conducted_tests, 0);
    const totalPassed = qualityTests.reduce((sum, test) => sum + test.passed_tests, 0);
    const passRate = totalConducted > 0 ? (totalPassed / totalConducted) * 100 : 0;

    const openNCRs = ncrs.filter(ncr => ncr.status === 'Open').length;
    const closedNCRs = ncrs.filter(ncr => ncr.status === 'Closed').length;
    const avgClosureDays = ncrs.filter(ncr => ncr.closure_days).reduce((sum, ncr) => sum + (ncr.closure_days || 0), 0) / Math.max(closedNCRs, 1);

    return {
      totalPlanned,
      totalConducted,
      totalPassed,
      passRate,
      openNCRs,
      closedNCRs,
      avgClosureDays: avgClosureDays || 0
    };
  }, [qualityTests, ncrs]);

  const safetyKPIs = useMemo(() => {
    const lti = safetyIncidents.filter(inc => inc.incident_type?.includes('LTI')).length;
    const nearMisses = safetyIncidents.filter(inc => inc.incident_type?.includes('Near Miss')).length;
    const firstAid = safetyIncidents.filter(inc => inc.incident_type?.includes('First Aid')).length;
    const totalIncidents = safetyIncidents.length;

    const ltifr = totalIncidents > 0 ? (lti * 1000000) / (totalIncidents * 1000) : 0; // Assuming 1000 manhours

    return {
      totalIncidents,
      lti,
      nearMisses,
      firstAid,
      ltifr
    };
  }, [safetyIncidents]);

  const milestoneKPIs = useMemo(() => {
    const totalMilestones = milestones.length;
    const achievedMilestones = milestones.filter(m => m.status === 'Achieved').length;
    const achievementRate = totalMilestones > 0 ? (achievedMilestones / totalMilestones) * 100 : 0;

    return {
      totalMilestones,
      achievedMilestones,
      achievementRate
    };
  }, [milestones]);

  // Chart data
  const incidentTrendData = useMemo(() => {
    const monthlyData: { [key: string]: { month: string; incidents: number; ncrs: number } } = {};

    safetyIncidents.forEach(incident => {
      if (incident.incident_date) {
        const month = incident.incident_date.slice(0, 7); // YYYY-MM
        if (!monthlyData[month]) {
          monthlyData[month] = { month, incidents: 0, ncrs: 0 };
        }
        monthlyData[month].incidents++;
      }
    });

    ncrs.forEach(ncr => {
      if (ncr.raised_date) {
        const month = ncr.raised_date.slice(0, 7);
        if (!monthlyData[month]) {
          monthlyData[month] = { month, incidents: 0, ncrs: 0 };
        }
        monthlyData[month].ncrs++;
      }
    });

    return Object.values(monthlyData).sort((a, b) => a.month.localeCompare(b.month));
  }, [safetyIncidents, ncrs]);

  const qualityPieData = useMemo(() => {
    if (qualityTests.length === 0) return [];

    const testTypes: { [key: string]: { name: string; passed: number; failed: number } } = {};

    qualityTests.forEach(test => {
      if (!testTypes[test.test_type]) {
        testTypes[test.test_type] = { name: test.test_type, passed: 0, failed: 0 };
      }
      testTypes[test.test_type].passed += test.passed_tests;
      testTypes[test.test_type].failed += test.failed_tests;
    });

    return Object.values(testTypes);
  }, [qualityTests]);

  if (!projectId) return <div className="text-sm text-slate-600">Select a project to view quality & safety dashboard.</div>;

  return (
    <div className="grid gap-6">
      <div className="text-2xl font-bold text-slate-900">Quality & Safety Dashboard</div>

      {/* Quality KPIs */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card title="Quality Tests Conducted">
          <div className="text-2xl font-extrabold text-blue-600">{qualityKPIs.totalConducted}</div>
          <div className="mt-1 text-xs text-slate-600">
            Out of {qualityKPIs.totalPlanned} planned ({qualityKPIs.totalPlanned > 0 ? ((qualityKPIs.totalConducted / qualityKPIs.totalPlanned) * 100).toFixed(1) : 0}%)
          </div>
        </Card>

        <Card title="Pass Rate" className={qualityKPIs.passRate >= 95 ? "border-emerald-200 bg-emerald-50" : "border-amber-200 bg-amber-50"}>
          <div className={`text-2xl font-extrabold ${qualityKPIs.passRate >= 95 ? "text-emerald-600" : "text-amber-600"}`}>
            {qualityKPIs.passRate.toFixed(1)}%
          </div>
          <div className="mt-1 text-xs text-slate-600">
            {qualityKPIs.totalPassed} passed / {qualityKPIs.totalConducted} total
          </div>
        </Card>

        <Card title="Open NCRs" className="border-rose-200 bg-rose-50">
          <div className="text-2xl font-extrabold text-rose-600">{qualityKPIs.openNCRs}</div>
          <div className="mt-1 text-xs text-slate-600">
            {qualityKPIs.closedNCRs} closed this period
          </div>
        </Card>

        <Card title="NCR Closure Time">
          <div className="text-2xl font-extrabold text-indigo-600">{qualityKPIs.avgClosureDays.toFixed(0)} days</div>
          <div className="mt-1 text-xs text-slate-600">
            Average time to resolve NCRs
          </div>
        </Card>
      </div>

      {/* Safety KPIs */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card title="Total Safety Incidents" className="border-rose-200 bg-rose-50">
          <div className="text-2xl font-extrabold text-rose-600">{safetyKPIs.totalIncidents}</div>
          <div className="mt-1 text-xs text-slate-600">Total incidents reported</div>
        </Card>

        <Card title="Lost Time Injuries (LTI)">
          <div className="text-2xl font-extrabold text-red-600">{safetyKPIs.lti}</div>
          <div className="mt-1 text-xs text-slate-600">Incidents causing lost time</div>
        </Card>

        <Card title="LTIFR (Lost Time Injury Frequency Rate)">
          <div className="text-2xl font-extrabold text-orange-600">{safetyKPIs.ltifr.toFixed(2)}</div>
          <div className="mt-1 text-xs text-slate-600">Per 1,000,000 manhours</div>
        </Card>

        <Card title="Near Misses">
          <div className="text-2xl font-extrabold text-amber-600">{safetyKPIs.nearMisses}</div>
          <div className="mt-1 text-xs text-slate-600">Potential incidents prevented</div>
        </Card>
      </div>

      {/* Milestone Achievement */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card title="Milestone Achievement Rate" className={milestoneKPIs.achievementRate >= 80 ? "border-emerald-200 bg-emerald-50" : "border-amber-200 bg-amber-50"}>
          <div className={`text-2xl font-extrabold ${milestoneKPIs.achievementRate >= 80 ? "text-emerald-600" : "text-amber-600"}`}>
            {milestoneKPIs.achievementRate.toFixed(1)}%
          </div>
          <div className="mt-1 text-xs text-slate-600">
            {milestoneKPIs.achievedMilestones} of {milestoneKPIs.totalMilestones} achieved
          </div>
        </Card>

        <Card title="First Aid Cases">
          <div className="text-2xl font-extrabold text-blue-600">{safetyKPIs.firstAid}</div>
          <div className="mt-1 text-xs text-slate-600">Minor injuries treated</div>
        </Card>

        <Card title="Safety Training">
          <div className="text-2xl font-extrabold text-green-600">85%</div>
          <div className="mt-1 text-xs text-slate-600">Workforce trained this month</div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Quality Test Results by Type">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={qualityPieData}
                  dataKey="passed"
                  nameKey="name"
                  outerRadius={100}
                  innerRadius={50}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                >
                  {qualityPieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Monthly Incident & NCR Trends">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={incidentTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="incidents" stroke="#ef4444" name="Safety Incidents" />
                <Line type="monotone" dataKey="ncrs" stroke="#f59e0b" name="Quality NCRs" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Recent NCRs Table */}
      <Card title="Recent NCRs">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200">
              <tr className="text-left">
                <th className="pb-2">NCR No</th>
                <th className="pb-2">Category</th>
                <th className="pb-2">Severity</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Closure Days</th>
                <th className="pb-2">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {ncrs.slice(0, 10).map((ncr) => (
                <tr key={ncr.id} className="hover:bg-slate-50">
                  <td className="py-3 font-semibold">{ncr.ncr_no}</td>
                  <td className="py-3">{ncr.category || "-"}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      ncr.severity === 'Critical' ? 'bg-red-100 text-red-800' :
                      ncr.severity === 'Major' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {ncr.severity}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      ncr.status === 'Closed' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {ncr.status}
                    </span>
                  </td>
                  <td className="py-3">{ncr.closure_days || "-"}</td>
                  <td className="py-3 max-w-xs truncate">{ncr.description || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {ncrs.length === 0 && (
            <div className="py-6 text-sm text-slate-600 text-center">No NCRs recorded yet.</div>
          )}
        </div>
      </Card>
    </div>
  );
}