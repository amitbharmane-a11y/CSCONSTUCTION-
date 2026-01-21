from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2)
    client: str
    location: str
    contract_no: str | None = None
    start_date: str | None = None  # YYYY-MM-DD
    end_date: str | None = None
    total_contract_value: float | None = None
    profit_margin_target: float = 10.0


class Project(ProjectCreate):
    id: int
    created_at: str


class DailyLogCreate(BaseModel):
    project_id: int
    log_date: str  # YYYY-MM-DD
    weather: str | None = None
    remarks: str | None = None


class DailyLog(DailyLogCreate):
    id: int
    created_at: str


class DailyActivityCreate(BaseModel):
    daily_log_id: int
    category: str
    activity: str
    uom: str
    quantity: float = 0
    labour_count: int = 0
    machinery: str | None = None
    notes: str | None = None


class DailyActivity(DailyActivityCreate):
    id: int


class CostEntryCreate(BaseModel):
    project_id: int
    entry_date: str
    cost_head: str
    description: str
    vendor: str | None = None
    amount: float
    quantity: float | None = None
    uom: str | None = None
    unit_rate: float | None = None
    payment_mode: str | None = None
    bill_no: str | None = None


class CostEntry(CostEntryCreate):
    id: int
    created_at: str


class BudgetItemUpsert(BaseModel):
    project_id: int
    cost_head: str
    budget_amount: float
    notes: str | None = None


class BudgetItem(BudgetItemUpsert):
    id: int
    created_at: str


class DashboardSummary(BaseModel):
    project_id: int
    from_date: str | None = None
    to_date: str | None = None
    total_cost: float
    cost_by_head: dict[str, float]
    total_budget: float
    budget_by_head: dict[str, float]
    variance_by_head: dict[str, float]
    percent_over_under_budget: float | None = None
    total_contract_value: float | None = None
    profit_margin_target: float = 10.0
    current_profit_margin: float | None = None
    days_remaining: int | None = None
    job_costing_categories: list[JobCostingCategory] = []
    recent_logs: list[DailyLog]


class AiChatRequest(BaseModel):
    project_id: int
    question: str
    from_date: str | None = None
    to_date: str | None = None


class AiChatResponse(BaseModel):
    mode: str  # "online" | "offline"
    answer: str


class JobCostingCategory(BaseModel):
    category: str
    planned_cost: float
    actual_cost: float
    quantity: float | None = None
    uom: str | None = None
    unit_cost: float | None = None
    percent_of_total_actual: float
    percent_over_under_budget: float | None = None


class JobCostingSummary(BaseModel):
    project_id: int
    project_name: str
    client: str
    location: str
    from_date: str | None = None
    to_date: str | None = None
    total_planned_cost: float
    total_actual_cost: float
    percent_over_under_budget: float | None = None
    categories: list[JobCostingCategory]


# ===== COMPREHENSIVE KPI SCHEMAS =====

# Project Packages
class ProjectPackageCreate(BaseModel):
    project_id: int
    package_name: str
    package_value: float = 0
    planned_start_date: str | None = None
    planned_end_date: str | None = None
    actual_start_date: str | None = None
    actual_end_date: str | None = None
    status: str = "Not Started"
    progress_percentage: float = 0

class ProjectPackage(ProjectPackageCreate):
    id: int
    created_at: str

# Project Progress KPIs
class ProjectMilestoneCreate(BaseModel):
    project_id: int
    milestone_name: str
    planned_date: str | None = None
    actual_date: str | None = None
    status: str = "Planned"
    weight: float = 0
    description: str | None = None

class ProjectMilestone(ProjectMilestoneCreate):
    id: int
    created_at: str

class DelayReasonCreate(BaseModel):
    project_id: int
    delay_date: str
    delay_category: str
    delay_hours: float = 0
    delay_days: float = 0
    description: str | None = None
    impact_on_schedule: str | None = None
    mitigation_action: str | None = None
    status: str = "Active"

class DelayReason(DelayReasonCreate):
    id: int
    created_at: str

