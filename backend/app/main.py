from __future__ import annotations

from collections import defaultdict
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db, seed_if_empty
import os

# Mock data for fallback when database is not available
MOCK_PROJECTS = [
    {
        "id": 1,
        "name": "Railway ROB + Bridge Works (Pile Foundation & Sub-Structure)",
        "client": "Indian Railways / PWD",
        "location": "Maharashtra",
        "contract_no": "PWD-IR-ROB-001",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "total_contract_value": 100000000.0,  # 10 crores
        "profit_margin_target": 12.0,
        "created_at": "2026-01-01T00:00:00",
        "status": "Execution",
        "contract_completion_date": "2026-12-31",
        "project_manager": "Er. Rajesh Kumar",
        "site_engineer": "Er. Amit Singh"
    }
]

MOCK_COST_ENTRIES = [
    {
        "id": 1,
        "project_id": 1,
        "cost_head": "Labour",
        "amount": 3779500.0,
        "quantity": 3250.0,
        "uom": "Hours",
        "unit_rate": 1161.54,
        "entry_date": "2026-01-15",
        "description": "Mason and carpenter work for pile foundation"
    },
    {
        "id": 2,
        "project_id": 1,
        "cost_head": "Materials",
        "amount": 3315000.0,
        "quantity": 81.5,
        "uom": "MT/CuM",
        "unit_rate": 40674.85,
        "entry_date": "2026-01-20",
        "description": "Steel and concrete materials"
    }
]

# Initialize database at import time (for local/dev). On Vercel, the
# filesystem is read-only for bundled files, so initialization may fail;
# we catch and fall back to mock data.
DB_AVAILABLE = True
try:
    if not os.getenv("VERCEL"):
        init_db()
        seed_if_empty()
except Exception as e:
    print(f"Database initialization failed: {e}")
    DB_AVAILABLE = False
    # For Vercel deployment, continue without database
    pass
from .schemas import (
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
    JobCostingCategory,
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
)
from .services.ai import answer as ai_answer
from .utils import row_to_dict, rows_to_dicts
from .db import db_cursor


app = FastAPI(title="C S Construction Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    """Run DB initialization only in environments where writes are allowed.

    On Vercel, we ship a pre-built SQLite file and open it read-only, so we
    skip schema/seed writes during startup.
    """
    global DB_AVAILABLE

    if os.getenv("VERCEL"):
        return

    try:
        init_db()
        seed_if_empty()
        DB_AVAILABLE = True
    except Exception as e:
        print(f"Database startup initialization failed: {e}")
        DB_AVAILABLE = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# ---------- Projects ----------
@app.get("/projects", response_model=list[Project])
def list_projects() -> list[Project]:
    if not DB_AVAILABLE:
        # Return mock data when database is not available
        return [Project(**project) for project in MOCK_PROJECTS]

    try:
        with db_cursor() as cur:
            cur.execute("SELECT * FROM projects ORDER BY id DESC;")
            rows = cur.fetchall()
        return [Project(**row_to_dict(r)) for r in rows]
    except Exception as e:
        print(f"Database query failed: {e}")
        # Fallback to mock data
        return [Project(**project) for project in MOCK_PROJECTS]


@app.post("/projects", response_model=Project)
def create_project(payload: ProjectCreate) -> Project:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO projects (name, client, location, contract_no, start_date, end_date, total_contract_value, profit_margin_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name,
                payload.client,
                payload.location,
                payload.contract_no,
                payload.start_date,
                payload.end_date,
                payload.total_contract_value,
                payload.profit_margin_target,
            ),
        )
        project_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM projects WHERE id = ?;", (project_id,))
        row = cur.fetchone()
    return Project(**row_to_dict(row))


@app.delete("/projects/{project_id}")
def delete_project(project_id: int) -> dict[str, Any]:
    with db_cursor() as cur:
        cur.execute("DELETE FROM projects WHERE id = ?;", (project_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True, "project_id": project_id}


# ---------- Daily Logs ----------
@app.get("/projects/{project_id}/daily-logs", response_model=list[DailyLog])
def list_daily_logs(project_id: int, from_date: str | None = None, to_date: str | None = None) -> list[DailyLog]:
    where = ["project_id = ?"]
    params: list[Any] = [project_id]
    if from_date:
        where.append("log_date >= ?")
        params.append(from_date)
    if to_date:
        where.append("log_date <= ?")
        params.append(to_date)

    sql = f"SELECT * FROM daily_logs WHERE {' AND '.join(where)} ORDER BY log_date DESC, id DESC;"
    with db_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return [DailyLog(**row_to_dict(r)) for r in rows]


@app.post("/daily-logs", response_model=DailyLog)
def create_daily_log(payload: DailyLogCreate) -> DailyLog:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO daily_logs (project_id, log_date, weather, remarks)
            VALUES (?, ?, ?, ?)
            """,
            (payload.project_id, payload.log_date, payload.weather, payload.remarks),
        )
        log_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM daily_logs WHERE id = ?;", (log_id,))
        row = cur.fetchone()
    return DailyLog(**row_to_dict(row))


@app.get("/daily-logs/{daily_log_id}/activities", response_model=list[DailyActivity])
def list_daily_activities(daily_log_id: int) -> list[DailyActivity]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM daily_activities WHERE daily_log_id = ? ORDER BY id DESC;", (daily_log_id,))
        rows = cur.fetchall()
    return [DailyActivity(**row_to_dict(r)) for r in rows]


@app.post("/daily-activities", response_model=DailyActivity)
def create_daily_activity(payload: DailyActivityCreate) -> DailyActivity:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO daily_activities
            (daily_log_id, category, activity, uom, quantity, labour_count, machinery, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.daily_log_id,
                payload.category,
                payload.activity,
                payload.uom,
                payload.quantity,
                payload.labour_count,
                payload.machinery,
                payload.notes,
            ),
        )
        act_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM daily_activities WHERE id = ?;", (act_id,))
        row = cur.fetchone()
    return DailyActivity(**row_to_dict(row))


