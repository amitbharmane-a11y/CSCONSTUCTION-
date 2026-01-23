import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type {
  AiChatRequest,
  AiChatResponse,
  BOQItem,
  BOQItemCreate,
  BudgetItem,
  BudgetItemUpsert,
  CalibrationRecord,
  CalibrationRecordCreate,
  ClaimsVariation,
  ClaimsVariationCreate,
  ComprehensiveDashboard,
  ContractCompliance,
  ContractComplianceCreate,
  CostEntry,
  CostEntryCreate,
  DailyActivity,
  DailyActivityCreate,
  DailyLog,
  DailyLogCreate,
  DashboardSummary,
  DelayReason,
  DelayReasonCreate,
  DrawingsApproval,
  DrawingsApprovalCreate,
  JobCostingSummary,
  LabourManpower,
  LabourManpowerCreate,
  MaterialInventory,
  MaterialInventoryCreate,
  MaterialProcurement,
  MaterialProcurementCreate,
  NCR,
  NCRCreate,
  PlantMachinery,
  PlantMachineryCreate,
  PortfolioOverview,
  Project,
  ProjectCreate,
  ProjectMilestone,
  ProjectMilestoneCreate,
  ProjectPackage,
  ProjectPackageCreate,
  QualityTest,
  QualityTestCreate,
  RABill,
  RABillCreate,
  RailwayBlock,
  RailwayBlockCreate,
  RFI,
  RFICreate,
  RiskRegister,
  RiskRegisterCreate,
  SafetyIncident,
  SafetyIncidentCreate,
  StakeholderIssue,
  StakeholderIssueCreate,
  SubcontractorPerformance,
  SubcontractorPerformanceCreate,
  ThirdPartyInspection,
  ThirdPartyInspectionCreate,
  ToolboxTalk,
  ToolboxTalkCreate,
  VendorPerformance,
  VendorPerformanceCreate,
  WorkPermit,
  WorkPermitCreate
} from "./types";

export function useProjects() {
  return useQuery({
    queryKey: ["projects"],
    queryFn: () => api.get<Project[]>("/projects")
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProjectCreate) => api.post<Project>("/projects", payload),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["projects"] });
    }
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (projectId: number) => api.del<{ deleted: boolean }>("/projects/" + projectId),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["projects"] });
    }
  });
}

export function useDailyLogs(projectId: number | null, fromDate?: string, toDate?: string) {
  return useQuery({
    queryKey: ["dailyLogs", projectId, fromDate, toDate],
    enabled: !!projectId,
    queryFn: () => {
      const qs = new URLSearchParams();
      if (fromDate) qs.set("from_date", fromDate);
      if (toDate) qs.set("to_date", toDate);
      const q = qs.toString() ? `?${qs.toString()}` : "";
      return api.get<DailyLog[]>(`/projects/${projectId}/daily-logs${q}`);
    }
  });
}

export function useCreateDailyLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: DailyLogCreate) => api.post<DailyLog>("/daily-logs", payload),
    onSuccess: async (log) => {
      await qc.invalidateQueries({ queryKey: ["dailyLogs", log.project_id] });
    }
  });
}

export function useDailyActivities(dailyLogId: number | null) {
  return useQuery({
    queryKey: ["dailyActivities", dailyLogId],
    enabled: !!dailyLogId,
    queryFn: () => api.get<DailyActivity[]>(`/daily-logs/${dailyLogId}/activities`)
  });
}

export function useCreateDailyActivity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: DailyActivityCreate) => api.post<DailyActivity>("/daily-activities", payload),
    onSuccess: async (act) => {
      await qc.invalidateQueries({ queryKey: ["dailyActivities", act.daily_log_id] });
    }
  });
}

export function useCosts(projectId: number | null, fromDate?: string, toDate?: string) {
  return useQuery({
    queryKey: ["costs", projectId, fromDate, toDate],
    enabled: !!projectId,
    queryFn: () => {
      const qs = new URLSearchParams();
      if (fromDate) qs.set("from_date", fromDate);
      if (toDate) qs.set("to_date", toDate);
      const q = qs.toString() ? `?${qs.toString()}` : "";
      return api.get<CostEntry[]>(`/projects/${projectId}/costs${q}`);
    }
  });
}