# Cost & Billing KPIs
class RABillCreate(BaseModel):
    project_id: int
    bill_no: str
    bill_date: str | None = None
    submitted_date: str | None = None
    certified_date: str | None = None
    paid_date: str | None = None
    bill_amount: float = 0
    certified_amount: float = 0
    paid_amount: float = 0
    retention_amount: float = 0
    status: str = "Draft"
    certification_cycle_days: int | None = None
    payment_cycle_days: int | None = None

class RABill(RABillCreate):
    id: int
    created_at: str

class ClaimsVariationCreate(BaseModel):
    project_id: int
    claim_type: str
    description: str | None = None
    claimed_amount: float = 0
    approved_amount: float = 0
    status: str = "Submitted"
    submitted_date: str | None = None
    approved_date: str | None = None
    remarks: str | None = None

class ClaimsVariation(ClaimsVariationCreate):
    id: int
    created_at: str

# Quantity & BOQ Control
class BOQItemCreate(BaseModel):
    project_id: int
    item_code: str | None = None
    item_description: str
    unit: str | None = None
    boq_quantity: float = 0
    boq_rate: float = 0
    boq_amount: float = 0
    executed_quantity: float = 0
    executed_amount: float = 0
    deviation_percentage: float = 0
    status: str = "Active"
    category: str | None = None

class BOQItem(BOQItemCreate):
    id: int
    created_at: str

# Quality KPIs
class QualityTestCreate(BaseModel):
    project_id: int
    test_type: str
    test_date: str | None = None
    planned_tests: int = 0
    conducted_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    pass_rate: float = 0
    status: str = "Planned"

class QualityTest(QualityTestCreate):
    id: int
    created_at: str

class NCRCreate(BaseModel):
    project_id: int
    ncr_no: str
    raised_date: str | None = None
    category: str | None = None
    description: str | None = None
    severity: str = "Minor"
    status: str = "Open"
    closure_date: str | None = None
    closure_days: int | None = None
    corrective_action: str | None = None

class NCR(NCRCreate):
    id: int
    created_at: str

class ThirdPartyInspectionCreate(BaseModel):
    project_id: int
    inspection_type: str
    scheduled_date: str | None = None
    conducted_date: str | None = None
    status: str = "Scheduled"
    inspector_name: str | None = None
    remarks: str | None = None

class ThirdPartyInspection(ThirdPartyInspectionCreate):
    id: int
    created_at: str

class CalibrationRecordCreate(BaseModel):
    project_id: int
    equipment_name: str
    equipment_type: str | None = None
    last_calibration_date: str | None = None
    next_due_date: str | None = None
    status: str = "Valid"
    days_to_expiry: int | None = None
    calibration_agency: str | None = None
    certificate_no: str | None = None

class CalibrationRecord(CalibrationRecordCreate):
    id: int
    created_at: str
    updated_at: str

# Safety KPIs
class SafetyIncidentCreate(BaseModel):
    project_id: int
    incident_date: str | None = None
    incident_type: str | None = None
    description: str | None = None
    severity: str = "Minor"
    lost_time_days: int = 0
    reported_by: str | None = None
    status: str = "Reported"

class SafetyIncident(SafetyIncidentCreate):
    id: int
    created_at: str

class ToolboxTalkCreate(BaseModel):
    project_id: int
    talk_date: str | None = None
    topic: str | None = None
    conducted_by: str | None = None
    attendees_count: int = 0
    planned_talks: int = 0
    conducted_talks: int = 0
    status: str = "Completed"

class ToolboxTalk(ToolboxTalkCreate):
    id: int
    created_at: str

class WorkPermitCreate(BaseModel):
    project_id: int
    permit_type: str | None = None
    permit_date: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    work_location: str | None = None
    hazards_identified: str | None = None
    ppe_required: str | None = None
    status: str = "Active"
    issued_by: str | None = None
    approved_by: str | None = None

class WorkPermit(WorkPermitCreate):
    id: int
    created_at: str

# Labour & Productivity KPIs
class LabourManpowerCreate(BaseModel):
    project_id: int
    record_date: str
    total_planned: int = 0
    total_actual: int = 0
    mason_count: int = 0
    carpenter_count: int = 0
    bar_bender_count: int = 0
    welder_count: int = 0
    helper_count: int = 0
    absenteeism_rate: float = 0
    overtime_hours: float = 0

class LabourManpower(LabourManpowerCreate):
    id: int
    created_at: str

