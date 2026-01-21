-- Comprehensive Construction Project Management Database Schema

-- Departments and Zones
CREATE TABLE IF NOT EXISTS departments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE, -- PWD, Indian Railways, MSRDC, etc.
  code TEXT UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS zones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  department_id INTEGER NOT NULL,
  zone_name TEXT NOT NULL,
  zone_code TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(department_id) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS divisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  zone_id INTEGER NOT NULL,
  division_name TEXT NOT NULL,
  division_code TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(zone_id) REFERENCES zones(id)
);

CREATE TABLE IF NOT EXISTS sub_divisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  division_id INTEGER NOT NULL,
  sub_division_name TEXT NOT NULL,
  sub_division_code TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(division_id) REFERENCES divisions(id)
);

-- Work Types and Funding
CREATE TABLE IF NOT EXISTS work_types (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE, -- Building, Road, Bridge, Track, Station, etc.
  category TEXT, -- Civil, Electrical, Mechanical, etc.
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS funding_heads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  code TEXT UNIQUE,
  department_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(department_id) REFERENCES departments(id)
);

-- Contractors
CREATE TABLE IF NOT EXISTS contractors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  contractor_code TEXT UNIQUE,
  gst_no TEXT,
  pan_no TEXT,
  contact_person TEXT,
  phone TEXT,
  email TEXT,
  address TEXT,
  is_jv INTEGER DEFAULT 0, -- 0=false, 1=true
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS subcontractors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contractor_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  work_type TEXT,
  contact_person TEXT,
  phone TEXT,
  email TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(contractor_id) REFERENCES contractors(id)
);

-- Core Projects Table (Enhanced)
CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  work_order_no TEXT,
  agreement_no TEXT,
  department_id INTEGER,
  zone_id INTEGER,
  division_id INTEGER,
  sub_division_id INTEGER,
  contractor_id INTEGER,
  is_jv INTEGER DEFAULT 0,
  work_type_id INTEGER,
  funding_head_id INTEGER,
  location TEXT NOT NULL,
  start_date TEXT,
  planned_finish_date TEXT,
  revised_finish_date TEXT,
  contract_value REAL DEFAULT 0,
  original_boq_value REAL DEFAULT 0,
  revised_boq_value REAL DEFAULT 0,
  project_manager TEXT,
  site_engineer TEXT,
  status TEXT DEFAULT 'Planning',
  physical_progress REAL DEFAULT 0,
  financial_progress REAL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(department_id) REFERENCES departments(id),
  FOREIGN KEY(zone_id) REFERENCES zones(id),
  FOREIGN KEY(division_id) REFERENCES divisions(id),
  FOREIGN KEY(sub_division_id) REFERENCES sub_divisions(id),
  FOREIGN KEY(contractor_id) REFERENCES contractors(id),
  FOREIGN KEY(work_type_id) REFERENCES work_types(id),
  FOREIGN KEY(funding_head_id) REFERENCES funding_heads(id)
);

-- Contract & Scope Management (BOQ)
CREATE TABLE IF NOT EXISTS boq_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  item_code TEXT,
  item_description TEXT NOT NULL,
  unit TEXT,
  boq_quantity REAL DEFAULT 0,
  boq_rate REAL DEFAULT 0,
  boq_amount REAL DEFAULT 0,
  revised_quantity REAL DEFAULT 0,
  revised_rate REAL DEFAULT 0,
  revised_amount REAL DEFAULT 0,
  executed_quantity REAL DEFAULT 0,
  executed_amount REAL DEFAULT 0,
  deviation_percentage REAL DEFAULT 0,
  item_type TEXT DEFAULT 'Original', -- Original, Extra, Substituted
  scope_change_notes TEXT,
  approval_reference TEXT,
  status TEXT DEFAULT 'Active',
  category TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Planning & Schedule (Baseline vs Actual)
