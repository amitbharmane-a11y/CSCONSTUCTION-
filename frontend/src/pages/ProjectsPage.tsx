import { useMemo, useState } from "react";
import { useCreateProject, useDeleteProject, useProjects } from "../api/hooks";
import { Button, Card, Input } from "../components/ui";

export default function ProjectsPage() {
  const { data, isLoading, error } = useProjects();
  const create = useCreateProject();
  const del = useDeleteProject();

  const [name, setName] = useState("");
  const [client, setClient] = useState("PWD / Indian Railways");
  const [location, setLocation] = useState("Maharashtra");
  const [contractNo, setContractNo] = useState("");
  const [startDate, setStartDate] = useState("");

  const canSubmit = name.trim().length >= 2 && client.trim() && location.trim();

  const projects = useMemo(() => data || [], [data]);

  return (
    <div className="grid gap-4">
      <Card title="Create Project">
        <form
          className="grid gap-3 md:grid-cols-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (!canSubmit) return;
            create.mutate(
              {
                name: name.trim(),
                client: client.trim(),
                location: location.trim(),
                contract_no: contractNo.trim() || null,
                start_date: startDate.trim() || null,
                end_date: null
              },
              {
                onSuccess: () => {
                  setName("");
                  setContractNo("");
                  setStartDate("");
                }
              }
            );
          }}
        >
          <Input label="Project Name" value={name} onChange={setName} placeholder="e.g. ROB + Bridge Works" required />
          <Input label="Client" value={client} onChange={setClient} placeholder="PWD / Indian Railways / MSRDC" required />
          <Input label="Location" value={location} onChange={setLocation} placeholder="City / District / State" required />
          <Input label="Contract No." value={contractNo} onChange={setContractNo} placeholder="Optional" />
          <Input label="Start Date" value={startDate} onChange={setStartDate} type="date" />
          <div className="flex items-end gap-2">
            <Button type="submit" disabled={!canSubmit || create.isPending}>
              {create.isPending ? "Creating…" : "Create"}
            </Button>
            {create.isError && <div className="text-sm text-rose-700">{(create.error as Error).message}</div>}
          </div>
        </form>
      </Card>

      <Card title="Projects">
        {isLoading && <div className="text-sm text-slate-600">Loading…</div>}
        {error && <div className="text-sm text-rose-700">Failed: {(error as Error).message}</div>}
        {!isLoading && projects.length === 0 && <div className="text-sm text-slate-600">No projects yet.</div>}

        <div className="divide-y divide-slate-100">
          {projects.map((p) => (
            <div key={p.id} className="flex flex-col gap-2 py-3 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-sm font-semibold">{p.name}</div>
                <div className="mt-1 text-xs text-slate-600">
                  {p.client} • {p.location} • {p.contract_no || "No contract no."}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="danger"
                  disabled={del.isPending}
                  onClick={() => {
                    if (!confirm("Delete this project? This will delete logs, costs and budgets.")) return;
                    del.mutate(p.id);
                  }}
                >
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