export function useCreateCost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CostEntryCreate) => api.post<CostEntry>("/costs", payload),
    onSuccess: async (entry) => {
      await qc.invalidateQueries({ queryKey: ["costs", entry.project_id] });
      await qc.invalidateQueries({ queryKey: ["summary", entry.project_id] });
    }
  });
}

export function useBudgets(projectId: number | null) {
  return useQuery({
    queryKey: ["budgets", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<BudgetItem[]>(`/projects/${projectId}/budgets`)
  });
}

export function useUpsertBudget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: BudgetItemUpsert) => api.post<BudgetItem>("/budgets/upsert", payload),
    onSuccess: async (item) => {
      await qc.invalidateQueries({ queryKey: ["budgets", item.project_id] });
      await qc.invalidateQueries({ queryKey: ["summary", item.project_id] });
    }
  });
}

export function useSummary(projectId: number | null, fromDate?: string, toDate?: string) {
  return useQuery({
    queryKey: ["summary", projectId, fromDate, toDate],
    enabled: !!projectId,
    queryFn: () => {
      const qs = new URLSearchParams();
      if (fromDate) qs.set("from_date", fromDate);
      if (toDate) qs.set("to_date", toDate);
      const q = qs.toString() ? `?${qs.toString()}` : "";
      return api.get<DashboardSummary>(`/projects/${projectId}/summary${q}`);
    }
  });
}

export function useAiChat() {
  return useMutation({
    mutationFn: (payload: AiChatRequest) => api.post<AiChatResponse>("/ai/chat", payload)
  });
}

export function useJobCosting(projectId: number | null, fromDate?: string, toDate?: string) {
  return useQuery({
    queryKey: ["jobCosting", projectId, fromDate, toDate],
    enabled: !!projectId,
    queryFn: () => {
      const qs = new URLSearchParams();
      if (fromDate) qs.set("from_date", fromDate);
      if (toDate) qs.set("to_date", toDate);
      const q = qs.toString() ? `?${qs.toString()}` : "";
      return api.get<JobCostingSummary>(`/projects/${projectId}/job-costing${q}`);
    }
  });
}

// Project Packages
export function useProjectPackages(projectId: number | null) {
  return useQuery({
    queryKey: ["projectPackages", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<ProjectPackage[]>(`/projects/${projectId}/packages`)
  });
}

export function useCreateProjectPackage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProjectPackageCreate) => api.post<ProjectPackage>("/project-packages", payload),
    onSuccess: async (pkg) => {
      await qc.invalidateQueries({ queryKey: ["projectPackages", pkg.project_id] });
    }
  });
}

// Project Milestones
export function useProjectMilestones(projectId: number | null) {
  return useQuery({
    queryKey: ["projectMilestones", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<ProjectMilestone[]>(`/projects/${projectId}/milestones`)
  });
}

export function useCreateProjectMilestone() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProjectMilestoneCreate) => api.post<ProjectMilestone>("/project-milestones", payload),
    onSuccess: async (ms) => {
      await qc.invalidateQueries({ queryKey: ["projectMilestones", ms.project_id] });
    }
  });
}

// RA Bills
export function useRABills(projectId: number | null) {
  return useQuery({
    queryKey: ["raBills", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<RABill[]>(`/projects/${projectId}/ra-bills`)
  });
}

export function useCreateRABill() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: RABillCreate) => api.post<RABill>("/ra-bills", payload),
    onSuccess: async (bill) => {
      await qc.invalidateQueries({ queryKey: ["raBills", bill.project_id] });
    }
  });
}

// Quality Tests
export function useQualityTests(projectId: number | null) {
  return useQuery({
    queryKey: ["qualityTests", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<QualityTest[]>(`/projects/${projectId}/quality-tests`)
  });
}

export function useCreateQualityTest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: QualityTestCreate) => api.post<QualityTest>("/quality-tests", payload),
    onSuccess: async (test) => {
      await qc.invalidateQueries({ queryKey: ["qualityTests", test.project_id] });
    }
  });
}

