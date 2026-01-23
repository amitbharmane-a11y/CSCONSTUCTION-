from __future__ import annotations

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from beanie import init_beanie
import asyncio

from .settings import settings

# Global MongoDB client and database
client = None
database = None
DB_AVAILABLE = False

async def init_mongodb():
    """Initialize MongoDB connection"""
    global client, database, DB_AVAILABLE
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]

        # Test the connection
        await client.admin.command('ping')
        DB_AVAILABLE = True
        print(f"Connected to MongoDB: {settings.database_name}")

        # Initialize Beanie with document models
        from .models import (
            Project, DailyLog, DailyActivity, CostEntry, BudgetItem,
            ProjectPackage, ProjectMilestone, RABill, QualityTest, NCR,
            SafetyIncident, LabourManpower, PlantMachinery, MaterialInventory,
            DrawingsApproval, RailwayBlock, RiskRegister, BOQItem,
            CalibrationRecord, ClaimsVariation, ContractCompliance,
            DelayReason, MaterialProcurement, RFI, StakeholderIssue,
            SubcontractorPerformance, ThirdPartyInspection, ToolboxTalk,
            VendorPerformance, WorkPermit
        )

        await init_beanie(
            database=database,
            document_models=[
                Project, DailyLog, DailyActivity, CostEntry, BudgetItem,
                ProjectPackage, ProjectMilestone, RABill, QualityTest, NCR,
                SafetyIncident, LabourManpower, PlantMachinery, MaterialInventory,
                DrawingsApproval, RailwayBlock, RiskRegister, BOQItem,
                CalibrationRecord, ClaimsVariation, ContractCompliance,
                DelayReason, MaterialProcurement, RFI, StakeholderIssue,
                SubcontractorPerformance, ThirdPartyInspection, ToolboxTalk,
                VendorPerformance, WorkPermit
            ]
        )

    except Exception as e:
        print(f"MongoDB connection failed: {str(e)}")
        DB_AVAILABLE = False
        print("Running with mock data fallback")


async def seed_if_empty():
    """Seed database with sample data if empty"""
    if not DB_AVAILABLE:
        print("⚠️ MongoDB not available, skipping seeding")
        return

    try:
        # Check if projects collection is empty
        count = await database.projects.count_documents({})
        if count > 0:
            return

        # Insert sample project
        from .models import Project
        project = Project(
            name="Railway ROB + Bridge Works (Pile Foundation & Sub-Structure)",
            client="Indian Railways / PWD",
            location="Maharashtra",
            contract_no="PWD-IR-ROB-001",
            start_date="2026-01-01",
            end_date="2026-12-31",
            total_contract_value=10_00_00_000,  # 10 crores total contract value
            profit_margin_target=12.0,  # 12% profit margin target
            contract_completion_date="2026-12-31",
            project_manager="Shri. A. K. Sharma",
            site_engineer="Er. R. K. Gupta",
            status="active"
        )

        await project.insert()
        print(f"✅ Database seeded with sample project ID: {project.id}")

        # Seed additional sample data for all collections
        await _seed_sample_data(project.id)

    except Exception as e:
        print(f"❌ Error seeding database: {e}")


