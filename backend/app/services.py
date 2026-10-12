from datetime import datetime, date
import uuid
from typing import Optional, List, Dict, Any, Tuple
from .database import get_db


def generate_id(prefix: str) -> str:
    """Generate a readable ID like B101, P401, I501, etc."""
    return f"{prefix}_{uuid.uuid4().hex[:6].upper()}"


# ====================================================================
# USER SERVICES
# ====================================================================

def get_all_users() -> List[Dict[str, Any]]:
    with get_db() as conn:
        return conn.execute("SELECT * FROM USER ORDER BY created_at DESC").fetchall()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        return conn.execute("SELECT * FROM USER WHERE user_id = ?", (user_id,)).fetchone()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        return conn.execute("SELECT * FROM USER WHERE email = ?", (email,)).fetchone()


def create_user(data: Dict[str, Any]) -> Dict[str, Any]:
    user_id = data.get("user_id") or generate_id("U")
    verification_status = "Verified" if data.get("role") == "Tourist" else "Pending"
    account_status = "Active" if verification_status == "Verified" else "Inactive"

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO USER (user_id, name, email, phone, password, role, verification_status, account_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                data["name"],
                data["email"],
                data["phone"],
                data["password"],
                data["role"],
                data.get("verification_status", verification_status),
                data.get("account_status", account_status),
            ),
        )
    return get_user_by_id(user_id)


def update_user_verification(user_id: str, verification_status: str, account_status: str) -> Dict[str, Any]:
    with get_db() as conn:
        conn.execute(
            """
            UPDATE USER 
            SET verification_status = ?, account_status = ?
            WHERE user_id = ?
            """,
            (verification_status, account_status, user_id),
        )
    return get_user_by_id(user_id)


# ====================================================================
# LOCATION SERVICES
# ====================================================================

def get_all_locations() -> List[Dict[str, Any]]:
    with get_db() as conn:
        return conn.execute("SELECT * FROM LOCATION ORDER BY city, address").fetchall()


def create_location(data: Dict[str, Any]) -> Dict[str, Any]:
    loc_id = data.get("location_id") or generate_id("L")
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO LOCATION (location_id, address, city, state, pincode, pickup_instructions)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                loc_id,
                data["address"],
                data["city"],
                data["state"],
                data["pincode"],
                data.get("pickup_instructions"),
            ),
        )
        return conn.execute("SELECT * FROM LOCATION WHERE location_id = ?", (loc_id,)).fetchone()


# ====================================================================
# VEHICLE SERVICES
# ====================================================================

