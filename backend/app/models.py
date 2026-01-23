from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


# Base model with common fields
class BaseDocument(Document):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        use_revision = True
        use_state_management = True


# Core Project Management Models
class Project(BaseDocument):
    name: str
    client: str
    location: str
    contract_no: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_contract_value: Optional[float] = None
    profit_margin_target: float = 10.0
    contract_completion_date: Optional[str] = None
    project_manager: Optional[str] = None
    site_engineer: Optional[str] = None
    status: str = "active"

    class Settings:
        name = "projects"


class DailyLog(BaseDocument):
    project_id: str
    log_date: str
    weather: Optional[str] = None
    remarks: Optional[str] = None

    class Settings:
        name = "daily_logs"


class DailyActivity(BaseDocument):
    daily_log_id: str
    category: str
    activity: str
    uom: str
    quantity: float = 0
    labour_count: int = 0
    machinery: Optional[str] = None
    notes: Optional[str] = None

    class Settings:
        name = "daily_activities"


class CostEntry(BaseDocument):
    project_id: str
    entry_date: str
    cost_head: str
    description: str
    vendor: Optional[str] = None
    amount: float
    quantity: Optional[float] = None
    uom: Optional[str] = None
    unit_rate: Optional[float] = None
    payment_mode: Optional[str] = None
    bill_no: Optional[str] = None

    class Settings:
        name = "cost_entries"


class BudgetItem(BaseDocument):
    project_id: str
    cost_head: str
    budget_amount: float
    notes: Optional[str] = None

    class Settings:
        name = "budget_items"


# Project Progress KPIs
class ProjectPackage(BaseDocument):
    project_id: str
    package_name: str
    planned_value: Optional[float] = None
    actual_value: Optional[float] = None
    progress_percentage: Optional[float] = None

    class Settings:
        name = "project_packages"


class ProjectMilestone(BaseDocument):
    project_id: str
    milestone_name: str
    planned_date: Optional[str] = None
    actual_date: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, delayed

    class Settings:
        name = "project_milestones"


# Cost & Billing KPIs
class RABill(BaseDocument):
    project_id: str
    bill_no: str
    bill_date: str
    bill_amount: float
    certified_amount: Optional[float] = None
    paid_amount: Optional[float] = None
    payment_date: Optional[str] = None
    status: str = "submitted"  # submitted, certified, paid

    class Settings:
        name = "ra_bills"


# Quality KPIs
class QualityTest(BaseDocument):
    project_id: str
    test_type: str
    planned_tests: int = 0
    conducted_tests: int = 0
    passed_tests: int = 0
    pass_rate: Optional[float] = None
    status: str = "planned"  # planned, ongoing, completed

    class Settings:
        name = "quality_tests"


class NCR(BaseDocument):
    project_id: str
    ncr_no: str
    description: str
    raised_date: str
    category: str = "Quality"
    severity: str = "Medium"  # Low, Medium, High
    status: str = "Open"  # Open, Closed
    closure_date: Optional[str] = None

    class Settings:
        name = "ncrs"


# Safety KPIs
class SafetyIncident(BaseDocument):
    project_id: str
    incident_no: str
    incident_date: str
    incident_type: str  # Near Miss, First Aid, Medical Treatment, Lost Time Injury, etc.
    description: str
    severity: str = "Low"  # Low, Medium, High
    status: str = "Open"  # Open, Closed
    action_taken: Optional[str] = None

    class Settings:
        name = "safety_incidents"


class ToolboxTalk(BaseDocument):
    project_id: str
    talk_date: str
    topic: str
    attendees_count: int = 0
    conducted_by: Optional[str] = None

    class Settings:
        name = "toolbox_talks"


# Labour & Productivity KPIs
class LabourManpower(BaseDocument):
    project_id: str
    recorded_date: str
    planned_manpower: int = 0
    actual_manpower: int = 0
    mason_count: int = 0
    carpenter_count: int = 0
    bar_bender_count: int = 0
    welder_count: int = 0
    absenteeism_rate: Optional[float] = None
    overtime_hours: Optional[float] = None

    class Settings:
        name = "labour_manpower"


class SubcontractorPerformance(BaseDocument):
    project_id: str
    subcontractor_name: str
    work_package: str
    progress_rating: float = 0  # 1-5 scale
    quality_rating: float = 0  # 1-5 scale
    safety_rating: float = 0  # 1-5 scale
    overall_rating: float = 0  # 1-5 scale

    class Settings:
        name = "subcontractor_performance"


# Plant & Machinery KPIs
class PlantMachinery(BaseDocument):
    project_id: str
    equipment_name: str
    equipment_type: str
    availability_percentage: float = 0
    utilization_percentage: float = 0
    breakdown_hours: float = 0
    idle_time_causes: Optional[str] = None

    class Settings:
        name = "plant_machinery"


