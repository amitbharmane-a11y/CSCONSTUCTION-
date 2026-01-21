import { NavLink } from "react-router-dom";
import type { Project } from "../api/types";
import { Select } from "./ui";

const nav = [
  { to: "/", label: "Dashboard" },
  { to: "/portfolio", label: "Portfolio Overview" },
  { to: "/quality-safety", label: "Quality & Safety" },
  { to: "/job-costing", label: "Job Costing" },
  { to: "/daily", label: "Daily Work Log" },
  { to: "/costs", label: "Costs & Budget" },
  { to: "/projects", label: "Projects" },
  { to: "/ai", label: "AI Assistant" }
];

export default function Layout({
  projects,
  projectId,
  setProjectId,
  children
}: {
  projects: Project[];
  projectId: number | null;
  setProjectId: (id: number) => void;
  children: React.ReactNode;
}) {
  const projectOptions = projects.map((p) => ({ value: String(p.id), label: p.name }));
  return (
    <div className="min-h-screen">
      <div className="flex">
        <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white px-4 py-5 md:block">
          <div className="text-lg font-extrabold tracking-tight text-slate-900">
            C S Construction
          </div>
          <div className="mt-1 text-xs font-semibold text-slate-500">
            PWD / Indian Railways / MSRDC Dashboard
          </div>

          <div className="mt-6 space-y-1">
            {nav.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  `block rounded-lg px-3 py-2 text-sm font-semibold ${
                    isActive ? "bg-indigo-50 text-indigo-700" : "text-slate-700 hover:bg-slate-50"
                  }`
                }
              >
                {n.label}
              </NavLink>
            ))}
          </div>

          <div className="mt-6">
            <Select
              label="Active Project"
              value={projectId ? String(projectId) : ""}
              onChange={(v) => setProjectId(Number(v))}
              options={projectOptions.length ? projectOptions : [{ value: "", label: "No projects" }]}
            />
          </div>
        </aside>

        <main className="flex-1 px-4 py-5 md:px-6">
          <div className="mb-4 flex items-start justify-between gap-4">
            <div>
              <div className="text-xl font-extrabold tracking-tight text-slate-900">
                Construction Dashboard
              </div>
              <div className="text-sm text-slate-600">
                Daily progress • cost control • budget flow
              </div>
            </div>
            <div className="w-80 max-w-full md:hidden">
              <Select
                label="Active Project"
                value={projectId ? String(projectId) : ""}
                onChange={(v) => setProjectId(Number(v))}
                options={projectOptions.length ? projectOptions : [{ value: "", label: "No projects" }]}
              />
            </div>
          </div>
          {children}
          <div className="mt-10 text-xs text-slate-500">
            API: <span className="font-mono">{import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}</span>
          </div>
        </main>
      </div>
    </div>
  );
}