// NCRs
export function useNCRs(projectId: number | null) {
  return useQuery({
    queryKey: ["ncrs", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<NCR[]>(`/projects/${projectId}/ncrs`)
  });
}

export function useCreateNCR() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: NCRCreate) => api.post<NCR>("/ncrs", payload),
    onSuccess: async (ncr) => {
      await qc.invalidateQueries({ queryKey: ["ncrs", ncr.project_id] });
    }
  });
}

// Safety Incidents
export function useSafetyIncidents(projectId: number | null) {
  return useQuery({
    queryKey: ["safetyIncidents", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<SafetyIncident[]>(`/projects/${projectId}/safety-incidents`)
  });
}

export function useCreateSafetyIncident() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: SafetyIncidentCreate) => api.post<SafetyIncident>("/safety-incidents", payload),
    onSuccess: async (incident) => {
      await qc.invalidateQueries({ queryKey: ["safetyIncidents", incident.project_id] });
    }
  });
}

// Labour Manpower
export function useLabourManpower(projectId: number | null) {
  return useQuery({
    queryKey: ["labourManpower", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<LabourManpower[]>(`/projects/${projectId}/labour-manpower`)
  });
}

export function useCreateLabourManpower() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: LabourManpowerCreate) => api.post<LabourManpower>("/labour-manpower", payload),
    onSuccess: async (lm) => {
      await qc.invalidateQueries({ queryKey: ["labourManpower", lm.project_id] });
    }
  });
}

// Plant & Machinery
export function usePlantMachinery(projectId: number | null) {
  return useQuery({
    queryKey: ["plantMachinery", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<PlantMachinery[]>(`/projects/${project_id}/plant-machinery`)
  });
}

export function useCreatePlantMachinery() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: PlantMachineryCreate) => api.post<PlantMachinery>("/plant-machinery", payload),
    onSuccess: async (pm) => {
      await qc.invalidateQueries({ queryKey: ["plantMachinery", pm.project_id] });
    }
  });
}

// Material Inventory
export function useMaterialInventory(projectId: number | null) {
  return useQuery({
    queryKey: ["materialInventory", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<MaterialInventory[]>(`/projects/${projectId}/material-inventory`)
  });
}

export function useCreateMaterialInventory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: MaterialInventoryCreate) => api.post<MaterialInventory>("/material-inventory", payload),
    onSuccess: async (mi) => {
      await qc.invalidateQueries({ queryKey: ["materialInventory", mi.project_id] });
    }
  });
}

// Drawings & Approvals
export function useDrawingsApprovals(projectId: number | null) {
  return useQuery({
    queryKey: ["drawingsApprovals", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<DrawingsApproval[]>(`/projects/${projectId}/drawings-approvals`)
  });
}

export function useCreateDrawingsApproval() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: DrawingsApprovalCreate) => api.post<DrawingsApproval>("/drawings-approvals", payload),
    onSuccess: async (da) => {
      await qc.invalidateQueries({ queryKey: ["drawingsApprovals", da.project_id] });
    }
  });
}

// Railway Blocks
export function useRailwayBlocks(projectId: number | null) {
  return useQuery({
    queryKey: ["railwayBlocks", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<RailwayBlock[]>(`/projects/${projectId}/railway-blocks`)
  });
}

export function useCreateRailwayBlock() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: RailwayBlockCreate) => api.post<RailwayBlock>("/railway-blocks", payload),
    onSuccess: async (rb) => {
      await qc.invalidateQueries({ queryKey: ["railwayBlocks", rb.project_id] });
    }
  });
}

// Risk Register
export function useRiskRegister(projectId: number | null) {
  return useQuery({
    queryKey: ["riskRegister", projectId],
    enabled: !!projectId,
    queryFn: () => api.get<RiskRegister[]>(`/projects/${projectId}/risk-register`)
  });
}

export function useCreateRiskRegister() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: RiskRegisterCreate) => api.post<RiskRegister>("/risk-register", payload),
    onSuccess: async (rr) => {
      await qc.invalidateQueries({ queryKey: ["riskRegister", rr.project_id] });
    }
  });
}// Portfolio Overview
export function usePortfolioOverview() {
  return useQuery({
    queryKey: ["portfolioOverview"],
    queryFn: () => api.get<PortfolioOverview>("/portfolio-overview")
  });
}