def get_all_vehicles(city: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    query = """
        SELECT v.*, l.city AS location_city, l.address AS location_address, u.name AS owner_name
        FROM VEHICLE v
        JOIN LOCATION l ON v.location_id = l.location_id
        JOIN USER u ON v.owner_id = u.user_id
        WHERE 1=1
    """
    params = []
    if city:
        query += " AND LOWER(l.city) = LOWER(?)"
        params.append(city)
    if status:
        query += " AND v.vehicle_status = ?"
        params.append(status)
    query += " ORDER BY v.brand, v.model"

    with get_db() as conn:
        return conn.execute(query, params).fetchall()


def get_vehicle_by_id(vehicle_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        return conn.execute(
            """
            SELECT v.*, l.city AS location_city, l.address AS location_address, u.name AS owner_name
            FROM VEHICLE v
            JOIN LOCATION l ON v.location_id = l.location_id
            JOIN USER u ON v.owner_id = u.user_id
            WHERE v.vehicle_id = ?
            """,
            (vehicle_id,),
        ).fetchone()


def create_vehicle(data: Dict[str, Any]) -> Dict[str, Any]:
    # Check owner verification
    owner = get_user_by_id(data["owner_id"])
    if not owner:
        raise ValueError(f"Owner {data['owner_id']} does not exist.")
    if owner["account_status"] != "Active" or owner["verification_status"] != "Verified":
        raise ValueError("Owner must be verified and active before listing vehicles.")

    veh_id = data.get("vehicle_id") or generate_id("V")
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO VEHICLE (vehicle_id, owner_id, location_id, vehicle_number, vehicle_type,
                                 brand, model, year, rental_rate_per_day, security_deposit, vehicle_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                veh_id,
                data["owner_id"],
                data["location_id"],
                data["vehicle_number"],
                data["vehicle_type"],
                data["brand"],
                data["model"],
                data["year"],
                data["rental_rate_per_day"],
                data["security_deposit"],
                data.get("vehicle_status", "Available"),
            ),
        )
    return get_vehicle_by_id(veh_id)


def update_vehicle_status(vehicle_id: str, status: str):
    with get_db() as conn:
        conn.execute("UPDATE VEHICLE SET vehicle_status = ? WHERE vehicle_id = ?", (status, vehicle_id))


# ====================================================================
# BOOKING SERVICES & OVERLAP VALIDATION ENGINE
# ====================================================================

def check_booking_overlap(vehicle_id: str, start_date: str, end_date: str, exclude_booking_id: Optional[str] = None) -> bool:
    """
    Returns True if an overlapping booking already exists for the given dates that is 'Approved'.
    Two ranges [S1, E1] and [S2, E2] overlap if: (S1 <= E2) AND (E1 >= S2).
    """
    query = """
        SELECT COUNT(*) as count FROM BOOKING
        WHERE vehicle_id = ?
          AND booking_status = 'Approved'
          AND start_date <= ?
          AND end_date >= ?
    """
    params = [vehicle_id, end_date, start_date]
    if exclude_booking_id:
        query += " AND booking_id != ?"
        params.append(exclude_booking_id)

    with get_db() as conn:
        row = conn.execute(query, params).fetchone()
        return (row["count"] > 0)


def calculate_rental_amount(rate_per_day: float, start_date_str: str, end_date_str: str) -> float:
    d1 = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    d2 = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    days = (d2 - d1).days + 1
    if days < 1:
        raise ValueError("End date must be on or after start date.")
    return days * rate_per_day


def get_all_bookings(tourist_id: Optional[str] = None, owner_id: Optional[str] = None) -> List[Dict[str, Any]]:
    query = """
        SELECT b.*, u.name AS tourist_name, v.brand AS vehicle_brand, v.model AS vehicle_model,
               v.vehicle_number, v.security_deposit, v.owner_id,
               CASE WHEN p.payment_id IS NOT NULL THEN 1 ELSE 0 END AS is_paid,
               p.payment_status AS payment_status
        FROM BOOKING b
        JOIN USER u ON b.tourist_id = u.user_id
        JOIN VEHICLE v ON b.vehicle_id = v.vehicle_id
        LEFT JOIN PAYMENT p ON b.booking_id = p.booking_id AND p.payment_type = 'Rental' AND p.payment_status = 'Success'
        WHERE 1=1
    """
    params = []
    if tourist_id:
        query += " AND b.tourist_id = ?"
        params.append(tourist_id)
    if owner_id:
        query += " AND v.owner_id = ?"
        params.append(owner_id)
    query += " ORDER BY b.booking_date DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        for r in rows:
            r["is_paid"] = bool(r.get("is_paid"))
        return rows


def get_booking_by_id(booking_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT b.*, u.name AS tourist_name, v.brand AS vehicle_brand, v.model AS vehicle_model,
                   v.vehicle_number, v.security_deposit, v.owner_id,
                   CASE WHEN p.payment_id IS NOT NULL THEN 1 ELSE 0 END AS is_paid,
                   p.payment_status AS payment_status
            FROM BOOKING b
            JOIN USER u ON b.tourist_id = u.user_id
            JOIN VEHICLE v ON b.vehicle_id = v.vehicle_id
            LEFT JOIN PAYMENT p ON b.booking_id = p.booking_id AND p.payment_type = 'Rental' AND p.payment_status = 'Success'
            WHERE b.booking_id = ?
            """,
            (booking_id,),
        ).fetchone()
        if row:
            row["is_paid"] = bool(row.get("is_paid"))
        return row


def create_booking_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Creates a booking request.
    Enforces:
    1. Vehicle existence and status (blocked if Under Maintenance).
    2. Overlap check against existing approved bookings.
    """
    vehicle = get_vehicle_by_id(data["vehicle_id"])
    if not vehicle:
        raise ValueError(f"Vehicle {data['vehicle_id']} not found.")

    # Maintenance check (Scenario 9.5)
    if vehicle["vehicle_status"] == "Under Maintenance":
        raise ValueError("Vehicle is currently under maintenance and cannot be booked.")

    # Calculate rental amount
    rental_amount = calculate_rental_amount(vehicle["rental_rate_per_day"], data["start_date"], data["end_date"])

    # Overlap check (Scenario 9.3)
    is_overlapping = check_booking_overlap(data["vehicle_id"], data["start_date"], data["end_date"])
    booking_id = data.get("booking_id") or generate_id("B")

    if is_overlapping:
        # Automatically mark rejected due to overlap as described in Scenario 9.3
        status = "Rejected"
        cancellation_reason = "Requested dates overlap with an existing approved booking."
    else:
        status = "Pending"
        cancellation_reason = None

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO BOOKING (booking_id, tourist_id, vehicle_id, start_date, end_date,
                                 rental_amount, booking_status, cancellation_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                booking_id,
                data["tourist_id"],
                data["vehicle_id"],
                data["start_date"],
                data["end_date"],
                rental_amount,
                status,
                cancellation_reason,
            ),
        )

    warning = "Booking automatically rejected due to overlapping schedule." if is_overlapping else None
    return get_booking_by_id(booking_id), warning


def update_booking_status(booking_id: str, new_status: str, cancellation_reason: Optional[str] = None) -> Dict[str, Any]:
    booking = get_booking_by_id(booking_id)
    if not booking:
        raise ValueError(f"Booking {booking_id} not found.")

    # If owner tries to approve, re-check overlap
    if new_status == "Approved":
        if check_booking_overlap(booking["vehicle_id"], booking["start_date"], booking["end_date"], exclude_booking_id=booking_id):
            raise ValueError("Cannot approve: Overlaps with an already approved booking for this vehicle.")

    with get_db() as conn:
        conn.execute(
            """
            UPDATE BOOKING
            SET booking_status = ?, cancellation_reason = ?
            WHERE booking_id = ?
            """,
            (new_status, cancellation_reason, booking_id),
        )

    # Release vehicle status if cancelled or completed
    if new_status in ("Cancelled", "Completed", "Rejected"):
        update_vehicle_status(booking["vehicle_id"], "Available")

    return get_booking_by_id(booking_id)


# ====================================================================
# PAYMENT SERVICES
# ====================================================================

def get_payments_for_booking(booking_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        return conn.execute("SELECT * FROM PAYMENT WHERE booking_id = ? ORDER BY payment_date ASC", (booking_id,)).fetchall()


def create_payment(data: Dict[str, Any]) -> Dict[str, Any]:
    booking = get_booking_by_id(data["booking_id"])
    if not booking:
        raise ValueError(f"Booking {data['booking_id']} not found.")

    payment_id = data.get("payment_id") or generate_id("P")
    amount = float(data["amount"])
    p_type = data["payment_type"]
    p_status = data.get("payment_status", "Success")
    tx_ref = data.get("transaction_reference") or f"TXN-{uuid.uuid4().hex[:8].upper()}"

    # Calculate 10% platform commission on rental revenue
    commission_rate = data.get("commission_rate", 0.10)
    if p_type == "Rental":
        commission = round(amount * commission_rate, 2)
        owner_earning = round(amount - commission, 2)
    else:
        commission = 0.0
        owner_earning = 0.0

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO PAYMENT (payment_id, booking_id, amount, payment_type, payment_status,
                                 transaction_reference, commission_amount, owner_earning)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payment_id, data["booking_id"], amount, p_type, p_status, tx_ref, commission, owner_earning),
        )

    # When rental payment succeeds, update vehicle to 'Booked'
    if p_type == "Rental" and p_status == "Success":
        update_vehicle_status(booking["vehicle_id"], "Booked")

    with get_db() as conn:
        return conn.execute("SELECT * FROM PAYMENT WHERE payment_id = ?", (payment_id,)).fetchone()