CREATE TABLE IF NOT EXISTS project_milestones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  milestone_name TEXT NOT NULL,
  baseline_date TEXT,
  actual_date TEXT,
  planned_progress REAL DEFAULT 0, -- percentage weight
  actual_progress REAL DEFAULT 0,
  status TEXT DEFAULT 'Planned', -- Planned, In Progress, Achieved, Delayed
  description TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schedule_delays (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  delay_date TEXT,
  delay_category TEXT, -- Land, Drawing, Material, Finance, Block, Power, Safety, Weather, etc.
  delay_hours REAL DEFAULT 0,
  delay_days REAL DEFAULT 0,
  affected_activity TEXT,
  description TEXT,
  mitigation_action TEXT,
  status TEXT DEFAULT 'Active', -- Active, Mitigated, Resolved
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Physical Progress Measurement
CREATE TABLE IF NOT EXISTS daily_progress (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  progress_date TEXT NOT NULL,
  activity TEXT NOT NULL,
  quantity REAL DEFAULT 0,
  unit TEXT,
  location TEXT,
  chainage_from TEXT,
  chainage_to TEXT,
  measurement_book_ref TEXT,
  block_executed INTEGER DEFAULT 0, -- 0=false, 1=true (Railway specific)
  mb_reference TEXT,
  photos_before TEXT, -- JSON array of photo URLs
  photos_after TEXT, -- JSON array of photo URLs
  remarks TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Billing & Payments (RA Bills)
CREATE TABLE IF NOT EXISTS ra_bills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  bill_no TEXT NOT NULL,
  bill_date TEXT,
  submitted_date TEXT,
  certified_date TEXT,
  paid_date TEXT,
  bill_amount REAL DEFAULT 0,
  certified_amount REAL DEFAULT 0,
  paid_amount REAL DEFAULT 0,
  retention_amount REAL DEFAULT 0,
  deductions_sd REAL DEFAULT 0, -- Security Deposit
  deductions_tds REAL DEFAULT 0, -- Tax Deducted at Source
  deductions_gst REAL DEFAULT 0,
  deductions_royalty REAL DEFAULT 0,
  status TEXT DEFAULT 'Draft', -- Draft, Submitted, Certified, Paid
  verification_stage TEXT, -- JE, AE, EE, Accounts
  payment_cycle_days INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Cost Control & Forecasting
CREATE TABLE IF NOT EXISTS budget_allocation (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  budget_head TEXT NOT NULL,
  allocated_amount REAL DEFAULT 0,
  revised_allocation REAL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
  UNIQUE(project_id, budget_head)
);

CREATE TABLE IF NOT EXISTS cost_forecast (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  forecast_date TEXT,
  bac REAL DEFAULT 0, -- Budget at Completion
  eac REAL DEFAULT 0, -- Estimate at Completion
  etc REAL DEFAULT 0, -- Estimate to Complete
  vac REAL DEFAULT 0, -- Variance at Completion
  forecasted_completion_date TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Materials Management
CREATE TABLE IF NOT EXISTS material_receipts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  material_type TEXT NOT NULL,
  challan_no TEXT,
  supplier_name TEXT,
  received_quantity REAL DEFAULT 0,
  unit TEXT,
  received_date TEXT,
  quality_status TEXT DEFAULT 'Pending', -- Pending, Approved, Rejected
  test_certificate_url TEXT,
  remarks TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS material_issues (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  material_type TEXT NOT NULL,
  issued_quantity REAL DEFAULT 0,
  unit TEXT,
  issued_date TEXT,
  issued_to TEXT,
  work_location TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS material_stock (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  material_type TEXT NOT NULL,
  current_stock REAL DEFAULT 0,
  unit TEXT,
  min_stock REAL DEFAULT 0,
  max_stock REAL DEFAULT 0,
  reorder_level REAL DEFAULT 0,
  last_updated TEXT DEFAULT (datetime('now')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
  UNIQUE(project_id, material_type)
);

-- Quality Control (QA/QC)
CREATE TABLE IF NOT EXISTS quality_tests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  test_type TEXT NOT NULL, -- Cube Strength, Soil Compaction, Weld Test, etc.
  test_date TEXT,
  sample_date TEXT,
  lab_name TEXT,
  sample_location TEXT,
  planned_tests INTEGER DEFAULT 0,
  conducted_tests INTEGER DEFAULT 0,
  passed_tests INTEGER DEFAULT 0,
  failed_tests INTEGER DEFAULT 0,
  pass_rate REAL DEFAULT 0,
  result TEXT, -- Pass, Fail, Pending
  test_report_url TEXT,
  status TEXT DEFAULT 'Planned',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ncrs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  ncr_no TEXT NOT NULL,
  raised_date TEXT,
  category TEXT,
  severity TEXT DEFAULT 'Minor', -- Minor, Major, Critical
  description TEXT,
  raised_by TEXT,
  assigned_to TEXT,
  corrective_action TEXT,
  preventive_action TEXT,
  closure_date TEXT,
  closure_days INTEGER,
  status TEXT DEFAULT 'Open', -- Open, Closed
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Safety & Compliance
CREATE TABLE IF NOT EXISTS safety_incidents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  incident_date TEXT,
  incident_type TEXT, -- LTI, Near Miss, First Aid, Property Damage, Unsafe Act
  severity TEXT DEFAULT 'Minor',
  description TEXT,
  location TEXT,
  reported_by TEXT,
  lost_time_days INTEGER DEFAULT 0,
  medical_treatment TEXT,
  root_cause TEXT,
  corrective_action TEXT,
  status TEXT DEFAULT 'Reported',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS toolbox_talks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  talk_date TEXT,
  topic TEXT,
  conducted_by TEXT,
  attendees_count INTEGER DEFAULT 0,
  crew_category TEXT, -- Skilled, Unskilled, Supervisors
  key_points TEXT,
  status TEXT DEFAULT 'Completed',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS work_permits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  permit_type TEXT, -- Height Work, Lifting, Electrical, Confined Space
  permit_date TEXT,
  valid_from TEXT,
  valid_to TEXT,
  work_location TEXT,
  work_description TEXT,
  hazards_identified TEXT,
  ppe_required TEXT,
  precautions TEXT,
  issued_by TEXT,
  approved_by TEXT,
  status TEXT DEFAULT 'Active', -- Active, Expired, Closed
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Railway-Specific Module (Blocks & Traffic)
CREATE TABLE IF NOT EXISTS railway_blocks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  block_date TEXT,
  section TEXT,
  block_type TEXT, -- Day Block, Night Block, Weekend Block
  requested_hours REAL DEFAULT 0,
  granted_hours REAL DEFAULT 0,
  utilized_hours REAL DEFAULT 0,
  cancellation_reason TEXT,
  work_done TEXT,
  traffic_constraints TEXT,
  status TEXT DEFAULT 'Requested', -- Requested, Granted, Utilized, Cancelled
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Manpower, Plant & Productivity
CREATE TABLE IF NOT EXISTS manpower_deployment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  record_date TEXT NOT NULL,
  total_planned INTEGER DEFAULT 0,
  total_actual INTEGER DEFAULT 0,
  skilled_workers INTEGER DEFAULT 0,
  unskilled_workers INTEGER DEFAULT 0,
  supervisors INTEGER DEFAULT 0,
  engineers INTEGER DEFAULT 0,
  absenteeism_rate REAL DEFAULT 0,
  overtime_hours REAL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
  UNIQUE(project_id, record_date)
);

CREATE TABLE IF NOT EXISTS equipment_deployment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  equipment_name TEXT NOT NULL,
  equipment_type TEXT,
  record_date TEXT,
  planned_hours REAL DEFAULT 0,
  utilized_hours REAL DEFAULT 0,
  breakdown_hours REAL DEFAULT 0,
  idle_hours REAL DEFAULT 0,
  idle_reason TEXT,
  fuel_consumed REAL DEFAULT 0,
  fuel_efficiency REAL DEFAULT 0,
  productivity_output REAL DEFAULT 0,
  output_unit TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- RFI / Drawings / Approvals Tracker
CREATE TABLE IF NOT EXISTS rfis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  rfi_no TEXT NOT NULL,
  raised_date TEXT,
  subject TEXT,
  description TEXT,
  raised_by TEXT,
  assigned_to TEXT,
  expected_response_date TEXT,
  actual_response_date TEXT,
  response_days INTEGER,
  status TEXT DEFAULT 'Open', -- Open, Responded, Closed
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS drawings_approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  drawing_no TEXT NOT NULL,
  drawing_type TEXT,
  revision_no TEXT,
  submitted_date TEXT,
  approved_date TEXT,
  approval_days INTEGER,
  submitted_by TEXT,
  approved_by TEXT,
  approval_authority TEXT, -- PWD AE/EE/SE, Rail SSE/ADEN/DEN etc.
  status TEXT DEFAULT 'Submitted', -- Draft, Submitted, Approved, Rejected
  remarks TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Procurement & Vendor Management
CREATE TABLE IF NOT EXISTS procurement_orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  po_type TEXT, -- RFQ, PO, Contract
  po_no TEXT NOT NULL,
  po_date TEXT,
  vendor_name TEXT,
  material_type TEXT,
  ordered_quantity REAL DEFAULT 0,
  unit TEXT,
  unit_rate REAL DEFAULT 0,
  total_value REAL DEFAULT 0,
  delivery_date_planned TEXT,
  delivery_date_actual TEXT,
  delay_days INTEGER DEFAULT 0,
  delay_reason TEXT,
  quality_status TEXT DEFAULT 'Pending',
  payment_status TEXT DEFAULT 'Pending',
  status TEXT DEFAULT 'Active', -- Active, Completed, Cancelled
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vendor_performance (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  vendor_name TEXT NOT NULL,
  evaluation_date TEXT,
  delivery_rating REAL DEFAULT 0, -- 1-5 scale
  quality_rating REAL DEFAULT 0, -- 1-5 scale
  price_rating REAL DEFAULT 0, -- 1-5 scale
  overall_rating REAL DEFAULT 0, -- 1-5 scale
  on_time_delivery_rate REAL DEFAULT 0,
  defect_rate REAL DEFAULT 0,
  remarks TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Land, Utilities & Site Handover
CREATE TABLE IF NOT EXISTS land_handover (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  location TEXT,
  chainage_from TEXT,
  chainage_to TEXT,
  area_available REAL DEFAULT 0,
  area_total REAL DEFAULT 0,
  availability_percentage REAL DEFAULT 0,
  handover_date TEXT,
  delay_days INTEGER DEFAULT 0,
  delay_reason TEXT,
  status TEXT DEFAULT 'Pending', -- Pending, Partially Available, Fully Available
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS utility_shifting (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  utility_type TEXT, -- Water, Power, Telecom, Drainage
  location TEXT,
  shifting_required INTEGER DEFAULT 1, -- 0=false, 1=true
  shifting_completed INTEGER DEFAULT 0, -- 0=false, 1=true
  agency_responsible TEXT,
  planned_date TEXT,
  completed_date TEXT,
  delay_days INTEGER DEFAULT 0,
  status TEXT DEFAULT 'Pending', -- Pending, In Progress, Completed
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Risk, Issues & Action Tracker
CREATE TABLE IF NOT EXISTS risk_register (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  risk_description TEXT NOT NULL,
  risk_category TEXT,
  probability TEXT DEFAULT 'Medium', -- Low, Medium, High
  impact TEXT DEFAULT 'Medium', -- Low, Medium, High
  risk_level TEXT DEFAULT 'Medium', -- Low, Medium, High, Critical
  risk_score REAL DEFAULT 0,
  exposure_amount REAL DEFAULT 0,
  exposure_days INTEGER DEFAULT 0,
  mitigation_plan TEXT,
  mitigation_status TEXT DEFAULT 'Planned', -- Planned, In Progress, Completed
  owner TEXT,
  review_date TEXT,
  rag_status TEXT DEFAULT 'Amber', -- Red, Amber, Green
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS issues_actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  issue_type TEXT, -- Technical, Commercial, Safety, Quality, Delay
  description TEXT,
  severity TEXT DEFAULT 'Medium', -- Low, Medium, High, Critical
  priority TEXT DEFAULT 'Medium',
  raised_date TEXT,
  raised_by TEXT,
  assigned_to TEXT,
  due_date TEXT,
  resolution_date TEXT,
  resolution_days INTEGER,
  action_taken TEXT,
  status TEXT DEFAULT 'Open', -- Open, In Progress, Resolved, Closed
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Claims, Variations & Disputes
CREATE TABLE IF NOT EXISTS claims_variations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  claim_no TEXT,
  claim_type TEXT, -- Extra Item, Variation, EOT, Escalation, Idle Charges
  description TEXT,
  claimed_amount REAL DEFAULT 0,
  approved_amount REAL DEFAULT 0,
  claimed_date TEXT,
  submitted_date TEXT,
  approved_date TEXT,
  approval_days INTEGER,
  supporting_docs TEXT, -- JSON array of document URLs
  status TEXT DEFAULT 'Draft', -- Draft, Submitted, Approved, Rejected, Paid
  remarks TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Document Management
CREATE TABLE IF NOT EXISTS project_documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  document_type TEXT, -- Agreement, Drawings, Test Reports, MB, RA Bills, Safety Docs
  document_name TEXT NOT NULL,
  file_url TEXT,
  version_no TEXT DEFAULT '1.0',
  revision_date TEXT,
  uploaded_by TEXT,
  approved_by TEXT,
  expiry_date TEXT,
  is_mandatory INTEGER DEFAULT 0, -- 0=false, 1=true
  status TEXT DEFAULT 'Active', -- Active, Superseded, Archived
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Stakeholder Reporting
CREATE TABLE IF NOT EXISTS stakeholder_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  report_type TEXT, -- DPR, Weekly Progress, Monthly Statement
  report_period TEXT,
  report_date TEXT,
  generated_by TEXT,
  approved_by TEXT,
  recipients TEXT, -- JSON array of recipient roles/emails
  report_url TEXT,
  status TEXT DEFAULT 'Generated',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Daily Logs (existing, keeping for compatibility)
CREATE TABLE IF NOT EXISTS daily_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  log_date TEXT NOT NULL,
  weather TEXT,
  remarks TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Daily Activities (existing)
CREATE TABLE IF NOT EXISTS daily_activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  daily_log_id INTEGER NOT NULL,
  category TEXT NOT NULL,
  activity TEXT NOT NULL,
  uom TEXT NOT NULL,
  quantity REAL NOT NULL DEFAULT 0,
  labour_count INTEGER NOT NULL DEFAULT 0,
  machinery TEXT,
  notes TEXT,
  FOREIGN KEY(daily_log_id) REFERENCES daily_logs(id) ON DELETE CASCADE
);

-- Cost Entries (existing, enhanced)
CREATE TABLE IF NOT EXISTS cost_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  entry_date TEXT NOT NULL,
  cost_head TEXT NOT NULL,
  description TEXT NOT NULL,
  vendor TEXT,
  amount REAL NOT NULL,
  quantity REAL,
  uom TEXT,
  unit_rate REAL,
  payment_mode TEXT,
  bill_no TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Budget Items (existing)
CREATE TABLE IF NOT EXISTS budget_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  cost_head TEXT NOT NULL,
  budget_amount REAL NOT NULL,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(project_id, cost_head),
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);