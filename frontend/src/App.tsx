import { Route, Routes } from "react-router-dom";
import { useProjects } from "./api/hooks";
import Layout from "./components/Layout";
import { useSelectedProjectId } from "./state";
import DashboardPage from "./pages/DashboardPage";
import ProjectsPage from "./pages/ProjectsPage";
import DailyLogsPage from "./pages/DailyLogsPage";
import CostsBudgetPage from "./pages/CostsBudgetPage";
import AiAssistantPage from "./pages/AiAssistantPage";
import JobCostingPage from "./pages/JobCostingPage";
import PortfolioOverviewPage from "./pages/PortfolioOverviewPage";
import QualitySafetyPage from "./pages/QualitySafetyPage";

export default function App() {
  const projectsQ = useProjects();
  const projects = projectsQ.data || [];
  const projectIds = projects.map((p) => p.id);
  const { projectId, setProjectId } = useSelectedProjectId(projectIds);

  return (
    <Layout
      projects={projects}
      projectId={projectId}
      setProjectId={(id) => setProjectId(id)}
    >
      {projectsQ.isLoading && <div className="text-sm text-slate-600">Loading projects…</div>}
      {projectsQ.error && (
        <div className="text-sm text-rose-700">
          Backend not reachable. Start backend on <span className="font-mono">http://localhost:8000</span>.
          <div className="mt-1">{(projectsQ.error as Error).message}</div>
        </div>
      )}

      {!projectsQ.isLoading && !projectsQ.error && (
        <Routes>
          <Route path="/" element={<DashboardPage projectId={projectId} />} />
          <Route path="/portfolio" element={<PortfolioOverviewPage />} />
          <Route path="/quality-safety" element={<QualitySafetyPage projectId={projectId} />} />
          <Route path="/job-costing" element={<JobCostingPage projectId={projectId} />} />
          <Route path="/daily" element={<DailyLogsPage projectId={projectId} />} />
          <Route path="/costs" element={<CostsBudgetPage projectId={projectId} />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/ai" element={<AiAssistantPage projectId={projectId} />} />
        </Routes>
      )}
    </Layout>
  );
}