# ====================================================================
# INSPECTION SERVICES
# ====================================================================

def get_inspections_for_booking(booking_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        return conn.execute("SELECT * FROM INSPECTION WHERE booking_id = ? ORDER BY inspection_date ASC", (booking_id,)).fetchall()


def create_inspection(data: Dict[str, Any]) -> Dict[str, Any]:
    booking = get_booking_by_id(data["booking_id"])
    if not booking:
        raise ValueError(f"Booking {data['booking_id']} not found.")

    insp_id = data.get("inspection_id") or generate_id("I")
    insp_type = data["inspection_type"]

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO INSPECTION (inspection_id, booking_id, inspection_type, vehicle_condition, fuel_status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                insp_id,
                data["booking_id"],
                insp_type,
                data["vehicle_condition"],
                data.get("fuel_status", "Full"),
                data.get("notes"),
            ),
        )

    # When return inspection completes without unresolved issues, booking completes and vehicle becomes Available
    if insp_type == "Return":
        update_booking_status(data["booking_id"], "Completed")
        update_vehicle_status(booking["vehicle_id"], "Available")

    with get_db() as conn:
        return conn.execute("SELECT * FROM INSPECTION WHERE inspection_id = ?", (insp_id,)).fetchone()


# ====================================================================
# DAMAGE & PENALTY INCIDENT SERVICES
# ====================================================================