class SubcontractorPerformanceCreate(BaseModel):
    project_id: int
    subcontractor_name: str
    evaluation_date: str | None = None
    progress_rating: float = 0
    quality_rating: float = 0
    safety_rating: float = 0
    overall_rating: float = 0
    remarks: str | None = None

class SubcontractorPerformance(SubcontractorPerformanceCreate):
    id: int
    created_at: str

# Plant & Machinery KPIs
class PlantMachineryCreate(BaseModel):
    project_id: int
    equipment_name: str
    equipment_type: str | None = None
    record_date: str | None = None
    available_hours: float = 0
    utilized_hours: float = 0
    breakdown_hours: float = 0
    idle_hours: float = 0
    fuel_consumed: float = 0
    fuel_norm: float = 0
    availability_percentage: float = 0
    utilization_percentage: float = 0
    mttr_hours: float = 0
    mtbf_hours: float = 0

class PlantMachinery(PlantMachineryCreate):
    id: int
    created_at: str

# Materials & Supply Chain KPIs
class MaterialInventoryCreate(BaseModel):
    project_id: int
    material_type: str
    record_date: str | None = None
    issued_quantity: float = 0
    consumed_quantity: float = 0
    theoretical_quantity: float = 0
    variance_percentage: float = 0
    stock_level: float = 0
    min_stock: float = 0
    max_stock: float = 0
    status: str = "Normal"

class MaterialInventory(MaterialInventoryCreate):
    id: int
    created_at: str

class MaterialProcurementCreate(BaseModel):
    project_id: int
    material_type: str
    po_no: str | None = None
    po_date: str | None = None
    vendor_name: str | None = None
    ordered_quantity: float = 0
    delivered_quantity: float = 0
    lead_time_days: int = 0
    delivery_date: str | None = None
    on_time_delivery: bool = False
    quality_status: str = "Pending"

class MaterialProcurement(MaterialProcurementCreate):
    id: int
    created_at: str

class VendorPerformanceCreate(BaseModel):
    project_id: int
    vendor_name: str
    material_type: str | None = None
    evaluation_date: str | None = None
    delivery_rating: float = 0
    quality_rating: float = 0
    price_rating: float = 0
    overall_score: float = 0
    on_time_delivery_rate: float = 0
    remarks: str | None = None

class VendorPerformance(VendorPerformanceCreate):
    id: int
    created_at: str

# Approvals, Drawings & Communication KPIs
class DrawingsApprovalCreate(BaseModel):
    project_id: int
    drawing_no: str
    drawing_type: str | None = None
    submitted_date: str | None = None
    approved_date: str | None = None
    approval_days: int | None = None
    status: str = "Submitted"
    approver_name: str | None = None
    remarks: str | None = None

class DrawingsApproval(DrawingsApprovalCreate):
    id: int
    created_at: str

class RFICreate(BaseModel):
    project_id: int
    rfi_no: str
    raised_date: str | None = None
    subject: str | None = None
    description: str | None = None
    closure_date: str | None = None
    closure_days: int | None = None
    status: str = "Open"
    response_by: str | None = None

class RFI(RFICreate):
    id: int
    created_at: str

class RailwayBlockCreate(BaseModel):
    project_id: int
    block_date: str | None = None
    block_type: str | None = None
    requested_hours: float = 0
    granted_hours: float = 0
    utilized_hours: float = 0
    status: str = "Requested"
    work_description: str | None = None

class RailwayBlock(RailwayBlockCreate):
    id: int
    created_at: str

# Contract Compliance KPIs
class ContractComplianceCreate(BaseModel):
    project_id: int
    compliance_type: str
    description: str | None = None
    due_date: str | None = None
    status: str = "Active"
    expiry_date: str | None = None
    days_to_expiry: int | None = None
    amount: float = 0
    remarks: str | None = None

class ContractCompliance(ContractComplianceCreate):
    id: int
    created_at: str
    updated_at: str

# Risk & Stakeholder KPIs
class RiskRegisterCreate(BaseModel):
    project_id: int
    risk_description: str
    risk_category: str | None = None
    probability: str = "Medium"
    impact: str = "Medium"
    risk_level: str = "Medium"
    exposure_amount: float = 0
    exposure_days: int = 0
    mitigation_plan: str | None = None
    mitigation_status: str = "Planned"
    rag_status: str = "Amber"
    owner: str | None = None

