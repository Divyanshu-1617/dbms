from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ..database import get_db, init_database

router = APIRouter(prefix="/api/admin", tags=["Admin & Database Explorer"])

ALLOWED_TABLES = [
    "USER", "LOCATION", "VEHICLE", "BOOKING",
    "PAYMENT", "INSPECTION", "DAMAGE_PENALTY", "MAINTENANCE"
]


@router.get("/metrics")
def get_metrics() -> Dict[str, Any]:
    with get_db() as conn:
        users_count = conn.execute("SELECT COUNT(*) as c FROM USER").fetchone()["c"]
        vehicles_count = conn.execute("SELECT COUNT(*) as c FROM VEHICLE").fetchone()["c"]
        available_vehicles = conn.execute("SELECT COUNT(*) as c FROM VEHICLE WHERE vehicle_status = 'Available'").fetchone()["c"]
        maintenance_vehicles = conn.execute("SELECT COUNT(*) as c FROM VEHICLE WHERE vehicle_status = 'Under Maintenance'").fetchone()["c"]
        active_bookings = conn.execute("SELECT COUNT(*) as c FROM BOOKING WHERE booking_status IN ('Pending', 'Approved')").fetchone()["c"]
        completed_bookings = conn.execute("SELECT COUNT(*) as c FROM BOOKING WHERE booking_status = 'Completed'").fetchone()["c"]
        
        # Financials
        rev_row = conn.execute("SELECT SUM(amount) as total_rev, SUM(commission_amount) as total_comm, SUM(owner_earning) as total_owner FROM PAYMENT WHERE payment_type = 'Rental' AND payment_status = 'Success'").fetchone()
        
        # Open incidents
        open_incidents = conn.execute("SELECT COUNT(*) as c FROM DAMAGE_PENALTY WHERE resolution_status = 'Under review'").fetchone()["c"]

        return {
            "total_users": users_count,
            "total_vehicles": vehicles_count,
            "available_vehicles": available_vehicles,
            "vehicles_under_maintenance": maintenance_vehicles,
            "active_bookings": active_bookings,
            "completed_bookings": completed_bookings,
            "total_rental_revenue": rev_row["total_rev"] or 0.0,
            "platform_commission": rev_row["total_comm"] or 0.0,
            "owner_payouts": rev_row["total_owner"] or 0.0,
            "open_incidents": open_incidents,
        }


@router.get("/tables")
def list_database_tables():
    result = []
    with get_db() as conn:
        for t in ALLOWED_TABLES:
            count = conn.execute(f"SELECT COUNT(*) as c FROM {t}").fetchone()["c"]
            result.append({"table_name": t, "row_count": count})
    return result


@router.get("/tables/{table_name}")
def get_table_data(table_name: str):
    upper_name = table_name.upper()
    if upper_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail=f"Table {table_name} is not a valid schema table.")
    
    with get_db() as conn:
        rows = conn.execute(f"SELECT * FROM {upper_name}").fetchall()
        columns_info = conn.execute(f"PRAGMA table_info({upper_name})").fetchall()
        columns = [c["name"] for c in columns_info]
        return {
            "table_name": upper_name,
            "columns": columns,
            "row_count": len(rows),
            "rows": rows,
        }


@router.post("/reset-database")
def reset_db():
    init_database(seed=True)
    return {"status": "success", "message": "Database reset and seeded with initial scenario records."}