# Materials & Supply Chain KPIs
class MaterialInventory(BaseDocument):
    project_id: str
    material_name: str
    current_stock: float = 0
    min_stock: float = 0
    max_stock: float = 0
    unit: str
    stock_value: Optional[float] = None
    lead_time_days: Optional[int] = None

    class Settings:
        name = "material_inventory"


class MaterialProcurement(BaseDocument):
    project_id: str
    material_name: str
    po_date: str
    delivery_date: Optional[str] = None
    quantity_ordered: float = 0
    quantity_received: float = 0
    unit: str
    lead_time_days: Optional[int] = None

    class Settings:
        name = "material_procurement"


class VendorPerformance(BaseDocument):
    project_id: str
    vendor_name: str
    material_type: str
    on_time_delivery_rate: float = 0  # percentage
    quality_rating: float = 0  # 1-5 scale
    overall_score: float = 0  # 1-5 scale

    class Settings:
        name = "vendor_performance"


# Approvals, Drawings & Communication KPIs
class DrawingsApproval(BaseDocument):
    project_id: str
    drawing_no: str
    drawing_title: str
    submitted_date: str
    approved_date: Optional[str] = None
    status: str = "submitted"  # submitted, approved, rejected

    class Settings:
        name = "drawings_approvals"


class RFI(BaseDocument):
    project_id: str
    rfi_no: str
    subject: str
    raised_date: str
    response_date: Optional[str] = None
    status: str = "open"  # open, closed

    class Settings:
        name = "rfis"


# Railway-specific models
class RailwayBlock(BaseDocument):
    project_id: str
    block_date: str
    block_type: str  # Complete block, Weekend block, Night block
    duration_hours: float = 0
    status: str = "requested"  # requested, approved, utilized

    class Settings:
        name = "railway_blocks"


# Contract Compliance KPIs
class ContractCompliance(BaseDocument):
    project_id: str
    compliance_type: str
    description: str
    due_date: Optional[str] = None
    status: str = "pending"  # pending, compliant, non-compliant

    class Settings:
        name = "contract_compliance"


# Risk Management KPIs
class RiskRegister(BaseDocument):
    project_id: str
    risk_description: str
    risk_category: str
    probability: str = "Medium"  # Low, Medium, High
    impact: str = "Medium"  # Low, Medium, High
    risk_level: str = "Medium"  # Low, Medium, High
    mitigation_plan: Optional[str] = None
    status: str = "active"  # active, mitigated, closed

    class Settings:
        name = "risk_register"


# BOQ & Quantity Control
class BOQItem(BaseDocument):
    project_id: str
    item_code: str
    item_description: str
    unit: str
    boq_quantity: float = 0
    executed_quantity: float = 0
    deviation_percentage: Optional[float] = None

    class Settings:
        name = "boq_items"


# Quality Control Records
class CalibrationRecord(BaseDocument):
    project_id: str
    equipment_name: str
    calibration_date: str
    next_calibration_date: str
    status: str = "valid"  # valid, due, overdue

    class Settings:
        name = "calibration_records"


class ThirdPartyInspection(BaseDocument):
    project_id: str
    inspection_type: str
    scheduled_date: str
    completed_date: Optional[str] = None
    status: str = "scheduled"  # scheduled, completed, pending

    class Settings:
        name = "third_party_inspections"


# Claims & Variations
class ClaimsVariation(BaseDocument):
    project_id: str
    claim_no: str
    claim_type: str
    description: str
    claimed_amount: float = 0
    approved_amount: Optional[float] = None
    status: str = "submitted"  # submitted, approved, rejected

    class Settings:
        name = "claims_variations"


# Delay Analysis
class DelayReason(BaseDocument):
    project_id: str
    delay_type: str  # Land, Traffic blocks, Drawings, Materials, Labour, Power, Weather
    description: str
    start_date: str
    end_date: Optional[str] = None
    delay_days: int = 0

    class Settings:
        name = "delay_reasons"


# Stakeholder Management
class StakeholderIssue(BaseDocument):
    project_id: str
    issue_type: str
    description: str
    raised_date: str
    resolution_date: Optional[str] = None
    status: str = "open"  # open, resolved

    class Settings:
        name = "stakeholder_issues"


# Work Permits & Safety
class WorkPermit(BaseDocument):
    project_id: str
    permit_type: str  # Height work, Lifting, Electrical, Confined space
    requested_date: str
    approved_date: Optional[str] = None
    status: str = "requested"  # requested, approved, completed

    class Settings:
        name = "work_permits"