async def _seed_sample_data(project_id):
    """Seed all collections with sample construction data"""
    try:
        # Seed project packages
        from .models import ProjectPackage
        packages = [
            ProjectPackage(project_id=project_id, package_name="Pile Foundation Works", planned_value=2_00_00_000, actual_value=1_80_00_000, progress_percentage=90.0),
            ProjectPackage(package_name="Bridge Sub-Structure", planned_value=3_00_00_000, actual_value=2_80_00_000, progress_percentage=93.3),
            ProjectPackage(package_name="Bridge Super-Structure", planned_value=2_50_00_000, actual_value=2_20_00_000, progress_percentage=88.0),
            ProjectPackage(package_name="Railway Track & Signaling", planned_value=2_50_00_000, actual_value=2_26_00_000, progress_percentage=90.4),
        ]
        for pkg in packages:
            pkg.project_id = project_id
            await pkg.insert()

        # Seed milestones
        from .models import ProjectMilestone
        milestones = [
            ProjectMilestone(project_id=project_id, milestone_name="Mobilization Complete", planned_date="2026-01-15", actual_date="2026-01-12", status="completed"),
            ProjectMilestone(project_id=project_id, milestone_name="Pile Foundation 50% Complete", planned_date="2026-03-15", actual_date="2026-03-20", status="completed"),
            ProjectMilestone(project_id=project_id, milestone_name="Bridge Deck Casting", planned_date="2026-08-15", actual_date="2026-08-30", status="in_progress"),
            ProjectMilestone(project_id=project_id, milestone_name="Final Handover", planned_date="2026-12-15", actual_date=None, status="pending"),
        ]
        for milestone in milestones:
            await milestone.insert()

        # Seed RA Bills
        from .models import RABill
        ra_bills = [
            RABill(project_id=project_id, bill_no="RA-001", bill_date="2026-02-28", bill_amount=45_00_000, certified_amount=42_00_000, paid_amount=42_00_000, payment_date="2026-03-15", status="paid"),
            RABill(project_id=project_id, bill_no="RA-002", bill_date="2026-04-30", bill_amount=52_00_000, certified_amount=48_00_000, paid_amount=48_00_000, payment_date="2026-05-15", status="paid"),
            RABill(project_id=project_id, bill_no="RA-003", bill_date="2026-06-30", bill_amount=58_00_000, certified_amount=55_00_000, paid_amount=55_00_000, payment_date="2026-07-15", status="paid"),
            RABill(project_id=project_id, bill_no="RA-004", bill_date="2026-08-30", bill_amount=62_00_000, certified_amount=58_00_000, paid_amount=58_00_000, payment_date="2026-09-15", status="paid"),
            RABill(project_id=project_id, bill_no="RA-005", bill_date="2026-10-30", bill_amount=68_00_000, certified_amount=65_00_000, paid_amount=None, payment_date=None, status="certified"),
        ]
        for bill in ra_bills:
            await bill.insert()

        # Seed Quality Tests
        from .models import QualityTest
        quality_tests = [
            QualityTest(project_id=project_id, test_type="Concrete Cube Test", planned_tests=120, conducted_tests=118, passed_tests=115, pass_rate=97.5, status="ongoing"),
            QualityTest(project_id=project_id, test_type="Rebar Testing", planned_tests=80, conducted_tests=76, passed_tests=74, pass_rate=97.4, status="ongoing"),
            QualityTest(project_id=project_id, test_type="Soil Compaction", planned_tests=60, conducted_tests=58, passed_tests=56, pass_rate=96.6, status="ongoing"),
            QualityTest(project_id=project_id, test_type="Weld Testing", planned_tests=40, conducted_tests=38, passed_tests=37, pass_rate=97.4, status="ongoing"),
        ]
        for test in quality_tests:
            await test.insert()

        # Seed NCRs
        from .models import NCR
        ncrs = [
            NCR(project_id=project_id, ncr_no="NCR-001", description="Concrete mix design variation", raised_date="2026-03-15", category="Quality", severity="Medium", status="Closed", closure_date="2026-03-20"),
            NCR(project_id=project_id, ncr_no="NCR-002", description="Formwork alignment issue", raised_date="2026-04-10", category="Quality", severity="Low", status="Closed", closure_date="2026-04-12"),
            NCR(project_id=project_id, ncr_no="NCR-003", description="Reinforcement cover deficiency", raised_date="2026-05-05", category="Quality", severity="High", status="Open", closure_date=None),
            NCR(project_id=project_id, ncr_no="NCR-004", description="Curing procedure non-compliance", raised_date="2026-06-20", category="Quality", severity="Medium", status="Open", closure_date=None),
        ]
        for ncr in ncrs:
            await ncr.insert()

        # Seed Safety Incidents
        from .models import SafetyIncident
        incidents = [
            SafetyIncident(project_id=project_id, incident_no="INC-001", incident_date="2026-02-15", incident_type="Near Miss", description="Worker slip on wet surface", severity="Low", status="Closed", action_taken="Safety briefing conducted"),
            SafetyIncident(project_id=project_id, incident_no="INC-002", incident_date="2026-03-22", incident_type="First Aid", description="Minor cut during rebar work", severity="Low", status="Closed", action_taken="First aid provided, safety gloves reinforced"),
            SafetyIncident(project_id=project_id, incident_no="INC-003", incident_date="2026-05-10", incident_type="Medical Treatment", description="Eye irritation from concrete dust", severity="Medium", status="Closed", action_taken="PPE training reinforced"),
            SafetyIncident(project_id=project_id, incident_no="INC-004", incident_date="2026-07-05", incident_type="Lost Time Injury", description="Ankle sprain during material handling", severity="High", status="Closed", action_taken="Medical treatment provided, lifting equipment training"),
        ]
        for incident in incidents:
            await incident.insert()

        # Seed Labour Manpower
        from .models import LabourManpower
        labour_data = [
            LabourManpower(project_id=project_id, recorded_date="2026-10-01", planned_manpower=150, actual_manpower=145, mason_count=25, carpenter_count=15, bar_bender_count=20, welder_count=8, absenteeism_rate=3.3, overtime_hours=120),
        ]
        for labour in labour_data:
            await labour.insert()

        # Seed Plant Machinery
        from .models import PlantMachinery
        machinery = [
            PlantMachinery(project_id=project_id, equipment_name="Batching Plant", equipment_type="Concrete Plant", availability_percentage=95.0, utilization_percentage=88.0, breakdown_hours=12, idle_time_causes="Waiting for material"),
            PlantMachinery(project_id=project_id, equipment_name="Pile Driving Rig", equipment_type="Foundation Equipment", availability_percentage=92.0, utilization_percentage=85.0, breakdown_hours=24, idle_time_causes="Weather conditions"),
            PlantMachinery(project_id=project_id, equipment_name="Concrete Pump", equipment_type="Placing Equipment", availability_percentage=98.0, utilization_percentage=90.0, breakdown_hours=8, idle_time_causes="No front"),
        ]
        for machine in machinery:
            await machine.insert()

        # Seed Material Inventory
        from .models import MaterialInventory
        materials = [
            MaterialInventory(project_id=project_id, material_name="Cement", current_stock=150, min_stock=100, max_stock=300, unit="MT", stock_value=4_50_000, lead_time_days=3),
            MaterialInventory(project_id=project_id, material_name="Steel Reinforcement", current_stock=45, min_stock=30, max_stock=100, unit="MT", stock_value=13_50_000, lead_time_days=7),
            MaterialInventory(project_id=project_id, material_name="Coarse Aggregate", current_stock=200, min_stock=150, max_stock=400, unit="Cum", stock_value=2_00_000, lead_time_days=2),
        ]
        for material in materials:
            await material.insert()

        print("✅ All sample data seeded successfully")

    except Exception as e:
        print(f"❌ Error seeding sample data: {e}")


def init_db():
    """Initialize database (compatibility function)"""
    # This is now async, so we'll handle it in the main startup
    pass


def init_db() -> None:
    """Initialize database schema"""
    global IS_POSTGRESQL

    if IS_POSTGRESQL:
        # For PostgreSQL, we'll need different schema
        print("PostgreSQL database - schema initialization may be needed")
        return

    # SQLite schema initialization
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
            """
        )


def seed_if_empty() -> None:
    """Seed database with sample data if empty"""
    with db_cursor() as cur:
        if IS_POSTGRESQL:
            cur.execute("SELECT COUNT(*) AS c FROM projects;")
            count = int(cur.fetchone()[0])
        else:
            cur.execute("SELECT COUNT(*) AS c FROM projects;")
            count = int(cur.fetchone()["c"])

        if count > 0:
            return

        # Insert sample project
        if IS_POSTGRESQL:
            cur.execute(
                """
                INSERT INTO projects (name, client, location, contract_no, start_date, end_date, total_contract_value, profit_margin_target)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
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
            project_id = cur.fetchone()[0]
        else:
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
            project_id = cur.lastrowid

        print(f"Database seeded with sample project ID: {project_id}")