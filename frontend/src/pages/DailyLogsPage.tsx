import { useMemo, useState } from "react";
import {
  useCreateDailyActivity,
  useCreateDailyLog,
  useDailyActivities,
  useDailyLogs
} from "../api/hooks";
import { Button, Card, Input, Select, TextArea } from "../components/ui";

const CATEGORY_OPTIONS = [
  "Pile Foundation",
  "Sub-Structure",
  "Super-Structure",
  "Bridge Works",
  "Flyover Works (MSRDC)",
  "Earthwork",
  "Drainage",
  "General"
].map((x) => ({ value: x, label: x }));

export default function DailyLogsPage({ projectId }: { projectId: number | null }) {
  const logsQ = useDailyLogs(projectId);
  const createLog = useCreateDailyLog();

  const [logDate, setLogDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [weather, setWeather] = useState("Clear");
  const [remarks, setRemarks] = useState("");

  const logs = useMemo(() => logsQ.data || [], [logsQ.data]);
  const [selectedLogId, setSelectedLogId] = useState<number | null>(null);

  const activitiesQ = useDailyActivities(selectedLogId);
  const createAct = useCreateDailyActivity();

  const [category, setCategory] = useState(CATEGORY_OPTIONS[0].value);
  const [activity, setActivity] = useState("");
  const [uom, setUom] = useState("Nos");
  const [quantity, setQuantity] = useState("1");
  const [labour, setLabour] = useState("10");
  const [machinery, setMachinery] = useState("");
  const [notes, setNotes] = useState("");

  const selectedLog = logs.find((l) => l.id === selectedLogId) || null;

  if (!projectId) return <div className="text-sm text-slate-600">Select a project first.</div>;

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card title="Create Daily Log (DPR)">
        <form
          className="grid gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            createLog.mutate(
              { project_id: projectId, log_date: logDate, weather, remarks: remarks.trim() || null },
              {
                onSuccess: (log) => {
                  setRemarks("");
                  setSelectedLogId(log.id);
                }
              }
            );
          }}
        >
          <div className="grid gap-3 md:grid-cols-2">
            <Input label="Date" type="date" value={logDate} onChange={setLogDate} required />
            <Input label="Weather" value={weather} onChange={setWeather} placeholder="Clear / Rain / Cloudy" />
          </div>
          <TextArea label="Remarks / Constraints" value={remarks} onChange={setRemarks} placeholder="Any issues, delays, permissions, blocks, etc." />
          <div className="flex items-center gap-2">
            <Button type="submit" disabled={createLog.isPending}>
              {createLog.isPending ? "Saving…" : "Save Daily Log"}
            </Button>
            {createLog.isError && <div className="text-sm text-rose-700">{(createLog.error as Error).message}</div>}
          </div>
        </form>
      </Card>

      <Card title="Daily Logs (select one)">
        {logsQ.isLoading && <div className="text-sm text-slate-600">Loading…</div>}
        {logsQ.error && <div className="text-sm text-rose-700">Failed: {(logsQ.error as Error).message}</div>}
        <div className="divide-y divide-slate-100">
          {logs.map((l) => (
            <button
              key={l.id}
              onClick={() => setSelectedLogId(l.id)}
              className={`w-full py-3 text-left ${selectedLogId === l.id ? "bg-indigo-50" : "hover:bg-slate-50"}`}
            >
              <div className="flex items-center justify-between px-3">
                <div className="text-sm font-semibold">{l.log_date}</div>
                <div className="text-xs text-slate-500">{l.weather || "-"}</div>
              </div>
              <div className="mt-1 px-3 text-sm text-slate-700 line-clamp-2">{l.remarks || "-"}</div>
            </button>
          ))}
          {logs.length === 0 && <div className="py-6 text-sm text-slate-600">No logs yet.</div>}
        </div>
      </Card>

      <div className="lg:col-span-2">
        <Card title={`Activities for: ${selectedLog ? selectedLog.log_date : "Select a log"}`}>
          {!selectedLogId && <div className="text-sm text-slate-600">Select a daily log to add activities.</div>}

          {selectedLogId && (
            <>
              <form
                className="grid gap-3 rounded-lg border border-slate-100 bg-slate-50 p-3 md:grid-cols-6"
                onSubmit={(e) => {
                  e.preventDefault();
                  if (!selectedLogId) return;
                  if (activity.trim().length < 2) return;
                  createAct.mutate(
                    {
                      daily_log_id: selectedLogId,
                      category,
                      activity: activity.trim(),
                      uom: uom.trim() || "Nos",
                      quantity: Number(quantity) || 0,
                      labour_count: Number(labour) || 0,
                      machinery: machinery.trim() || null,
                      notes: notes.trim() || null
                    },
                    {
                      onSuccess: () => {
                        setActivity("");
                        setNotes("");
                      }
                    }
                  );
                }}
              >
                <div className="md:col-span-2">
                  <Select label="Category" value={category} onChange={setCategory} options={CATEGORY_OPTIONS} />
                </div>
                <div className="md:col-span-4">
                  <Input label="Activity" value={activity} onChange={setActivity} placeholder="e.g. Boring for pile P-02" required />
                </div>
                <Input label="UOM" value={uom} onChange={setUom} placeholder="Nos / m3 / Kg" />
                <Input label="Qty" value={quantity} onChange={setQuantity} placeholder="0" />
                <Input label="Labour" value={labour} onChange={setLabour} placeholder="0" />
                <Input label="Machinery" value={machinery} onChange={setMachinery} placeholder="Rig / Crane / DG" />
                <div className="md:col-span-5">
                  <Input label="Notes" value={notes} onChange={setNotes} placeholder="Depth, chainage, mix, issue etc." />
                </div>
                <div className="flex items-end">
                  <Button type="submit" disabled={createAct.isPending}>
                    {createAct.isPending ? "Adding…" : "Add"}
                  </Button>
                </div>
              </form>

              <div className="mt-4">
                {activitiesQ.isLoading && <div className="text-sm text-slate-600">Loading…</div>}
                {activitiesQ.error && (
                  <div className="text-sm text-rose-700">Failed: {(activitiesQ.error as Error).message}</div>
                )}
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-xs uppercase text-slate-600">
                        <th className="py-2 pr-3">Category</th>
                        <th className="py-2 pr-3">Activity</th>
                        <th className="py-2 pr-3">Qty</th>
                        <th className="py-2 pr-3">Labour</th>
                        <th className="py-2 pr-3">Machinery</th>
                        <th className="py-2 pr-3">Notes</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {(activitiesQ.data || []).map((a) => (
                        <tr key={a.id}>
                          <td className="py-2 pr-3 font-semibold">{a.category}</td>
                          <td className="py-2 pr-3">{a.activity}</td>
                          <td className="py-2 pr-3">
                            {a.quantity} {a.uom}
                          </td>
                          <td className="py-2 pr-3">{a.labour_count}</td>
                          <td className="py-2 pr-3">{a.machinery || "-"}</td>
                          <td className="py-2 pr-3">{a.notes || "-"}</td>
                        </tr>
                      ))}
                      {(activitiesQ.data || []).length === 0 && (
                        <tr>
                          <td colSpan={6} className="py-6 text-sm text-slate-600">
                            No activities yet.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}