class RiskRegister(RiskRegisterCreate):
    id: int
    created_at: str
    updated_at: str

class StakeholderIssueCreate(BaseModel):
    project_id: int
    issue_type: str | None = None
    description: str | None = None
    raised_date: str | None = None
    resolved_date: str | None = None
    resolution_days: int | None = None
    status: str = "Open"
    priority: str = "Medium"
    raised_by: str | None = None
    assigned_to: str | None = None

class StakeholderIssue(StakeholderIssueCreate):
    id: int
    created_at: str

# ===== DASHBOARD SUMMARY SCHEMAS =====

class ProgressKPISummary(BaseModel):
    project_id: int
    overall_progress: float
    spi: float | None = None
    schedule_variance_days: int | None = None
    milestone_achievement_rate: float
    critical_activities_pending: int
    delay_reasons: dict[str, float]  # category -> delay_days

class CostBillingKPISummary(BaseModel):
    project_id: int
    budget_variance_percentage: float | None = None
    cpi: float | None = None
    ra_bills_submitted: int
    ra_bills_certified: int
    ra_bills_paid: int
    outstanding_receivables: float
    retention_held: float
    certification_cycle_avg: float | None = None
    payment_cycle_avg: float | None = None
    claims_submitted: float
    claims_settled: float

class QualitySafetyKPISummary(BaseModel):
    project_id: int
    quality_tests_planned: int
    quality_tests_conducted: int
    quality_pass_rate: float
    ncrs_raised: int
    ncrs_closed: int
    ncr_closure_avg_days: float | None = None
    rework_rate: float | None = None
    total_incidents: int
    ltifr: float | None = None
    toolbox_talks_conducted: int
    safety_audits_completed: int
    third_party_inspections_pending: int
    calibration_overdue: int

class LabourProductivityKPISummary(BaseModel):
    project_id: int
    manpower_deployed: int
    manpower_planned: int
    skill_mix: dict[str, int]
    absenteeism_rate: float
    overtime_hours: float
    productivity_rates: dict[str, float]
    subcontractor_avg_rating: float | None = None

class MachineryMaterialsKPISummary(BaseModel):
    project_id: int
    equipment_availability_avg: float
    equipment_utilization_avg: float
    breakdown_mttr_avg: float | None = None
    material_lead_time_avg: int | None = None
    stockout_incidents: int
    on_time_delivery_rate: float
    vendor_performance_avg: float | None = None
    material_variance_percentage: float

class ApprovalsComplianceKPISummary(BaseModel):
    project_id: int
    drawings_submitted: int
    drawings_approved: int
    rfis_raised: int
    rfis_closed: int
    rfi_closure_avg_days: float | None = None
    railway_blocks_requested: float
    railway_blocks_granted: float
    railway_blocks_utilized: float
    permits_pending: int
    eot_status: str
    liquidated_damages_risk: float
    security_deposit_expiry_days: int | None = None
    insurance_expiry_days: int | None = None

class RiskStakeholderKPISummary(BaseModel):
    project_id: int
    top_risks: list[dict]
    risk_exposure_total: float
    mitigation_actions_overdue: int
    client_inspections_passed: int
    audit_observations_open: int
    stakeholder_issues_open: int
    stakeholder_issues_resolved: int

class PortfolioOverview(BaseModel):
    total_projects: int
    active_projects: int
    delayed_projects: int
    total_contract_value: float
    total_billed_value: float
    overall_progress: float
    safety_incidents_total: int
    quality_ncrs_total: int
    projects_by_client: dict[str, int]
    projects_by_status: dict[str, int]

class ComprehensiveDashboard(BaseModel):
    project_id: int
    project_name: str
    client: str
    progress_kpis: ProgressKPISummary
    cost_billing_kpis: CostBillingKPISummary
    quality_safety_kpis: QualitySafetyKPISummary
    labour_productivity_kpis: LabourProductivityKPISummary
    machinery_materials_kpis: MachineryMaterialsKPISummary
    approvals_compliance_kpis: ApprovalsComplianceKPISummary
    risk_stakeholder_kpis: RiskStakeholderKPISummary

