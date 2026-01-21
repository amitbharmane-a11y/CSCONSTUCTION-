import { useMemo, useState } from "react";
import { useAiChat, useSummary } from "../api/hooks";
import { Button, Card, Input, TextArea } from "../components/ui";

export default function AiAssistantPage({ projectId }: { projectId: number | null }) {
  const [question, setQuestion] = useState(
    "Create today's DPR summary (pile foundation + structure) and highlight risks & next day plan."
  );
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const chat = useAiChat();
  const summaryQ = useSummary(projectId, fromDate || undefined, toDate || undefined);

  const quickFacts = useMemo(() => {
    const s = summaryQ.data;
    if (!s) return null;
    const topHead = Object.entries(s.cost_by_head).sort((a, b) => (b[1] || 0) - (a[1] || 0))[0];
    return {
      totalCost: s.total_cost,
      totalBudget: s.total_budget,
      topHead: topHead ? `${topHead[0]} (${Math.round(topHead[1])})` : "-"
    };
  }, [summaryQ.data]);

  if (!projectId) return <div className="text-sm text-slate-600">Select a project first.</div>;

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card title="Ask the AI Assistant">
        <div className="grid gap-3">
          <div className="grid gap-3 md:grid-cols-2">
            <Input label="From date (optional)" type="date" value={fromDate} onChange={setFromDate} />
            <Input label="To date (optional)" type="date" value={toDate} onChange={setToDate} />
          </div>
          <TextArea
            label="Question"
            value={question}
            onChange={setQuestion}
            placeholder="Ask about DPR, progress, cost variance, budget flow, risks…"
          />
          <div className="flex items-center gap-2">
            <Button
              onClick={() => {
                chat.mutate({
                  project_id: projectId,
                  question,
                  from_date: fromDate || null,
                  to_date: toDate || null
                });
              }}
              disabled={chat.isPending}
            >
              {chat.isPending ? "Thinking…" : "Ask"}
            </Button>
            {chat.isError && <div className="text-sm text-rose-700">{(chat.error as Error).message}</div>}
          </div>
        </div>
      </Card>

      <Card title="Quick Facts (from data)">
        {!quickFacts && <div className="text-sm text-slate-600">Loading…</div>}
        {quickFacts && (
          <div className="grid gap-2 text-sm">
            <div className="flex items-center justify-between">
              <span>Total Cost</span>
              <span className="font-semibold">{Math.round(quickFacts.totalCost).toLocaleString("en-IN")} INR</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Total Budget</span>
              <span className="font-semibold">{Math.round(quickFacts.totalBudget).toLocaleString("en-IN")} INR</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Top cost head</span>
              <span className="font-semibold">{quickFacts.topHead}</span>
            </div>
          </div>
        )}
        <div className="mt-3 text-xs text-slate-600">
          If you set <span className="font-mono">OPENAI_API_KEY</span> in <span className="font-mono">backend/.env</span>, this page runs in
          online mode; otherwise it answers in offline mode.
        </div>
      </Card>

      <div className="lg:col-span-2">
        <Card title="Answer">
          {!chat.data && <div className="text-sm text-slate-600">Ask a question to get a response.</div>}
          {chat.data && (
            <div className="space-y-2">
              <div className="text-xs text-slate-500">
                Mode: <span className="font-semibold">{chat.data.mode}</span>
              </div>
              <pre className="whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-sm text-slate-800">
                {chat.data.answer}
              </pre>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

