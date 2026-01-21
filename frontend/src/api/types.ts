export type Project = {
  id: number;
  name: string;
  client: string;
  location: string;
  contract_no?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  created_at: string;
};

export type ProjectCreate = Omit<Project, "id" | "created_at">;

export type DailyLog = {
  id: number;
  project_id: number;
  log_date: string;
  weather?: string | null;
  remarks?: string | null;
  created_at: string;
};

export type DailyLogCreate = Omit<DailyLog, "id" | "created_at">;

export type DailyActivity = {
  id: number;
  daily_log_id: number;
  category: string;
  activity: string;
  uom: string;
  quantity: number;
  labour_count: number;
  machinery?: string | null;
  notes?: string | null;
};

export type DailyActivityCreate = Omit<DailyActivity, "id">;

export type CostEntry = {
  id: number;
  project_id: number;
  entry_date: string;
  cost_head: string;
  description: string;
  vendor?: string | null;
  amount: number;
  quantity?: number | null;
  uom?: string | null;
  unit_rate?: number | null;
  payment_mode?: string | null;
  bill_no?: string | null;
  created_at: string;
};

export type CostEntryCreate = Omit<CostEntry, "id" | "created_at">;

export type BudgetItem = {
  id: number;
  project_id: number;
  cost_head: string;
  budget_amount: number;
  notes?: string | null;
  created_at: string;
};

export type BudgetItemUpsert = Omit<BudgetItem, "id" | "created_at">;

export type DashboardSummary = {
  project_id: number;
  from_date?: string | null;
  to_date?: string | null;
  total_cost: number;
  cost_by_head: Record<string, number>;
  total_budget: number;
  budget_by_head: Record<string, number>;
  variance_by_head: Record<string, number>;
  recent_logs: DailyLog[];
};

export type AiChatRequest = {
  project_id: number;
  question: string;
  from_date?: string | null;
  to_date?: string | null;
};

export type AiChatResponse = {
  mode: "online" | "offline";
  answer: string;
};

export type JobCostingCategory = {
  category: string; // Labour / Materials / Equipment / Subcontractors / Other
  planned_cost: number;
  actual_cost: number;
  quantity?: number | null;
  uom?: string | null;
  unit_cost?: number | null;
  percent_of_total_actual: number;
  percent_over_under_budget?: number | null;
};

export type JobCostingSummary = {
  project_id: number;
  project_name: string;
  client: string;
  location: string;
  from_date?: string | null;
  to_date?: string | null;
  total_planned_cost: number;
  total_actual_cost: number;
  percent_over_under_budget?: number | null;
  categories: JobCostingCategory[];
};

export type JobCostingCategory = {
  category: "Labour" | "Materials" | "Equipment" | "Subcontractors" | "Other" | string;
  planned_cost: number;
  actual_cost: number;
  quantity?: number | null;
  uom?: string | null;
  unit_cost?: number | null;
  percent_of_total_actual: number;
  percent_over_under_budget?: number | null;
};

export type JobCostingSummary = {
  project_id: number;
  project_name: string;
  client: string;
  location: string;
  from_date?: string | null;
  to_date?: string | null;
  total_planned_cost: number;
  total_actual_cost: number;
  percent_over_under_budget?: number | null;
  categories: JobCostingCategory[];
};

