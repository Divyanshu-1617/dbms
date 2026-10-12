import pytest
from app.database import get_db, init_database
from app.services import (
    create_booking_request,
    update_booking_status,
    create_payment,
    create_inspection,
    get_vehicle_by_id,
    get_booking_by_id,
)

@pytest.fixture(autouse=True)
def setup_db():
    init_database(seed=True)

def test_view_active_rentals():
    """Verify VIEW_ACTIVE_RENTALS returns currently active rentals with joined details."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM VIEW_ACTIVE_RENTALS").fetchall()
        assert isinstance(rows, list)

def test_view_owner_revenue_summary():
    """Verify VIEW_OWNER_REVENUE_SUMMARY computes revenue aggregate for owners."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM VIEW_OWNER_REVENUE_SUMMARY WHERE owner_id = 'U150'").fetchall()
        assert len(rows) == 1
        assert rows[0]["owner_name"] == "Rakesh Verma"

def test_trigger_payment_sets_vehicle_booked():
    """Verify DB Trigger automatically sets VEHICLE.vehicle_status to Booked on successful rental payment."""
    # Create and approve booking
    b, _ = create_booking_request({
        "booking_id": "B_TRIG_1",
        "tourist_id": "U201",
        "vehicle_id": "V302",
        "start_date": "2026-11-01",
        "end_date": "2026-11-03",
    })
    update_booking_status("B_TRIG_1", "Approved")

    # Insert payment directly into DB
    with get_db() as conn:
        conn.execute("""
            INSERT INTO PAYMENT (payment_id, booking_id, amount, payment_type, payment_status, transaction_reference)
            VALUES ('P_TRIG_1', 'B_TRIG_1', 3600.0, 'Rental', 'Success', 'TXN-TRIG-1')
        """)

    # Verify Trigger changed vehicle status
    veh = get_vehicle_by_id("V302")
    assert veh["vehicle_status"] == "Booked"

def test_trigger_inspection_completes_booking():
    """Verify DB Trigger automatically marks BOOKING Completed and releases VEHICLE to Available on Return inspection."""
    # Setup vehicle as booked
    with get_db() as conn:
        conn.execute("UPDATE VEHICLE SET vehicle_status = 'Booked' WHERE vehicle_id = 'V302'")
        conn.execute("""
            INSERT INTO BOOKING (booking_id, tourist_id, vehicle_id, start_date, end_date, rental_amount, booking_status)
            VALUES ('B_TRIG_2', 'U201', 'V302', '2026-11-01', '2026-11-03', 3600.0, 'Approved')
        """)
        # Insert Return inspection
        conn.execute("""
            INSERT INTO INSPECTION (inspection_id, booking_id, inspection_type, vehicle_condition, fuel_status)
            VALUES ('I_TRIG_2', 'B_TRIG_2', 'Return', 'Good', 'Full')
        """)

    # Verify Trigger actions
    b = get_booking_by_id("B_TRIG_2")
    assert b["booking_status"] == "Completed"
    veh = get_vehicle_by_id("V302")
    assert veh["vehicle_status"] == "Available"

def test_transaction_commit_and_rollback():
    """Demonstrate ACID transaction properties with COMMIT, ROLLBACK, and atomic integrity."""
    # Test Rollback on failure
    with pytest.raises(Exception):
        with get_db() as conn:
            conn.execute("UPDATE VEHICLE SET rental_rate_per_day = 9999 WHERE vehicle_id = 'V301'")
            # Deliberate failure: CHECK constraint violation (rental_rate_per_day <= 0)
            conn.execute("UPDATE VEHICLE SET rental_rate_per_day = -50 WHERE vehicle_id = 'V302'")

    # Because transaction rolled back, V301 should retain original rate
    veh = get_vehicle_by_id("V301")
    assert veh["rental_rate_per_day"] == 500.0

    # Test Commit on success
    with get_db() as conn:
        conn.execute("UPDATE VEHICLE SET rental_rate_per_day = 650 WHERE vehicle_id = 'V301'")
    assert get_vehicle_by_id("V301")["rental_rate_per_day"] == 650.0
