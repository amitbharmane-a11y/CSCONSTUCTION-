import { useMemo, useState } from "react";
import { useBudgets, useCosts, useCreateCost, useUpsertBudget } from "../api/hooks";
import { Button, Card, Input, Select, TextArea, formatINR } from "../components/ui";

const COST_HEADS = [
  "Materials - Steel",
  "Materials - Cement/RMC",
  "Labour",
  "Machinery",
  "Subcontract",
  "Fuel",
  "Testing & QA",
  "Overheads",
  "Misc"
].map((x) => ({ value: x, label: x }));

export default function CostsBudgetPage({ projectId }: { projectId: number | null }) {
  const costsQ = useCosts(projectId);
  const budgetsQ = useBudgets(projectId);
  const createCost = useCreateCost();
  const upsert = useUpsertBudget();

  const [entryDate, setEntryDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [costHead, setCostHead] = useState(COST_HEADS[0].value);
  const [description, setDescription] = useState("");
  const [vendor, setVendor] = useState("");
  const [amount, setAmount] = useState("");
  const [quantity, setQuantity] = useState("");
  const [uom, setUom] = useState("");
  const [unitRate, setUnitRate] = useState("");
  const [paymentMode, setPaymentMode] = useState("Cash");
  const [billNo, setBillNo] = useState("");

  const costs = useMemo(() => costsQ.data || [], [costsQ.data]);
  const budgets = useMemo(() => budgetsQ.data || [], [budgetsQ.data]);

  const totalCosts = useMemo(() => costs.reduce((s, c) => s + (c.amount || 0), 0), [costs]);
  const totalBudget = useMemo(() => budgets.reduce((s, b) => s + (b.budget_amount || 0), 0), [budgets]);

  if (!projectId) return <div className="text-sm text-slate-600">Select a project first.</div>;

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card title="Add Cost Entry">
        <form
          className="grid gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            if (!projectId) return;
            if (description.trim().length < 2) return;
            createCost.mutate(
              {
                project_id: projectId,
                entry_date: entryDate,
                cost_head: costHead,
                description: description.trim(),
                vendor: vendor.trim() || null,
                amount: Number(amount) || 0,
                quantity: Number(quantity) || null,
                uom: uom.trim() || null,
                unit_rate: Number(unitRate) || null,
                payment_mode: paymentMode.trim() || null,
                bill_no: billNo.trim() || null
              },
              {
                onSuccess: () => {
                  setDescription("");
                  setVendor("");
                  setAmount("");
                  setQuantity("");
                  setUom("");
                  setUnitRate("");
                  setBillNo("");
                }
              }
            );
          }}
        >
          <div className="grid gap-3 md:grid-cols-2">
            <Input label="Date" type="date" value={entryDate} onChange={setEntryDate} required />
            <Select label="Cost Head" value={costHead} onChange={setCostHead} options={COST_HEADS} />
          </div>
          <TextArea label="Description" value={description} onChange={setDescription} placeholder="e.g. RMC M30 supply for pile cap" />
          <div className="grid gap-3 md:grid-cols-2">
            <Input label="Vendor" value={vendor} onChange={setVendor} placeholder="Optional" />
            <Input label="Amount (INR)" value={amount} onChange={setAmount} placeholder="e.g. 25000" required />
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <Input label="Quantity" value={quantity} onChange={setQuantity} placeholder="e.g. 10" />
            <Input label="UOM" value={uom} onChange={setUom} placeholder="e.g. CuM, MT, Nos" />
            <Input label="Unit Rate (INR)" value={unitRate} onChange={setUnitRate} placeholder="e.g. 2500" />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <Input label="Payment Mode" value={paymentMode} onChange={setPaymentMode} placeholder="Cash / Bank / UPI" />
            <Input label="Bill No." value={billNo} onChange={setBillNo} placeholder="Optional" />
          </div>
          <div className="flex items-center gap-2">
            <Button type="submit" disabled={createCost.isPending}>
              {createCost.isPending ? "Saving…" : "Save Cost"}
            </Button>
            {createCost.isError && <div className="text-sm text-rose-700">{(createCost.error as Error).message}</div>}
          </div>
        </form>
      </Card>

      <Card title="Budget Heads (Edit planned amounts)">
        {budgetsQ.isLoading && <div className="text-sm text-slate-600">Loading…</div>}
        {budgetsQ.error && <div className="text-sm text-rose-700">Failed: {(budgetsQ.error as Error).message}</div>}

        <div className="grid gap-2">
          {budgets.map((b) => (
            <div key={b.id} className="grid gap-2 rounded-lg border border-slate-100 p-3 md:grid-cols-3">
              <div className="md:col-span-2">
                <div className="text-sm font-semibold">{b.cost_head}</div>
                <div className="text-xs text-slate-600">{b.notes || "—"}</div>
              </div>
              <div className="flex items-end gap-2">
                <Input
                  label="Budget (INR)"
                  value={String(b.budget_amount)}
                  onChange={(v) => {
                    const next = Number(v);
                    if (!Number.isFinite(next)) return;
                    upsert.mutate({ project_id: projectId, cost_head: b.cost_head, budget_amount: next, notes: b.notes || null });
                  }}
                />
              </div>
            </div>
          ))}
          {budgets.length === 0 && (
            <div className="text-sm text-slate-600">
              No budget heads yet. Add by entering a new cost head in backend seed or request an “Add budget head” feature.
            </div>
          )}
        </div>
      </Card>

      <Card
        title="Costs (Latest)"
        right={
          <div className="text-xs text-slate-600">
            Total: <span className="font-semibold">{formatINR(totalCosts)}</span>
          </div>
        }
      >
        {costsQ.isLoading && <div className="text-sm text-slate-600">Loading…</div>}
        {costsQ.error && <div className="text-sm text-rose-700">Failed: {(costsQ.error as Error).message}</div>}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-xs uppercase text-slate-600">
                <th className="py-2 pr-3">Date</th>
                <th className="py-2 pr-3">Head</th>
                <th className="py-2 pr-3">Description</th>
                <th className="py-2 pr-3">Qty</th>
                <th className="py-2 pr-3">UOM</th>
                <th className="py-2 pr-3">Unit Rate</th>
                <th className="py-2 pr-3">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {costs.map((c) => (
                <tr key={c.id}>
                  <td className="py-2 pr-3 font-semibold">{c.entry_date}</td>
                  <td className="py-2 pr-3">{c.cost_head}</td>
                  <td className="py-2 pr-3">{c.description}</td>
                  <td className="py-2 pr-3 text-right">{c.quantity ? c.quantity.toLocaleString() : "-"}</td>
                  <td className="py-2 pr-3">{c.uom || "-"}</td>
                  <td className="py-2 pr-3 text-right">{c.unit_rate ? formatINR(c.unit_rate) : "-"}</td>
                  <td className="py-2 pr-3 font-semibold text-right">{formatINR(c.amount)}</td>
                </tr>
              ))}
              {costs.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-6 text-sm text-slate-600">
                    No cost entries yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Budget Flow (Quick View)">
        <div className="grid gap-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-700">Total Budget</span>
            <span className="font-semibold">{formatINR(totalBudget)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-700">Total Actual Cost</span>
            <span className="font-semibold">{formatINR(totalCosts)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-700">Variance</span>
            <span className={`font-semibold ${totalCosts - totalBudget > 0 ? "text-rose-700" : "text-emerald-700"}`}>
              {formatINR(totalCosts - totalBudget)}
            </span>
          </div>
        </div>
        <div className="mt-3 text-xs text-slate-600">
          For better cash flow, we can add “receipts / RA bill / payments pending” next.
        </div>
      </Card>
    </div>
  );
}

