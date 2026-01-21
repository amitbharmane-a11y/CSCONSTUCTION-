import { useEffect, useMemo, useState } from "react";

const LS_PROJECT_ID = "csdash:selectedProjectId";

export function useSelectedProjectId(projectIds: number[]) {
  const [projectId, setProjectId] = useState<number | null>(() => {
    const raw = localStorage.getItem(LS_PROJECT_ID);
    const parsed = raw ? Number(raw) : NaN;
    return Number.isFinite(parsed) ? parsed : null;
  });

  // If project list loads and there's no selection, pick first
  useEffect(() => {
    if (!projectId && projectIds.length > 0) setProjectId(projectIds[0]);
  }, [projectId, projectIds]);

  useEffect(() => {
    if (projectId) localStorage.setItem(LS_PROJECT_ID, String(projectId));
  }, [projectId]);

  const safeProjectId = useMemo(() => {
    if (!projectId) return null;
    if (projectIds.length === 0) return null;
    return projectIds.includes(projectId) ? projectId : projectIds[0];
  }, [projectId, projectIds]);

  return { projectId: safeProjectId, setProjectId };
}