def get_incidents_for_booking(booking_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        return conn.execute("SELECT * FROM DAMAGE_PENALTY WHERE booking_id = ? ORDER BY reported_date DESC", (booking_id,)).fetchall()


def get_all_incidents() -> List[Dict[str, Any]]:
    with get_db() as conn:
        return conn.execute(
            """
            SELECT dp.*, b.tourist_id, b.vehicle_id, u.name AS tourist_name
            FROM DAMAGE_PENALTY dp
            JOIN BOOKING b ON dp.booking_id = b.booking_id
            JOIN USER u ON b.tourist_id = u.user_id
            ORDER BY dp.reported_date DESC
            """
        ).fetchall()


def create_incident(data: Dict[str, Any]) -> Dict[str, Any]:
    incident_id = data.get("incident_id") or generate_id("D")
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO DAMAGE_PENALTY (incident_id, booking_id, incident_type, description, amount, resolution_status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                incident_id,
                data["booking_id"],
                data["incident_type"],
                data["description"],
                float(data["amount"]),
                "Under review",
            ),
        )
        return conn.execute("SELECT * FROM DAMAGE_PENALTY WHERE incident_id = ?", (incident_id,)).fetchone()


def resolve_incident(incident_id: str, resolution_status: str) -> Dict[str, Any]:
    with get_db() as conn:
        conn.execute(
            "UPDATE DAMAGE_PENALTY SET resolution_status = ? WHERE incident_id = ?",
            (resolution_status, incident_id),
        )
        return conn.execute("SELECT * FROM DAMAGE_PENALTY WHERE incident_id = ?", (incident_id,)).fetchone()


# ====================================================================
# MAINTENANCE SERVICES
# ====================================================================

def get_maintenance_history(vehicle_id: Optional[str] = None) -> List[Dict[str, Any]]:
    query = """
        SELECT m.*, v.brand, v.model, v.vehicle_number
        FROM MAINTENANCE m
        JOIN VEHICLE v ON m.vehicle_id = v.vehicle_id
        WHERE 1=1
    """
    params = []
    if vehicle_id:
        query += " AND m.vehicle_id = ?"
        params.append(vehicle_id)
    query += " ORDER BY m.maintenance_date DESC"

    with get_db() as conn:
        return conn.execute(query, params).fetchall()


def create_maintenance_record(data: Dict[str, Any]) -> Dict[str, Any]:
    m_id = data.get("maintenance_id") or generate_id("M")
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO MAINTENANCE (maintenance_id, vehicle_id, maintenance_type, description, cost, status)
            VALUES (?, ?, ?, ?, ?, 'In Progress')
            """,
            (m_id, data["vehicle_id"], data["maintenance_type"], data["description"], float(data.get("cost", 0.0))),
        )
        conn.execute("UPDATE VEHICLE SET vehicle_status = 'Under Maintenance' WHERE vehicle_id = ?", (data["vehicle_id"],))
        return conn.execute("SELECT * FROM MAINTENANCE WHERE maintenance_id = ?", (m_id,)).fetchone()


def complete_maintenance_record(maintenance_id: str, cost: Optional[float] = None) -> Dict[str, Any]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM MAINTENANCE WHERE maintenance_id = ?", (maintenance_id,)).fetchone()
        if not row:
            raise ValueError(f"Maintenance record {maintenance_id} not found.")

        if cost is not None:
            conn.execute("UPDATE MAINTENANCE SET status = 'Completed', cost = ? WHERE maintenance_id = ?", (cost, maintenance_id))
        else:
            conn.execute("UPDATE MAINTENANCE SET status = 'Completed' WHERE maintenance_id = ?", (maintenance_id,))

        vehicle_id = row["vehicle_id"]
        # Check if any other in-progress maintenance exists for this vehicle
        active_records = conn.execute(
            "SELECT COUNT(*) as cnt FROM MAINTENANCE WHERE vehicle_id = ? AND status = 'In Progress'",
            (vehicle_id,),
        ).fetchone()

        if active_records["cnt"] == 0:
            conn.execute("UPDATE VEHICLE SET vehicle_status = 'Available' WHERE vehicle_id = ?", (vehicle_id,))

        return conn.execute("SELECT * FROM MAINTENANCE WHERE maintenance_id = ?", (maintenance_id,)).fetchone()
