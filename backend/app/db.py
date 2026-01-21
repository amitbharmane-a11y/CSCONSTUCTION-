from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .settings import settings


def _ensure_db_dir() -> None:
    db_path = Path(settings.database_path)
    if db_path.parent and not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    _ensure_db_dir()
    conn = sqlite3.connect(settings.database_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    _ensure_db_dir()
    with db_cursor() as cur:
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              client TEXT NOT NULL,
              location TEXT NOT NULL,
              contract_no TEXT,
              start_date TEXT,
              end_date TEXT,
              total_contract_value REAL,
              profit_margin_target REAL DEFAULT 10.0,
              created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS daily_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              log_date TEXT NOT NULL,
              weather TEXT,
              remarks TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

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

            -- Project Packages for package-wise tracking
            CREATE TABLE IF NOT EXISTS project_packages (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              package_name TEXT NOT NULL,
              package_value REAL DEFAULT 0,
              planned_start_date TEXT,
              planned_end_date TEXT,
              actual_start_date TEXT,
              actual_end_date TEXT,
              status TEXT DEFAULT 'Not Started',
              progress_percentage REAL DEFAULT 0,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Project Milestones
            CREATE TABLE IF NOT EXISTS project_milestones (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              milestone_name TEXT NOT NULL,
              planned_date TEXT,
              actual_date TEXT,
              status TEXT DEFAULT 'Planned', -- Planned, Achieved, Delayed
              weight REAL DEFAULT 0,
              description TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- RA Bills (Running Account Bills)
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
              status TEXT DEFAULT 'Draft', -- Draft, Submitted, Certified, Paid
              certification_cycle_days INTEGER,
              payment_cycle_days INTEGER,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- BOQ Items (Bill of Quantities)
            CREATE TABLE IF NOT EXISTS boq_items (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              item_code TEXT,
              item_description TEXT NOT NULL,
              unit TEXT,
              boq_quantity REAL DEFAULT 0,
              boq_rate REAL DEFAULT 0,
              boq_amount REAL DEFAULT 0,
              executed_quantity REAL DEFAULT 0,
              executed_amount REAL DEFAULT 0,
              deviation_percentage REAL DEFAULT 0,
              status TEXT DEFAULT 'Active',
              category TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Quality Tests
            CREATE TABLE IF NOT EXISTS quality_tests (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              test_type TEXT NOT NULL, -- Cube Strength, Soil Compaction, Weld Test, etc.
              test_date TEXT,
              planned_tests INTEGER DEFAULT 0,
              conducted_tests INTEGER DEFAULT 0,
              passed_tests INTEGER DEFAULT 0,
              failed_tests INTEGER DEFAULT 0,
              pass_rate REAL DEFAULT 0,
              status TEXT DEFAULT 'Planned',
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- NCRs (Non-Conformance Reports)
            CREATE TABLE IF NOT EXISTS ncrs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              ncr_no TEXT NOT NULL,
              raised_date TEXT,
              category TEXT,
              description TEXT,
              severity TEXT DEFAULT 'Minor',
              status TEXT DEFAULT 'Open', -- Open, Closed
              closure_date TEXT,
              closure_days INTEGER,
              corrective_action TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Safety Incidents
            CREATE TABLE IF NOT EXISTS safety_incidents (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              incident_date TEXT,
              incident_type TEXT, -- LTI, Near Miss, First Aid, Property Damage
              description TEXT,
              severity TEXT DEFAULT 'Minor',
              lost_time_days INTEGER DEFAULT 0,
              reported_by TEXT,
              status TEXT DEFAULT 'Reported',
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Labour Manpower
            CREATE TABLE IF NOT EXISTS labour_manpower (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              record_date TEXT NOT NULL,
              total_planned INTEGER DEFAULT 0,
              total_actual INTEGER DEFAULT 0,
              mason_count INTEGER DEFAULT 0,
              carpenter_count INTEGER DEFAULT 0,
              bar_bender_count INTEGER DEFAULT 0,
              welder_count INTEGER DEFAULT 0,
              helper_count INTEGER DEFAULT 0,
              absenteeism_rate REAL DEFAULT 0,
              overtime_hours REAL DEFAULT 0,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
              UNIQUE(project_id, record_date)
            );

            -- Plant & Machinery
            CREATE TABLE IF NOT EXISTS plant_machinery (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              equipment_name TEXT NOT NULL,
              equipment_type TEXT,
              record_date TEXT,
              available_hours REAL DEFAULT 0,
              utilized_hours REAL DEFAULT 0,
              breakdown_hours REAL DEFAULT 0,
              idle_hours REAL DEFAULT 0,
              fuel_consumed REAL DEFAULT 0,
              fuel_norm REAL DEFAULT 0,
              availability_percentage REAL DEFAULT 0,
              utilization_percentage REAL DEFAULT 0,
              mttr_hours REAL DEFAULT 0,
              mtbf_hours REAL DEFAULT 0,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Material Inventory
            CREATE TABLE IF NOT EXISTS material_inventory (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              material_type TEXT NOT NULL, -- Cement, Steel, Bitumen, Ballast, etc.
              record_date TEXT,
              issued_quantity REAL DEFAULT 0,
              consumed_quantity REAL DEFAULT 0,
              theoretical_quantity REAL DEFAULT 0,
              variance_percentage REAL DEFAULT 0,
              stock_level REAL DEFAULT 0,
              min_stock REAL DEFAULT 0,
              max_stock REAL DEFAULT 0,
              status TEXT DEFAULT 'Normal', -- Normal, Low Stock, Over Stock
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Material Procurement
            CREATE TABLE IF NOT EXISTS material_procurement (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              material_type TEXT NOT NULL,
              po_no TEXT,
              po_date TEXT,
              vendor_name TEXT,
              ordered_quantity REAL DEFAULT 0,
              delivered_quantity REAL DEFAULT 0,
              lead_time_days INTEGER DEFAULT 0,
              delivery_date TEXT,
              on_time_delivery INTEGER DEFAULT 0, -- 0=false, 1=true
              quality_status TEXT DEFAULT 'Pending',
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Drawings & Approvals
            CREATE TABLE IF NOT EXISTS drawings_approvals (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              drawing_no TEXT NOT NULL,
              drawing_type TEXT,
              submitted_date TEXT,
              approved_date TEXT,
              approval_days INTEGER,
              status TEXT DEFAULT 'Submitted', -- Draft, Submitted, Approved, Rejected
              approver_name TEXT,
              remarks TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- RFIs (Requests for Information)
            CREATE TABLE IF NOT EXISTS rfis (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              rfi_no TEXT NOT NULL,
              raised_date TEXT,
              subject TEXT,
              description TEXT,
              closure_date TEXT,
              closure_days INTEGER,
              status TEXT DEFAULT 'Open', -- Open, Closed
              response_by TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Railway Blocks
            CREATE TABLE IF NOT EXISTS railway_blocks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              block_date TEXT,
              block_type TEXT, -- Day Block, Night Block, Weekend Block
              requested_hours REAL DEFAULT 0,
              granted_hours REAL DEFAULT 0,
              utilized_hours REAL DEFAULT 0,
              status TEXT DEFAULT 'Requested', -- Requested, Granted, Utilized
              work_description TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Contract Compliance
            CREATE TABLE IF NOT EXISTS contract_compliance (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              compliance_type TEXT NOT NULL, -- EOT, LD, Security Deposit, Insurance, PF, ESIC
              description TEXT,
              due_date TEXT,
              status TEXT DEFAULT 'Active', -- Active, Expired, Renewed
              expiry_date TEXT,
              days_to_expiry INTEGER,
              amount REAL DEFAULT 0,
              remarks TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              updated_at TEXT DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Risk Register
            CREATE TABLE IF NOT EXISTS risk_register (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              risk_description TEXT NOT NULL,
              risk_category TEXT,
              probability TEXT DEFAULT 'Medium', -- Low, Medium, High
              impact TEXT DEFAULT 'Medium', -- Low, Medium, High
              risk_level TEXT DEFAULT 'Medium', -- Low, Medium, High, Critical
              exposure_amount REAL DEFAULT 0,
              exposure_days INTEGER DEFAULT 0,
              mitigation_plan TEXT,
              mitigation_status TEXT DEFAULT 'Planned', -- Planned, In Progress, Completed
              rag_status TEXT DEFAULT 'Amber', -- Red, Amber, Green
              owner TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              updated_at TEXT DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Stakeholder Issues
            CREATE TABLE IF NOT EXISTS stakeholder_issues (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              issue_type TEXT, -- Public Complaint, Client Inspection, Audit Observation
              description TEXT,
              raised_date TEXT,
              resolved_date TEXT,
              resolution_days INTEGER,
              status TEXT DEFAULT 'Open', -- Open, Resolved, Closed
              priority TEXT DEFAULT 'Medium', -- Low, Medium, High, Critical
              raised_by TEXT,
              assigned_to TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Delay Reasons Tracking
            CREATE TABLE IF NOT EXISTS delay_reasons (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              delay_date TEXT,
              delay_category TEXT, -- Land, Traffic, Drawings, Materials, Labour, Power, Weather
              delay_hours REAL DEFAULT 0,
              delay_days REAL DEFAULT 0,
              description TEXT,
              impact_on_schedule TEXT,
              mitigation_action TEXT,
              status TEXT DEFAULT 'Active', -- Active, Mitigated, Resolved
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Claims and Variations
            CREATE TABLE IF NOT EXISTS claims_variations (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              claim_type TEXT, -- Extra Item, Variation, Claim
              description TEXT,
              claimed_amount REAL DEFAULT 0,
              approved_amount REAL DEFAULT 0,
              status TEXT DEFAULT 'Submitted', -- Draft, Submitted, Approved, Rejected, Paid
              submitted_date TEXT,
              approved_date TEXT,
              remarks TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Third Party Inspections
            CREATE TABLE IF NOT EXISTS third_party_inspections (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              inspection_type TEXT, -- Concrete, Steel, Welding, Foundation
              scheduled_date TEXT,
              conducted_date TEXT,
              status TEXT DEFAULT 'Scheduled', -- Scheduled, Conducted, Passed, Failed, Pending
              inspector_name TEXT,
              remarks TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Calibration Records
            CREATE TABLE IF NOT EXISTS calibration_records (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              equipment_name TEXT NOT NULL,
              equipment_type TEXT, -- Lab Equipment, Survey Equipment, Concrete Testing
              last_calibration_date TEXT,
              next_due_date TEXT,
              status TEXT DEFAULT 'Valid', -- Valid, Due Soon, Overdue
              days_to_expiry INTEGER,
              calibration_agency TEXT,
              certificate_no TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              updated_at TEXT DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Toolbox Talks
            CREATE TABLE IF NOT EXISTS toolbox_talks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              talk_date TEXT,
              topic TEXT,
              conducted_by TEXT,
              attendees_count INTEGER DEFAULT 0,
              planned_talks INTEGER DEFAULT 0,
              conducted_talks INTEGER DEFAULT 0,
              status TEXT DEFAULT 'Completed',
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Work Permits
            CREATE TABLE IF NOT EXISTS work_permits (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              permit_type TEXT, -- Height Work, Lifting, Electrical, Confined Space
              permit_date TEXT,
              valid_from TEXT,
              valid_to TEXT,
              work_location TEXT,
              hazards_identified TEXT,
              ppe_required TEXT,
              status TEXT DEFAULT 'Active', -- Active, Expired, Closed
              issued_by TEXT,
              approved_by TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Subcontractor Performance
            CREATE TABLE IF NOT EXISTS subcontractor_performance (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              subcontractor_name TEXT NOT NULL,
              evaluation_date TEXT,
              progress_rating REAL DEFAULT 0, -- 1-5 scale
              quality_rating REAL DEFAULT 0, -- 1-5 scale
              safety_rating REAL DEFAULT 0, -- 1-5 scale
              overall_rating REAL DEFAULT 0, -- 1-5 scale
              remarks TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Vendor Performance
            CREATE TABLE IF NOT EXISTS vendor_performance (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL,
              vendor_name TEXT NOT NULL,
              material_type TEXT,
              evaluation_date TEXT,
              delivery_rating REAL DEFAULT 0, -- 1-5 scale
              quality_rating REAL DEFAULT 0, -- 1-5 scale
              price_rating REAL DEFAULT 0, -- 1-5 scale
              overall_score REAL DEFAULT 0, -- 1-5 scale
              on_time_delivery_rate REAL DEFAULT 0,
              remarks TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """
        )
        _migrate_schema(cur)


def _column_names(cur: sqlite3.Cursor, table: str) -> set[str]:
    cur.execute(f"PRAGMA table_info({table});")
    rows = cur.fetchall()
    return {str(r[1]) for r in rows}  # row[1] = column name


def _ensure_columns(cur: sqlite3.Cursor, table: str, columns: dict[str, str]) -> None:
    existing = _column_names(cur, table)
    for col, col_def in columns.items():
        if col in existing:
            continue
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def};")


def _migrate_schema(cur: sqlite3.Cursor) -> None:
    # Backward-compatible migrations for older DB files.
    _ensure_columns(
        cur,
        "cost_entries",
        {
            "quantity": "REAL",
            "uom": "TEXT",
            "unit_rate": "REAL",
        },
    )
    _ensure_columns(
        cur,
        "projects",
        {
            "total_contract_value": "REAL",
            "profit_margin_target": "REAL DEFAULT 10.0",
            "contract_completion_date": "TEXT",
            "project_manager": "TEXT",
            "site_engineer": "TEXT",
            "status": "TEXT DEFAULT 'Planning'",
            "updated_at": "TEXT",
        },
    )


def seed_if_empty() -> None:
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM projects;")
        count = int(cur.fetchone()["c"])
        if count > 0:
            return

        cur.execute(
            """
            INSERT INTO projects (name, client, location, contract_no, start_date, end_date, total_contract_value, profit_margin_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Railway ROB + Bridge Works (Pile Foundation & Sub-Structure)",
                "Indian Railways / PWD",
                "Maharashtra",
                "PWD-IR-ROB-001",
                "2026-01-01",
                "2026-12-31",
                10_00_00_000,  # 10 crores total contract value
                12.0,  # 12% profit margin target
            ),
        )
        project_id = int(cur.lastrowid)

        # Budget heads (example)
        budgets = [
            ("Materials - Steel", 1_20_00_000),
            ("Materials - Cement/RMC", 95_00_000),
            ("Labour", 65_00_000),
            ("Machinery", 40_00_000),
            ("Subcontract", 75_00_000),
            ("Fuel", 18_00_000),
            ("Testing & QA", 6_00_000),
            ("Overheads", 22_00_000),
        ]
        for head, amt in budgets:
            cur.execute(
                """
                INSERT INTO budget_items (project_id, cost_head, budget_amount, notes)
                VALUES (?, ?, ?, ?)
                """,
                (project_id, head, float(amt), "Seed budget head"),
            )

        # One daily log with some activities
        cur.execute(
            """
            INSERT INTO daily_logs (project_id, log_date, weather, remarks)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, "2026-01-21", "Clear", "Mobilization + initial pile boring started."),
        )
        log_id = int(cur.lastrowid)
        activities = [
            ("Pile Foundation", "Boring for pile P-01", "Nos", 1, 18, "Hydraulic Rig", "Depth 18m"),
            ("Pile Foundation", "Rebar cage fabrication", "Kg", 650, 10, "Bar bending yard", "Cage for P-01"),
            ("General", "Site survey & setting out", "Job", 1, 6, "", ""),
        ]
        for category, activity, uom, qty, labour, mach, notes in activities:
            cur.execute(
                """
                INSERT INTO daily_activities
                (daily_log_id, category, activity, uom, quantity, labour_count, machinery, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (log_id, category, activity, uom, float(qty), int(labour), mach, notes),
            )

        # Some costs with detailed quantities and rates
        costs = [
            ("2026-01-21", "Materials - Steel", "Reinforcement steel for pile cages", "Steel Corp Ltd", 325000, 6.5, "MT", 50000, "Bank", "BILL-STL-001"),
            ("2026-01-21", "Materials - Cement/RMC", "Ready mix concrete M30", "RMC Suppliers", 187500, 75, "CuM", 2500, "Bank", "BILL-RMC-001"),
            ("2026-01-21", "Labour", "Pile foundation labour", "Local Contractor", 89250, 3250, "Hours", 27.46, "Cash", "PAY-001"),
            ("2026-01-21", "Machinery", "Hydraulic piling rig rental", "Equip Rentals", 250000, 1, "Job", 250000, "Bank", "BILL-EQP-001"),
            ("2026-01-21", "Fuel", "Diesel for DG + equipment", "Fuel Station", 18000, 200, "Litre", 90, "Cash", "CASH-001"),
            ("2026-01-22", "Testing & QA", "Pile integrity testing", "Test Lab", 15600, 13, "Nos", 1200, "Bank", "BILL-TST-001"),
            ("2026-01-22", "Overheads", "Site supervision & management", "Internal", 22500, 75, "Hours", 300, "Bank", "INT-001"),
        ]
        for dt, head, desc, vendor, amt, qty, uom, rate, mode, bill in costs:
            cur.execute(
                """
                INSERT INTO cost_entries
                (project_id, entry_date, cost_head, description, vendor, amount, quantity, uom, unit_rate, payment_mode, bill_no)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, dt, head, desc, vendor, float(amt), float(qty), uom, float(rate), mode, bill),
            )

        # Sample project milestones
        milestones = [
            ("Foundation Work Completion", "2026-03-15", "Achieved", 25.0, "Pile foundation and sub-structure completed"),
            ("Superstructure Erection", "2026-06-30", "Planned", 35.0, "Bridge deck and superstructure"),
            ("Finishing Works", "2026-10-15", "Planned", 25.0, "Painting, electrical, and finishing"),
            ("Final Handover", "2026-11-30", "Planned", 15.0, "Project completion and handover"),
        ]
        for name, planned_date, status, weight, desc in milestones:
            cur.execute(
                """
                INSERT INTO project_milestones (project_id, milestone_name, planned_date, status, weight, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, name, planned_date, status, weight, desc),
            )

        # Sample RA Bills
        ra_bills_data = [
            ("RA-001", "2026-01-15", "2026-01-20", "2026-02-05", 850000, 820000, 800000, 15000, "Paid", 15, 20),
            ("RA-002", "2026-02-15", "2026-02-20", "2026-03-10", 1250000, 1200000, 1150000, 25000, "Certified", 12, None),
            ("RA-003", "2026-03-15", None, None, 1450000, 0, 0, 0, "Submitted", None, None),
        ]
        for bill_no, bill_date, submitted, certified, bill_amt, certified_amt, paid_amt, retention, status, cert_cycle, pay_cycle in ra_bills_data:
            cur.execute(
                """
                INSERT INTO ra_bills
                (project_id, bill_no, bill_date, submitted_date, certified_date, paid_date,
                 bill_amount, certified_amount, paid_amount, retention_amount, status,
                 certification_cycle_days, payment_cycle_days)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, bill_no, bill_date, submitted, certified, None, bill_amt, certified_amt, paid_amt, retention, status, cert_cycle, pay_cycle),
            )

        # Sample Quality Tests
        quality_tests_data = [
            ("Cube Strength Test", "2026-01-25", 50, 48, 46, 2, 95.8, "Completed"),
            ("Soil Compaction Test", "2026-01-28", 25, 25, 23, 2, 92.0, "Completed"),
            ("Weld Testing", "2026-02-01", 30, 28, 27, 1, 96.4, "Completed"),
            ("Concrete Pour Inspection", "2026-02-05", 15, 12, 12, 0, 100.0, "Completed"),
            ("Reinforcement Testing", "2026-02-08", 20, 18, 17, 1, 94.4, "Completed"),
        ]
        for test_type, test_date, planned, conducted, passed, failed, pass_rate, status in quality_tests_data:
            cur.execute(
                """
                INSERT INTO quality_tests
                (project_id, test_type, test_date, planned_tests, conducted_tests,
                 passed_tests, failed_tests, pass_rate, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, test_type, test_date, planned, conducted, passed, failed, pass_rate, status),
            )

        # Sample NCRs
        ncrs_data = [
            ("NCR-001", "2026-01-20", "Quality", "Concrete strength below specification", "Major", "Closed", "2026-01-25", 5, "Additional curing implemented"),
            ("NCR-002", "2026-01-28", "Safety", "Inadequate PPE usage observed", "Minor", "Closed", "2026-01-30", 2, "Safety training conducted"),
            ("NCR-003", "2026-02-05", "Documentation", "Missing inspection reports", "Minor", "Open", None, None, "Documentation being updated"),
            ("NCR-004", "2026-02-10", "Material", "Steel reinforcement diameter variance", "Major", "Open", None, None, "Supplier notified for replacement"),
        ]
        for ncr_no, raised_date, category, desc, severity, status, closure_date, closure_days, action in ncrs_data:
            cur.execute(
                """
                INSERT INTO ncrs
                (project_id, ncr_no, raised_date, category, description, severity, status,
                 closure_date, closure_days, corrective_action)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, ncr_no, raised_date, category, desc, severity, status, closure_date, closure_days, action),
            )

        # Sample Safety Incidents
        safety_incidents_data = [
            ("2026-01-15", "First Aid", "Minor cut during rebar work", "Minor", 0, "Worker A", "Reported"),
            ("2026-01-22", "Near Miss", "Equipment nearly tipped during lifting", "Minor", 0, "Supervisor B", "Reported"),
            ("2026-01-28", "LTI", "Ankle sprain during concrete pouring", "Major", 2, "Worker C", "Reported"),
            ("2026-02-05", "Property Damage", "Minor equipment damage", "Minor", 0, "Operator D", "Reported"),
        ]
        for incident_date, incident_type, desc, severity, lost_days, reported_by, status in safety_incidents_data:
            cur.execute(
                """
                INSERT INTO safety_incidents
                (project_id, incident_date, incident_type, description, severity,
                 lost_time_days, reported_by, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, incident_date, incident_type, desc, severity, lost_days, reported_by, status),
            )

        # Sample Labour Manpower data
        labour_data = [
            ("2026-01-31", 85, 82, 12, 8, 15, 6, 41, 3.5, 45),
            ("2026-02-15", 85, 78, 12, 8, 14, 6, 38, 7.1, 52),
            ("2026-02-28", 90, 86, 13, 9, 16, 7, 41, 4.4, 38),
        ]
        for record_date, planned, actual, mason, carpenter, bar_bender, welder, helper, absenteeism, overtime in labour_data:
            cur.execute(
                """
                INSERT INTO labour_manpower
                (project_id, record_date, total_planned, total_actual, mason_count, carpenter_count,
                 bar_bender_count, welder_count, helper_count, absenteeism_rate, overtime_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, record_date, planned, actual, mason, carpenter, bar_bender, welder, helper, absenteeism, overtime),
            )

        # Sample Plant & Machinery data
        machinery_data = [
            ("Hydraulic Piling Rig", "Piling Equipment", "2026-01-31", 200, 180, 5, 15, 800, 780, 97.5, 90.0, 2.5, 150),
            ("Concrete Pump", "Concrete Equipment", "2026-01-31", 160, 145, 3, 12, 450, 420, 98.1, 90.6, 1.8, 180),
            ("Tower Crane", "Lifting Equipment", "2026-01-31", 200, 170, 8, 22, 600, 580, 96.0, 85.0, 3.2, 120),
        ]
        for equip_name, equip_type, record_date, avail_hrs, util_hrs, breakdown_hrs, idle_hrs, fuel_consumed, fuel_norm, avail_pct, util_pct, mttr, mtbf in machinery_data:
            cur.execute(
                """
                INSERT INTO plant_machinery
                (project_id, equipment_name, equipment_type, record_date, available_hours, utilized_hours,
                 breakdown_hours, idle_hours, fuel_consumed, fuel_norm, availability_percentage,
                 utilization_percentage, mttr_hours, mtbf_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, equip_name, equip_type, record_date, avail_hrs, util_hrs, breakdown_hrs, idle_hrs, fuel_consumed, fuel_norm, avail_pct, util_pct, mttr, mtbf),
            )

        # Sample Material Inventory
        material_inventory_data = [
            ("Cement", "2026-01-31", 500, 480, 485, -1.0, 20, 50, 100, "Normal"),
            ("Steel", "2026-01-31", 50, 48, 46, 4.3, 2, 5, 10, "Low Stock"),
            ("RMC", "2026-01-31", 200, 195, 198, -1.5, 5, 10, 20, "Normal"),
        ]
        for material_type, record_date, issued, consumed, theoretical, variance_pct, stock_level, min_stock, max_stock, status in material_inventory_data:
            cur.execute(
                """
                INSERT INTO material_inventory
                (project_id, material_type, record_date, issued_quantity, consumed_quantity,
                 theoretical_quantity, variance_percentage, stock_level, min_stock, max_stock, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, material_type, record_date, issued, consumed, theoretical, variance_pct, stock_level, min_stock, max_stock, status),
            )

        # Sample Risk Register
        risks_data = [
            ("Land acquisition delays", "Land & Rights", "Medium", "High", "High", 500000, 60, "Regular follow-up with authorities", "In Progress", "Amber", "Project Manager"),
            ("Material price escalation", "Procurement", "High", "Medium", "Medium", 200000, 0, "Fixed price contracts negotiated", "Completed", "Green", "Procurement Head"),
            ("Monsoon impact on construction", "Weather", "Medium", "High", "Medium", 300000, 90, "Weather contingency planning", "Planned", "Amber", "Site Engineer"),
            ("Key skilled labour shortage", "Human Resources", "High", "Medium", "High", 400000, 30, "Additional recruitment drive", "In Progress", "Red", "HR Manager"),
        ]
        for risk_desc, category, probability, impact, risk_level, exposure_amt, exposure_days, mitigation, status, rag_status, owner in risks_data:
            cur.execute(
                """
                INSERT INTO risk_register
                (project_id, risk_description, risk_category, probability, impact, risk_level,
                 exposure_amount, exposure_days, mitigation_plan, mitigation_status, rag_status, owner)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, risk_desc, category, probability, impact, risk_level, exposure_amt, exposure_days, mitigation, status, rag_status, owner),
            )