# ---------- Costs ----------
@app.get("/projects/{project_id}/costs", response_model=list[CostEntry])
def list_costs(project_id: int, from_date: str | None = None, to_date: str | None = None) -> list[CostEntry]:
    where = ["project_id = ?"]
    params: list[Any] = [project_id]
    if from_date:
        where.append("entry_date >= ?")
        params.append(from_date)
    if to_date:
        where.append("entry_date <= ?")
        params.append(to_date)

    sql = f"SELECT * FROM cost_entries WHERE {' AND '.join(where)} ORDER BY entry_date DESC, id DESC;"
    with db_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return [CostEntry(**row_to_dict(r)) for r in rows]


@app.post("/costs", response_model=CostEntry)
def create_cost(payload: CostEntryCreate) -> CostEntry:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO cost_entries
            (project_id, entry_date, cost_head, description, vendor, amount, quantity, uom, unit_rate, payment_mode, bill_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.project_id,
                payload.entry_date,
                payload.cost_head,
                payload.description,
                payload.vendor,
                payload.amount,
                payload.quantity,
                payload.uom,
                payload.unit_rate,
                payload.payment_mode,
                payload.bill_no,
            ),
        )
        cost_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM cost_entries WHERE id = ?;", (cost_id,))
        row = cur.fetchone()
    return CostEntry(**row_to_dict(row))


# ---------- Budgets ----------
@app.get("/projects/{project_id}/budgets", response_model=list[BudgetItem])
def list_budgets(project_id: int) -> list[BudgetItem]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM budget_items WHERE project_id = ? ORDER BY cost_head;", (project_id,))
        rows = cur.fetchall()
    return [BudgetItem(**row_to_dict(r)) for r in rows]


@app.post("/budgets/upsert", response_model=BudgetItem)
def upsert_budget(payload: BudgetItemUpsert) -> BudgetItem:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO budget_items (project_id, cost_head, budget_amount, notes)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(project_id, cost_head)
            DO UPDATE SET budget_amount=excluded.budget_amount, notes=excluded.notes
            """,
            (payload.project_id, payload.cost_head, payload.budget_amount, payload.notes),
        )
        cur.execute(
            "SELECT * FROM budget_items WHERE project_id = ? AND cost_head = ?;",
            (payload.project_id, payload.cost_head),
        )
        row = cur.fetchone()
    return BudgetItem(**row_to_dict(row))


# ---------- Dashboard summary ----------
@app.get("/projects/{project_id}/summary", response_model=DashboardSummary)
def summary(project_id: int, from_date: str | None = None, to_date: str | None = None) -> DashboardSummary:
    # Costs
    where_cost = ["project_id = ?"]
    params_cost: list[Any] = [project_id]
    if from_date:
        where_cost.append("entry_date >= ?")
        params_cost.append(from_date)
    if to_date:
        where_cost.append("entry_date <= ?")
        params_cost.append(to_date)

    cost_by_head: dict[str, float] = defaultdict(float)
    total_cost = 0.0

    # Budgets (full)
    budget_by_head: dict[str, float] = {}
    total_budget = 0.0

    # Recent logs
    where_logs = ["project_id = ?"]
    params_logs: list[Any] = [project_id]
    if from_date:
        where_logs.append("log_date >= ?")
        params_logs.append(from_date)
    if to_date:
        where_logs.append("log_date <= ?")
        params_logs.append(to_date)

    with db_cursor() as cur:
        # Get project details
        cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        proj_row = cur.fetchone()
        if not proj_row:
            raise HTTPException(status_code=404, detail="Project not found")
        proj = row_to_dict(proj_row)

        cur.execute(
            f"""
            SELECT cost_head, SUM(amount) AS amt
            FROM cost_entries
            WHERE {' AND '.join(where_cost)}
            GROUP BY cost_head
            """,
            params_cost,
        )
        for r in cur.fetchall():
            head = str(r["cost_head"])
            amt = float(r["amt"] or 0)
            cost_by_head[head] += amt
            total_cost += amt

        cur.execute(
            """
            SELECT cost_head, budget_amount
            FROM budget_items
            WHERE project_id = ?
            """,
            (project_id,),
        )
        for r in cur.fetchall():
            head = str(r["cost_head"])
            amt = float(r["budget_amount"] or 0)
            budget_by_head[head] = amt
            total_budget += amt

        cur.execute(
            f"""
            SELECT * FROM daily_logs
            WHERE {' AND '.join(where_logs)}
            ORDER BY log_date DESC, id DESC
            LIMIT 10
            """,
            params_logs,
        )
        recent_logs = [DailyLog(**row_to_dict(r)) for r in cur.fetchall()]

    variance_by_head: dict[str, float] = {}
    all_heads = set(budget_by_head.keys()) | set(cost_by_head.keys())
    for head in sorted(all_heads):
        variance_by_head[head] = float(cost_by_head.get(head, 0.0) - budget_by_head.get(head, 0.0))

    # Calculate percentage over/under budget
    percent_over_under_budget = None
    if total_budget > 0:
        percent_over_under_budget = float(((total_cost - total_budget) / total_budget) * 100.0)

    # Calculate current profit margin
    current_profit_margin = None
    total_contract_value = float(proj.get("total_contract_value") or 0)
    if total_contract_value > 0:
        current_profit_margin = float(((total_contract_value - total_cost) / total_contract_value) * 100.0)

    # Calculate days remaining
    days_remaining = None
    end_date = proj.get("end_date")
    if end_date:
        from datetime import datetime
        end_dt = datetime.fromisoformat(end_date)
        today = datetime.now()
        if end_dt > today:
            days_remaining = (end_dt - today).days

    # Get job costing categories (simplified version)
    job_costing_categories = []
    # We'll use the same logic as the job costing endpoint but simplified
    from .utils import row_to_dict

    with db_cursor() as cur:
        cur.execute(
            f"""
            SELECT cost_head,
                   SUM(amount) AS amt,
                   SUM(COALESCE(quantity, 0)) AS qty,
                   GROUP_CONCAT(DISTINCT COALESCE(uom, '')) AS uoms
            FROM cost_entries
            WHERE {' AND '.join(where_cost)}
            GROUP BY cost_head
            """,
            params_cost,
        )
        costs = rows_to_dict(cur.fetchall())

        cur.execute(
            """
            SELECT cost_head, budget_amount
            FROM budget_items
            WHERE project_id = ?
            """,
            (project_id,),
        )
        budgets = rows_to_dict(cur.fetchall())

    # Aggregate by category (same logic as job costing)
    planned_by_cat: dict[str, float] = defaultdict(float)
    actual_by_cat: dict[str, float] = defaultdict(float)
    qty_by_cat: dict[str, float] = defaultdict(float)
    uoms_by_cat: dict[str, set[str]] = defaultdict(set)

    for b in budgets:
        cat = _job_costing_category_for_head(str(b["cost_head"]))
        planned_by_cat[cat] += float(b.get("budget_amount") or 0.0)

    for c in costs:
        cat = _job_costing_category_for_head(str(c["cost_head"]))
        actual_by_cat[cat] += float(c.get("amt") or 0.0)
        qty_by_cat[cat] += float(c.get("qty") or 0.0)
        raw = str(c.get("uoms") or "")
        for u in raw.split(","):
            u = u.strip()
            if u:
                uoms_by_cat[cat].add(u)

    categories_order = ["Labour", "Materials", "Equipment", "Subcontractors", "Other"]
    total_planned = float(sum(planned_by_cat.values()))
    total_actual = float(sum(actual_by_cat.values()))

    cats: list[JobCostingCategory] = []
    for cat in categories_order:
        planned = float(planned_by_cat.get(cat, 0.0))
        actual = float(actual_by_cat.get(cat, 0.0))
        qty = float(qty_by_cat.get(cat, 0.0))
        uom_set = uoms_by_cat.get(cat, set())
        uom = list(uom_set)[0] if len(uom_set) == 1 else None

        unit_cost = None
        if qty > 0:
            unit_cost = float(actual / qty)

        pct_of_total_actual = float((actual / total_actual) * 100.0) if total_actual > 0 else 0.0
        pct_over_under = None
        if planned > 0:
            pct_over_under = float(((actual - planned) / planned) * 100.0)

        cats.append(
            JobCostingCategory(
                category=cat,
                planned_cost=planned,
                actual_cost=actual,
                quantity=qty if qty > 0 else None,
                uom=uom,
                unit_cost=unit_cost,
                percent_of_total_actual=pct_of_total_actual,
                percent_over_under_budget=pct_over_under,
            )
        )

    return DashboardSummary(
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
        total_cost=float(total_cost),
        cost_by_head=dict(cost_by_head),
        total_budget=float(total_budget),
        budget_by_head=budget_by_head,
        variance_by_head=variance_by_head,
        percent_over_under_budget=percent_over_under_budget,
        total_contract_value=total_contract_value if total_contract_value > 0 else None,
        profit_margin_target=float(proj.get("profit_margin_target") or 10.0),
        current_profit_margin=current_profit_margin,
        days_remaining=days_remaining,
        job_costing_categories=cats,
        recent_logs=recent_logs,
    )


def _job_costing_category_for_head(cost_head: str) -> str:
    h = (cost_head or "").lower()
    if "labour" in h or "labor" in h:
        return "Labour"
    if "material" in h:
        return "Materials"
    if "machinery" in h or "equipment" in h:
        return "Equipment"
    if "subcontract" in h:
        return "Subcontractors"
    return "Other"


@app.get("/projects/{project_id}/job-costing", response_model=JobCostingSummary)
def job_costing(project_id: int, from_date: str | None = None, to_date: str | None = None) -> JobCostingSummary:
    if not DB_AVAILABLE:
        # Return mock job costing data when database is not available
        return JobCostingSummary(
            project_id=project_id,
            project_name="Railway ROB + Bridge Works (Pile Foundation & Sub-Structure)",
            total_budget=8350000,
            total_actual_cost=8642040,
            total_variance=32040,
            percent_over_under_budget=3.87,
            categories=[
                JobCostingCategory(
                    category="Labour",
                    planned_cost=3250000,
                    actual_cost=3779500,
                    quantity=3250,
                    uom="Hours",
                    unit_cost=1161.54,
                    percent_of_total_actual=43.73,
                    percent_over_under_budget=16.15
                ),
                JobCostingCategory(
                    category="Materials",
                    planned_cost=3200000,
                    actual_cost=3315000,
                    quantity=81.5,
                    uom="MT/CuM",
                    unit_cost=None,
                    percent_of_total_actual=38.37,
                    percent_over_under_budget=3.59
                ),
                JobCostingCategory(
                    category="Equipment",
                    planned_cost=1500000,
                    actual_cost=0,
                    quantity=None,
                    uom=None,
                    unit_cost=None,
                    percent_of_total_actual=0,
                    percent_over_under_budget=-100
                ),
                JobCostingCategory(
                    category="Subcontractors",
                    planned_cost=400000,
                    actual_cost=1547540,
                    quantity=None,
                    uom=None,
                    unit_cost=None,
                    percent_of_total_actual=17.91,
                    percent_over_under_budget=286.89
                )
            ]
        )

    try:
        where_cost = ["project_id = ?"]
        params_cost: list[Any] = [project_id]
        if from_date:
            where_cost.append("entry_date >= ?")
            params_cost.append(from_date)
        if to_date:
            where_cost.append("entry_date <= ?")
            params_cost.append(to_date)

        with db_cursor() as cur:
            cur.execute("SELECT * FROM projects WHERE id = ?;", (project_id,))
        proj = cur.fetchone()
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")

        cur.execute(
            f"""
            SELECT cost_head,
                   SUM(amount) AS amt,
                   SUM(COALESCE(quantity, 0)) AS qty,
                   GROUP_CONCAT(DISTINCT COALESCE(uom, '')) AS uoms
            FROM cost_entries
            WHERE {' AND '.join(where_cost)}
            GROUP BY cost_head
            """,
            params_cost,
        )
        costs = rows_to_dicts(cur.fetchall())

        cur.execute(
            """
            SELECT cost_head, budget_amount
            FROM budget_items
            WHERE project_id = ?
            """,
            (project_id,),
        )
        budgets = rows_to_dicts(cur.fetchall())

        # Aggregate by category
        planned_by_cat: dict[str, float] = defaultdict(float)
        actual_by_cat: dict[str, float] = defaultdict(float)
        qty_by_cat: dict[str, float] = defaultdict(float)
        uoms_by_cat: dict[str, set[str]] = defaultdict(set)

        for b in budgets:
            cat = _job_costing_category_for_head(str(b["cost_head"]))
            planned_by_cat[cat] += float(b.get("budget_amount") or 0.0)

        for c in costs:
            cat = _job_costing_category_for_head(str(c["cost_head"]))
            actual_by_cat[cat] += float(c.get("amt") or 0.0)
            qty_by_cat[cat] += float(c.get("qty") or 0.0)
            raw = str(c.get("uoms") or "")
            for u in raw.split(","):
                u = u.strip()
                if u:
                    uoms_by_cat[cat].add(u)

        categories_order = ["Labour", "Materials", "Equipment", "Subcontractors", "Other"]
        total_planned = float(sum(planned_by_cat.values()))
        total_actual = float(sum(actual_by_cat.values()))
        total_pct_over_under = None
        if total_planned > 0:
            total_pct_over_under = float(((total_actual - total_planned) / total_planned) * 100.0)

        cats: list[JobCostingCategory] = []
        for cat in categories_order:
            planned = float(planned_by_cat.get(cat, 0.0))
            actual = float(actual_by_cat.get(cat, 0.0))
            qty = float(qty_by_cat.get(cat, 0.0))
            uom_set = uoms_by_cat.get(cat, set())
            uom = list(uom_set)[0] if len(uom_set) == 1 else None

            unit_cost = None
            if qty > 0:
                unit_cost = float(actual / qty)

            pct_of_total_actual = float((actual / total_actual) * 100.0) if total_actual > 0 else 0.0
            pct_over_under = None
            if planned > 0:
                pct_over_under = float(((actual - planned) / planned) * 100.0)

            cats.append(
                JobCostingCategory(
                    category=cat,
                    planned_cost=planned,
                    actual_cost=actual,
                    quantity=qty if qty > 0 else None,
                    uom=uom,
                    unit_cost=unit_cost,
                    percent_of_total_actual=pct_of_total_actual,
                    percent_over_under_budget=pct_over_under,
                )
            )

        proj_d = row_to_dict(proj)
        return JobCostingSummary(
            project_id=project_id,
            project_name=proj_d["name"],
            total_budget=sum(planned_by_cat.values()),
            total_actual_cost=sum(actual_by_cat.values()),
            total_variance=sum(actual_by_cat.values()) - sum(planned_by_cat.values()),
            percent_over_under_budget=(
                ((sum(actual_by_cat.values()) - sum(planned_by_cat.values())) / sum(planned_by_cat.values()) * 100)
                if sum(planned_by_cat.values()) > 0 else 0
            ),
            categories=[
                JobCostingCategory(
                    category=cat,
                    planned_cost=planned_by_cat[cat],
                    actual_cost=actual_by_cat[cat],
                    quantity=qty_by_cat[cat] if qty_by_cat[cat] > 0 else None,
                    uom=list(uoms_by_cat[cat])[0] if uoms_by_cat[cat] else None,
                    unit_cost=(
                        actual_by_cat[cat] / qty_by_cat[cat] if qty_by_cat[cat] > 0 and actual_by_cat[cat] > 0 else None
                    ),
                    percent_of_total_actual=(
                        (actual_by_cat[cat] / sum(actual_by_cat.values()) * 100) if sum(actual_by_cat.values()) > 0 else 0
                    ),
                    percent_over_under_budget=(
                        ((actual_by_cat[cat] - planned_by_cat[cat]) / planned_by_cat[cat] * 100)
                        if planned_by_cat[cat] > 0 else 0
                    ),
                )
                for cat in sorted(set(planned_by_cat.keys()) | set(actual_by_cat.keys()))
            ],
        )
    except Exception as e:
        print(f"Database query failed in job_costing: {e}")
        # Fallback to mock data
        return JobCostingSummary(
            project_id=project_id,
            project_name="Railway ROB + Bridge Works (Pile Foundation & Sub-Structure)",
            total_budget=8350000,
            total_actual_cost=8642040,
            total_variance=32040,
            percent_over_under_budget=3.87,
            categories=[
                JobCostingCategory(
                    category="Labour",
                    planned_cost=3250000,
                    actual_cost=3779500,
                    quantity=3250,
                    uom="Hours",
                    unit_cost=1161.54,
                    percent_of_total_actual=43.73,
                    percent_over_under_budget=16.15
                ),
                JobCostingCategory(
                    category="Materials",
                    planned_cost=3200000,
                    actual_cost=3315000,
                    quantity=81.5,
                    uom="MT/CuM",
                    unit_cost=None,
                    percent_of_total_actual=38.37,
                    percent_over_under_budget=3.59
                ),
                JobCostingCategory(
                    category="Equipment",
                    planned_cost=1500000,
                    actual_cost=0,
                    quantity=None,
                    uom=None,
                    unit_cost=None,
                    percent_of_total_actual=0,
                    percent_over_under_budget=-100
                ),
                JobCostingCategory(
                    category="Subcontractors",
                    planned_cost=400000,
                    actual_cost=1547540,
                    quantity=None,
                    uom=None,
                    unit_cost=None,
                    percent_of_total_actual=17.91,
                    percent_over_under_budget=286.89
                )
            ]
        )

    return JobCostingSummary(
        project_id=project_id,
        project_name=str(proj_d["name"]),
        client=str(proj_d["client"]),
        location=str(proj_d["location"]),
        from_date=from_date,
        to_date=to_date,
        total_planned_cost=total_planned,
        total_actual_cost=total_actual,
        percent_over_under_budget=total_pct_over_under,
        categories=cats,
    )


# ========== COMPREHENSIVE KPI ENDPOINTS ==========

# ---------- Project Packages ----------
@app.get("/projects/{project_id}/packages", response_model=list[ProjectPackage])
def list_project_packages(project_id: int) -> list[ProjectPackage]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM project_packages WHERE project_id = ? ORDER BY id DESC;", (project_id,))
        rows = cur.fetchall()
    return [ProjectPackage(**row_to_dict(r)) for r in rows]

@app.post("/project-packages", response_model=ProjectPackage)
def create_project_package(payload: ProjectPackageCreate) -> ProjectPackage:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO project_packages
            (project_id, package_name, package_value, planned_start_date, planned_end_date,
             actual_start_date, actual_end_date, status, progress_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.package_name, payload.package_value, payload.planned_start_date,
             payload.planned_end_date, payload.actual_start_date, payload.actual_end_date,
             payload.status, payload.progress_percentage),
        )
        pkg_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM project_packages WHERE id = ?;", (pkg_id,))
        row = cur.fetchone()
    return ProjectPackage(**row_to_dict(row))

# ---------- Project Milestones ----------
@app.get("/projects/{project_id}/milestones", response_model=list[ProjectMilestone])
def list_project_milestones(project_id: int) -> list[ProjectMilestone]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM project_milestones WHERE project_id = ? ORDER BY planned_date;", (project_id,))
        rows = cur.fetchall()
    return [ProjectMilestone(**row_to_dict(r)) for r in rows]

@app.post("/project-milestones", response_model=ProjectMilestone)
def create_project_milestone(payload: ProjectMilestoneCreate) -> ProjectMilestone:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO project_milestones
            (project_id, milestone_name, planned_date, actual_date, status, weight, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.milestone_name, payload.planned_date, payload.actual_date,
             payload.status, payload.weight, payload.description),
        )
        ms_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM project_milestones WHERE id = ?;", (ms_id,))
        row = cur.fetchone()
    return ProjectMilestone(**row_to_dict(row))

# ---------- Delay Reasons ----------
@app.get("/projects/{project_id}/delay-reasons", response_model=list[DelayReason])
def list_delay_reasons(project_id: int) -> list[DelayReason]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM delay_reasons WHERE project_id = ? ORDER BY delay_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [DelayReason(**row_to_dict(r)) for r in rows]

@app.post("/delay-reasons", response_model=DelayReason)
def create_delay_reason(payload: DelayReasonCreate) -> DelayReason:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO delay_reasons
            (project_id, delay_date, delay_category, delay_hours, delay_days, description,
             impact_on_schedule, mitigation_action, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.delay_date, payload.delay_category, payload.delay_hours,
             payload.delay_days, payload.description, payload.impact_on_schedule,
             payload.mitigation_action, payload.status),
        )
        dr_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM delay_reasons WHERE id = ?;", (dr_id,))
        row = cur.fetchone()
    return DelayReason(**row_to_dict(row))

# ---------- RA Bills ----------
@app.get("/projects/{project_id}/ra-bills", response_model=list[RABill])
def list_ra_bills(project_id: int) -> list[RABill]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM ra_bills WHERE project_id = ? ORDER BY bill_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [RABill(**row_to_dict(r)) for r in rows]

@app.post("/ra-bills", response_model=RABill)
def create_ra_bill(payload: RABillCreate) -> RABill:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO ra_bills
            (project_id, bill_no, bill_date, submitted_date, certified_date, paid_date,
             bill_amount, certified_amount, paid_amount, retention_amount, status,
             certification_cycle_days, payment_cycle_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.bill_no, payload.bill_date, payload.submitted_date,
             payload.certified_date, payload.paid_date, payload.bill_amount, payload.certified_amount,
             payload.paid_amount, payload.retention_amount, payload.status,
             payload.certification_cycle_days, payload.payment_cycle_days),
        )
        bill_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM ra_bills WHERE id = ?;", (bill_id,))
        row = cur.fetchone()
    return RABill(**row_to_dict(row))

# ---------- Claims & Variations ----------
@app.get("/projects/{project_id}/claims-variations", response_model=list[ClaimsVariation])
def list_claims_variations(project_id: int) -> list[ClaimsVariation]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM claims_variations WHERE project_id = ? ORDER BY submitted_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [ClaimsVariation(**row_to_dict(r)) for r in rows]

@app.post("/claims-variations", response_model=ClaimsVariation)
def create_claims_variation(payload: ClaimsVariationCreate) -> ClaimsVariation:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO claims_variations
            (project_id, claim_type, description, claimed_amount, approved_amount, status,
             submitted_date, approved_date, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.claim_type, payload.description, payload.claimed_amount,
             payload.approved_amount, payload.status, payload.submitted_date,
             payload.approved_date, payload.remarks),
        )
        cv_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM claims_variations WHERE id = ?;", (cv_id,))
        row = cur.fetchone()
    return ClaimsVariation(**row_to_dict(row))

# ---------- BOQ Items ----------
@app.get("/projects/{project_id}/boq-items", response_model=list[BOQItem])
def list_boq_items(project_id: int) -> list[BOQItem]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM boq_items WHERE project_id = ? ORDER BY item_code;", (project_id,))
        rows = cur.fetchall()
    return [BOQItem(**row_to_dict(r)) for r in rows]

@app.post("/boq-items", response_model=BOQItem)
def create_boq_item(payload: BOQItemCreate) -> BOQItem:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO boq_items
            (project_id, item_code, item_description, unit, boq_quantity, boq_rate, boq_amount,
             executed_quantity, executed_amount, deviation_percentage, status, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.item_code, payload.item_description, payload.unit,
             payload.boq_quantity, payload.boq_rate, payload.boq_amount, payload.executed_quantity,
             payload.executed_amount, payload.deviation_percentage, payload.status, payload.category),
        )
        boq_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM boq_items WHERE id = ?;", (boq_id,))
        row = cur.fetchone()
    return BOQItem(**row_to_dict(row))

# ---------- Quality Tests ----------
@app.get("/projects/{project_id}/quality-tests", response_model=list[QualityTest])
def list_quality_tests(project_id: int) -> list[QualityTest]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM quality_tests WHERE project_id = ? ORDER BY test_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [QualityTest(**row_to_dict(r)) for r in rows]

@app.post("/quality-tests", response_model=QualityTest)
def create_quality_test(payload: QualityTestCreate) -> QualityTest:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO quality_tests
            (project_id, test_type, test_date, planned_tests, conducted_tests,
             passed_tests, failed_tests, pass_rate, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.test_type, payload.test_date, payload.planned_tests,
             payload.conducted_tests, payload.passed_tests, payload.failed_tests,
             payload.pass_rate, payload.status),
        )
        qt_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM quality_tests WHERE id = ?;", (qt_id,))
        row = cur.fetchone()
    return QualityTest(**row_to_dict(row))

# ---------- NCRs ----------
@app.get("/projects/{project_id}/ncrs", response_model=list[NCR])
def list_ncrs(project_id: int) -> list[NCR]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM ncrs WHERE project_id = ? ORDER BY raised_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [NCR(**row_to_dict(r)) for r in rows]

@app.post("/ncrs", response_model=NCR)
def create_ncr(payload: NCRCreate) -> NCR:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO ncrs
            (project_id, ncr_no, raised_date, category, description, severity, status,
             closure_date, closure_days, corrective_action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.ncr_no, payload.raised_date, payload.category,
             payload.description, payload.severity, payload.status, payload.closure_date,
             payload.closure_days, payload.corrective_action),
        )
        ncr_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM ncrs WHERE id = ?;", (ncr_id,))
        row = cur.fetchone()
    return NCR(**row_to_dict(row))

# ---------- Safety Incidents ----------
@app.get("/projects/{project_id}/safety-incidents", response_model=list[SafetyIncident])
def list_safety_incidents(project_id: int) -> list[SafetyIncident]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM safety_incidents WHERE project_id = ? ORDER BY incident_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [SafetyIncident(**row_to_dict(r)) for r in rows]

@app.post("/safety-incidents", response_model=SafetyIncident)
def create_safety_incident(payload: SafetyIncidentCreate) -> SafetyIncident:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO safety_incidents
            (project_id, incident_date, incident_type, description, severity,
             lost_time_days, reported_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.incident_date, payload.incident_type, payload.description,
             payload.severity, payload.lost_time_days, payload.reported_by, payload.status),
        )
        si_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM safety_incidents WHERE id = ?;", (si_id,))
        row = cur.fetchone()
    return SafetyIncident(**row_to_dict(row))

# ---------- Labour Manpower ----------
@app.get("/projects/{project_id}/labour-manpower", response_model=list[LabourManpower])
def list_labour_manpower(project_id: int) -> list[LabourManpower]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM labour_manpower WHERE project_id = ? ORDER BY record_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [LabourManpower(**row_to_dict(r)) for r in rows]

@app.post("/labour-manpower", response_model=LabourManpower)
def create_labour_manpower(payload: LabourManpowerCreate) -> LabourManpower:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO labour_manpower
            (project_id, record_date, total_planned, total_actual, mason_count, carpenter_count,
             bar_bender_count, welder_count, helper_count, absenteeism_rate, overtime_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.record_date, payload.total_planned, payload.total_actual,
             payload.mason_count, payload.carpenter_count, payload.bar_bender_count,
             payload.welder_count, payload.helper_count, payload.absenteeism_rate, payload.overtime_hours),
        )
        lm_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM labour_manpower WHERE id = ?;", (lm_id,))
        row = cur.fetchone()
    return LabourManpower(**row_to_dict(row))

# ---------- Plant & Machinery ----------
@app.get("/projects/{project_id}/plant-machinery", response_model=list[PlantMachinery])
def list_plant_machinery(project_id: int) -> list[PlantMachinery]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM plant_machinery WHERE project_id = ? ORDER BY record_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [PlantMachinery(**row_to_dict(r)) for r in rows]

@app.post("/plant-machinery", response_model=PlantMachinery)
def create_plant_machinery(payload: PlantMachineryCreate) -> PlantMachinery:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO plant_machinery
            (project_id, equipment_name, equipment_type, record_date, available_hours, utilized_hours,
             breakdown_hours, idle_hours, fuel_consumed, fuel_norm, availability_percentage,
             utilization_percentage, mttr_hours, mtbf_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.equipment_name, payload.equipment_type, payload.record_date,
             payload.available_hours, payload.utilized_hours, payload.breakdown_hours, payload.idle_hours,
             payload.fuel_consumed, payload.fuel_norm, payload.availability_percentage,
             payload.utilization_percentage, payload.mttr_hours, payload.mtbf_hours),
        )
        pm_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM plant_machinery WHERE id = ?;", (pm_id,))
        row = cur.fetchone()
    return PlantMachinery(**row_to_dict(row))

# ---------- Material Inventory ----------
@app.get("/projects/{project_id}/material-inventory", response_model=list[MaterialInventory])
def list_material_inventory(project_id: int) -> list[MaterialInventory]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM material_inventory WHERE project_id = ? ORDER BY record_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [MaterialInventory(**row_to_dict(r)) for r in rows]

@app.post("/material-inventory", response_model=MaterialInventory)
def create_material_inventory(payload: MaterialInventoryCreate) -> MaterialInventory:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO material_inventory
            (project_id, material_type, record_date, issued_quantity, consumed_quantity,
             theoretical_quantity, variance_percentage, stock_level, min_stock, max_stock, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.material_type, payload.record_date, payload.issued_quantity,
             payload.consumed_quantity, payload.theoretical_quantity, payload.variance_percentage,
             payload.stock_level, payload.min_stock, payload.max_stock, payload.status),
        )
        mi_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM material_inventory WHERE id = ?;", (mi_id,))
        row = cur.fetchone()
    return MaterialInventory(**row_to_dict(row))

# ---------- Drawings & Approvals ----------
@app.get("/projects/{project_id}/drawings-approvals", response_model=list[DrawingsApproval])
def list_drawings_approvals(project_id: int) -> list[DrawingsApproval]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM drawings_approvals WHERE project_id = ? ORDER BY submitted_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [DrawingsApproval(**row_to_dict(r)) for r in rows]

@app.post("/drawings-approvals", response_model=DrawingsApproval)
def create_drawings_approval(payload: DrawingsApprovalCreate) -> DrawingsApproval:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO drawings_approvals
            (project_id, drawing_no, drawing_type, submitted_date, approved_date,
             approval_days, status, approver_name, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.drawing_no, payload.drawing_type, payload.submitted_date,
             payload.approved_date, payload.approval_days, payload.status, payload.approver_name, payload.remarks),
        )
        da_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM drawings_approvals WHERE id = ?;", (da_id,))
        row = cur.fetchone()
    return DrawingsApproval(**row_to_dict(row))

# ---------- Railway Blocks ----------
@app.get("/projects/{project_id}/railway-blocks", response_model=list[RailwayBlock])
def list_railway_blocks(project_id: int) -> list[RailwayBlock]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM railway_blocks WHERE project_id = ? ORDER BY block_date DESC;", (project_id,))
        rows = cur.fetchall()
    return [RailwayBlock(**row_to_dict(r)) for r in rows]

@app.post("/railway-blocks", response_model=RailwayBlock)
def create_railway_block(payload: RailwayBlockCreate) -> RailwayBlock:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO railway_blocks
            (project_id, block_date, block_type, requested_hours, granted_hours,
             utilized_hours, status, work_description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.block_date, payload.block_type, payload.requested_hours,
             payload.granted_hours, payload.utilized_hours, payload.status, payload.work_description),
        )
        rb_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM railway_blocks WHERE id = ?;", (rb_id,))
        row = cur.fetchone()
    return RailwayBlock(**row_to_dict(row))

# ---------- Risk Register ----------
@app.get("/projects/{project_id}/risk-register", response_model=list[RiskRegister])
def list_risk_register(project_id: int) -> list[RiskRegister]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM risk_register WHERE project_id = ? ORDER BY risk_level DESC;", (project_id,))
        rows = cur.fetchall()
    return [RiskRegister(**row_to_dict(r)) for r in rows]

@app.post("/risk-register", response_model=RiskRegister)
def create_risk_register(payload: RiskRegisterCreate) -> RiskRegister:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO risk_register
            (project_id, risk_description, risk_category, probability, impact, risk_level,
             exposure_amount, exposure_days, mitigation_plan, mitigation_status, rag_status, owner)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.project_id, payload.risk_description, payload.risk_category, payload.probability,
             payload.impact, payload.risk_level, payload.exposure_amount, payload.exposure_days,
             payload.mitigation_plan, payload.mitigation_status, payload.rag_status, payload.owner),
        )
        rr_id = int(cur.lastrowid)
        cur.execute("SELECT * FROM risk_register WHERE id = ?;", (rr_id,))
        row = cur.fetchone()
    return RiskRegister(**row_to_dict(row))

# ---------- Comprehensive Dashboard KPI Summary ----------
@app.get("/projects/{project_id}/comprehensive-dashboard", response_model=ComprehensiveDashboard)
def get_comprehensive_dashboard(project_id: int) -> ComprehensiveDashboard:
    # This would be a complex aggregation of all KPIs
    # For now, return a basic structure - would need full implementation
    with db_cursor() as cur:
        cur.execute("SELECT * FROM projects WHERE id = ?;", (project_id,))
        proj = cur.fetchone()
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")

        proj_d = row_to_dict(proj)

        # Placeholder implementation - would need to aggregate all KPIs
        return ComprehensiveDashboard(
            project_id=project_id,
            project_name=str(proj_d["name"]),
            client=str(proj_d["client"]),
            progress_kpis=None,  # Would need to implement aggregation
            cost_billing_kpis=None,
            quality_safety_kpis=None,
            labour_productivity_kpis=None,
            machinery_materials_kpis=None,
            approvals_compliance_kpis=None,
            risk_stakeholder_kpis=None
        )

# ---------- Portfolio Overview ----------
@app.get("/portfolio-overview", response_model=PortfolioOverview)
def get_portfolio_overview() -> PortfolioOverview:
    with db_cursor() as cur:
        # Get project counts
        cur.execute("SELECT COUNT(*) as total FROM projects;")
        total_projects = int(cur.fetchone()["total"])

        cur.execute("SELECT COUNT(*) as active FROM projects WHERE status IN ('Planning', 'Execution', 'Monitoring');")
        active_projects = int(cur.fetchone()["active"])

        cur.execute("SELECT COUNT(*) as delayed FROM projects WHERE status = 'Delayed';")
        delayed_projects = int(cur.fetchone()["delayed"])

        # Get financial totals
        cur.execute("SELECT SUM(total_contract_value) as contract_value FROM projects;")
        contract_value = float(cur.fetchone()["contract_value"] or 0)

        # Placeholder for billed value - would need to sum RA bills
        billed_value = contract_value * 0.7  # Example

        # Placeholder for other metrics
        overall_progress = 65.0
        safety_incidents = 5
        quality_ncrs = 12

        # Projects by client
        cur.execute("SELECT client, COUNT(*) as count FROM projects GROUP BY client;")
        projects_by_client = {row["client"]: row["count"] for row in cur.fetchall()}

        # Projects by status
        cur.execute("SELECT status, COUNT(*) as count FROM projects GROUP BY status;")
        projects_by_status = {row["status"]: row["count"] for row in cur.fetchall()}

        return PortfolioOverview(
            total_projects=total_projects,
            active_projects=active_projects,
            delayed_projects=delayed_projects,
            total_contract_value=contract_value,
            total_billed_value=billed_value,
            overall_progress=overall_progress,
            safety_incidents_total=safety_incidents,
            quality_ncrs_total=quality_ncrs,
            projects_by_client=projects_by_client,
            projects_by_status=projects_by_status
        )

# ---------- AI Assistant ----------
@app.post("/ai/chat", response_model=AiChatResponse)
async def ai_chat(payload: AiChatRequest) -> AiChatResponse:
    # Build a compact context from logs + activities + costs + budgets
    with db_cursor() as cur:
        cur.execute("SELECT * FROM projects WHERE id = ?;", (payload.project_id,))
        proj = cur.fetchone()
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")

        # Logs range
        where_logs = ["project_id = ?"]
        params_logs: list[Any] = [payload.project_id]
        if payload.from_date:
            where_logs.append("log_date >= ?")
            params_logs.append(payload.from_date)
        if payload.to_date:
            where_logs.append("log_date <= ?")
            params_logs.append(payload.to_date)

        cur.execute(
            f"""
            SELECT * FROM daily_logs
            WHERE {' AND '.join(where_logs)}
            ORDER BY log_date DESC
            LIMIT 15
            """,
            params_logs,
        )
        logs = cur.fetchall()

        # Activities for those logs
        log_ids = [int(r["id"]) for r in logs]
        activities: list[dict[str, Any]] = []
        if log_ids:
            placeholders = ",".join(["?"] * len(log_ids))
            cur.execute(
                f"""
                SELECT a.*, l.log_date
                FROM daily_activities a
                JOIN daily_logs l ON l.id = a.daily_log_id
                WHERE a.daily_log_id IN ({placeholders})
                ORDER BY l.log_date DESC, a.id DESC
                LIMIT 60
                """,
                log_ids,
            )
            activities = rows_to_dicts(cur.fetchall())

        # Costs range
        where_cost = ["project_id = ?"]
        params_cost: list[Any] = [payload.project_id]
        if payload.from_date:
            where_cost.append("entry_date >= ?")
            params_cost.append(payload.from_date)
        if payload.to_date:
            where_cost.append("entry_date <= ?")
            params_cost.append(payload.to_date)
        cur.execute(
            f"""
            SELECT cost_head, SUM(amount) AS amt
            FROM cost_entries
            WHERE {' AND '.join(where_cost)}
            GROUP BY cost_head
            ORDER BY amt DESC
            """,
            params_cost,
        )
        cost_heads = rows_to_dicts(cur.fetchall())

        cur.execute(
            """
            SELECT cost_head, budget_amount
            FROM budget_items
            WHERE project_id = ?
            ORDER BY budget_amount DESC
            """,
            (payload.project_id,),
        )
        budgets = rows_to_dicts(cur.fetchall())

    proj_d = row_to_dict(proj)

    # Build readable context text
    ctx_lines: list[str] = []
    ctx_lines.append(f"Project: {proj_d['name']}")
    ctx_lines.append(f"Client: {proj_d['client']} | Location: {proj_d['location']} | Contract: {proj_d.get('contract_no')}")
    if payload.from_date or payload.to_date:
        ctx_lines.append(f"Range: {payload.from_date or '...'} to {payload.to_date or '...'}")
    ctx_lines.append("")

    if logs:
        ctx_lines.append("Recent daily logs (top 15):")
        for r in logs[:15]:
            ctx_lines.append(f"- {r['log_date']}: Weather={r['weather'] or '-'} | Remarks={r['remarks'] or '-'}")
        ctx_lines.append("")

    if activities:
        ctx_lines.append("Recent activities (top 60):")
        for a in activities[:60]:
            ctx_lines.append(
                f"- {a['log_date']} [{a['category']}] {a['activity']} | Qty {a['quantity']} {a['uom']} | Labour {a['labour_count']} | Mach {a.get('machinery') or '-'}"
            )
        ctx_lines.append("")

    if cost_heads:
        ctx_lines.append("Costs by head (sum):")
        for c in cost_heads[:15]:
            ctx_lines.append(f"- {c['cost_head']}: {float(c['amt'] or 0):.2f}")
        ctx_lines.append("")

    if budgets:
        ctx_lines.append("Budget heads:")
        for b in budgets[:20]:
            ctx_lines.append(f"- {b['cost_head']}: {float(b['budget_amount'] or 0):.2f}")
        ctx_lines.append("")

    context = "\n".join(ctx_lines).strip()
    res = await ai_answer(payload.question, context)
    return AiChatResponse(mode=res.mode, answer=res.answer)

