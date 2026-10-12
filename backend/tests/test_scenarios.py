import pytest
from datetime import date
from app.database import init_database, get_db
from app.services import (
    get_user_by_id,
    create_user,
    update_user_verification,
    get_vehicle_by_id,
    create_vehicle,
    get_all_vehicles,
    create_booking_request,
    update_booking_status,
    get_booking_by_id,
    create_payment,
    get_payments_for_booking,
    create_inspection,
    get_inspections_for_booking,
    create_incident,
    resolve_incident,
    create_maintenance_record,
    complete_maintenance_record,
    check_booking_overlap,
)


@pytest.fixture(autouse=True)
def setup_clean_db():
    """Reset and re-seed database before each test run to ensure strict isolation."""
    init_database(seed=True)


# ====================================================================
# SCENARIO 9.1: Successful End-to-End Booking
# ====================================================================
def test_scenario_9_1_successful_end_to_end_booking():
    # 1. Aarav (U201) requests booking for scooter (V301) for 10-Sep to 13-Sep
    booking, warning = create_booking_request({
        "booking_id": "B101",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    assert booking["booking_status"] == "Pending"
    assert booking["rental_amount"] == 2000.0  # 4 days * 500

    # 2. Rakesh (owner) approves it
    updated_b = update_booking_status("B101", "Approved")
    assert updated_b["booking_status"] == "Approved"

    # 3. Aarav makes payment
    payment = create_payment({
        "payment_id": "P401",
        "booking_id": "B101",
        "amount": 2000.0,
        "payment_type": "Rental",
        "payment_status": "Success",
    })
    assert payment["payment_status"] == "Success"
    assert payment["commission_amount"] == 200.0   # 10%
    assert payment["owner_earning"] == 1800.0      # 90%
    assert get_vehicle_by_id("V301")["vehicle_status"] == "Booked"

    # 4. Pickup inspection
    pickup_insp = create_inspection({
        "inspection_id": "I501",
        "booking_id": "B101",
        "inspection_type": "Pickup",
        "vehicle_condition": "Good",
        "fuel_status": "Full",
    })
    assert pickup_insp["inspection_type"] == "Pickup"

    # 5. Return inspection
    return_insp = create_inspection({
        "inspection_id": "I502",
        "booking_id": "B101",
        "inspection_type": "Return",
        "vehicle_condition": "Good",
        "fuel_status": "Good",
    })
    assert return_insp["inspection_type"] == "Return"

    # Verification of final state
    final_b = get_booking_by_id("B101")
    assert final_b["booking_status"] == "Completed"
    assert get_vehicle_by_id("V301")["vehicle_status"] == "Available"


# ====================================================================
# SCENARIO 9.2: Owner Rejects a Booking Request
# ====================================================================
def test_scenario_9_2_owner_rejects_booking():
    booking, warning = create_booking_request({
        "booking_id": "B102",
        "tourist_id": "U205",
        "vehicle_id": "V301",
        "start_date": "2026-09-15",
        "end_date": "2026-09-17",
    })
    assert booking["booking_status"] == "Pending"

    # Owner rejects the request
    rejected_b = update_booking_status("B102", "Rejected", cancellation_reason="Owner declined")
    assert rejected_b["booking_status"] == "Rejected"
    assert rejected_b["cancellation_reason"] == "Owner declined"

    # No payment rows exist
    payments = get_payments_for_booking("B102")
    assert len(payments) == 0

    # Vehicle remains Available
    assert get_vehicle_by_id("V301")["vehicle_status"] == "Available"


# ====================================================================
# SCENARIO 9.3: Preventing an Overlapping Booking
# ====================================================================
def test_scenario_9_3_prevent_overlapping_booking():
    # 1. First tourist books V301 for 10-Sep to 13-Sep and gets Approved
    b1, _ = create_booking_request({
        "booking_id": "B110",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    update_booking_status("B110", "Approved")

    # 2. Second tourist requests V301 for overlapping dates (12-Sep to 15-Sep)
    b2, warning = create_booking_request({
        "booking_id": "B111",
        "tourist_id": "U205",
        "vehicle_id": "V301",
        "start_date": "2026-09-12",
        "end_date": "2026-09-15",
    })
    # Must be automatically rejected due to overlap
    assert b2["booking_status"] == "Rejected"
    assert "overlap" in b2["cancellation_reason"].lower()


# ====================================================================
# SCENARIO 9.4: Damage Reported After Return
# ====================================================================
def test_scenario_9_4_damage_reported_after_return():
    b, _ = create_booking_request({
        "booking_id": "B101",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    update_booking_status("B101", "Approved")

    # Return inspection notes damage
    create_inspection({
        "inspection_id": "I502",
        "booking_id": "B101",
        "inspection_type": "Return",
        "vehicle_condition": "Damaged - cracked mirror",
        "fuel_status": "Full",
    })

    # Owner logs damage penalty incident
    incident = create_incident({
        "incident_id": "D601",
        "booking_id": "B101",
        "incident_type": "Damage",
        "description": "Cracked right rear-view mirror",
        "amount": 500.0,
    })
    assert incident["resolution_status"] == "Under review"
    assert incident["amount"] == 500.0


# ====================================================================
# SCENARIO 9.5: Vehicle Blocked While Under Maintenance
# ====================================================================
def test_scenario_9_5_vehicle_blocked_under_maintenance():
    # 1. Put V301 under maintenance
    maint = create_maintenance_record({
        "maintenance_id": "M701",
        "vehicle_id": "V301",
        "maintenance_type": "Brake repair",
        "description": "Front disc brake pads worn out",
        "cost": 850.0,
    })
    assert maint["status"] == "In Progress"
    assert get_vehicle_by_id("V301")["vehicle_status"] == "Under Maintenance"

    # 2. Attempting to book V301 must raise error
    with pytest.raises(ValueError, match="under maintenance"):
        create_booking_request({
            "booking_id": "B199",
            "tourist_id": "U201",
            "vehicle_id": "V301",
            "start_date": "2026-09-20",
            "end_date": "2026-09-22",
        })

    # 3. Complete maintenance
    complete_maintenance_record("M701", cost=900.0)
    assert get_vehicle_by_id("V301")["vehicle_status"] == "Available"


# ====================================================================
# SCENARIO 9.6: Tourist Cancels a Booking Before Pickup
# ====================================================================
def test_scenario_9_6_tourist_cancels_before_pickup():
    b, _ = create_booking_request({
        "booking_id": "B120",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    update_booking_status("B120", "Approved")
    create_payment({
        "payment_id": "P414",
        "booking_id": "B120",
        "amount": 2000.0,
        "payment_type": "Rental",
    })

    # Tourist cancels
    cancelled = update_booking_status("B120", "Cancelled", cancellation_reason="Change of travel plan")
    assert cancelled["booking_status"] == "Cancelled"

    # Issue refund payment
    refund = create_payment({
        "payment_id": "P415",
        "booking_id": "B120",
        "amount": 1800.0,
        "payment_type": "Refund",
        "payment_status": "Success",
    })
    assert refund["payment_type"] == "Refund"
    assert get_vehicle_by_id("V301")["vehicle_status"] == "Available"


# ====================================================================
# SCENARIO 9.7: Late Return Penalty
# ====================================================================
def test_scenario_9_7_late_return_penalty():
    b, _ = create_booking_request({
        "booking_id": "B101",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    update_booking_status("B101", "Approved")

    incident = create_incident({
        "incident_id": "D610",
        "booking_id": "B101",
        "incident_type": "Late Return",
        "description": "Vehicle returned 6 hours past cutoff time",
        "amount": 150.0,
    })
    assert incident["incident_type"] == "Late Return"
    assert incident["amount"] == 150.0

    resolved = resolve_incident("D610", "Resolved")
    assert resolved["resolution_status"] == "Resolved"


# ====================================================================
# SCENARIO 9.8: One Tourist, Multiple Bookings
# ====================================================================
def test_scenario_9_8_one_tourist_multiple_bookings():
    b1, _ = create_booking_request({
        "booking_id": "B130",
        "tourist_id": "U201",
        "vehicle_id": "V301",  # Manali
        "start_date": "2026-09-10",
        "end_date": "2026-09-12",
    })
    b2, _ = create_booking_request({
        "booking_id": "B131",
        "tourist_id": "U201",
        "vehicle_id": "V355",  # Shimla
        "start_date": "2026-09-15",
        "end_date": "2026-09-17",
    })
    assert b1["tourist_id"] == "U201"
    assert b2["tourist_id"] == "U201"
    assert b1["vehicle_id"] != b2["vehicle_id"]


# ====================================================================
# SCENARIO 9.9: One Owner, Multiple Vehicles
# ====================================================================
def test_scenario_9_9_one_owner_multiple_vehicles():
    # Rakesh (U150) owns V301, V302, V303
    v1 = get_vehicle_by_id("V301")
    v2 = get_vehicle_by_id("V302")
    v3 = get_vehicle_by_id("V303")
    assert v1["owner_id"] == "U150"
    assert v2["owner_id"] == "U150"
    assert v3["owner_id"] == "U150"
    assert len({v1["vehicle_id"], v2["vehicle_id"], v3["vehicle_id"]}) == 3


# ====================================================================
# SCENARIO 9.10: Administrator Verifies a New User
# ====================================================================
def test_scenario_9_10_admin_verifies_new_user():
    # Suresh (U152) starts with Pending & Inactive
    suresh = get_user_by_id("U152")
    assert suresh["verification_status"] == "Pending"
    assert suresh["account_status"] == "Inactive"

    # Suresh cannot list a vehicle yet
    with pytest.raises(ValueError, match="must be verified and active"):
        create_vehicle({
            "vehicle_id": "V999",
            "owner_id": "U152",
            "location_id": "L01",
            "vehicle_number": "HP-01-XX-9999",
            "vehicle_type": "Scooter",
            "brand": "Hero",
            "model": "Pleasure",
            "year": 2021,
            "rental_rate_per_day": 400.0,
            "security_deposit": 1000.0,
        })

    # Admin verifies Suresh
    verified_user = update_user_verification("U152", "Verified", "Active")
    assert verified_user["verification_status"] == "Verified"
    assert verified_user["account_status"] == "Active"

    # Now Suresh can list a vehicle
    new_veh = create_vehicle({
        "vehicle_id": "V999",
        "owner_id": "U152",
        "location_id": "L01",
        "vehicle_number": "HP-01-XX-9999",
        "vehicle_type": "Scooter",
        "brand": "Hero",
        "model": "Pleasure",
        "year": 2021,
        "rental_rate_per_day": 400.0,
        "security_deposit": 1000.0,
    })
    assert new_veh["vehicle_id"] == "V999"


# ====================================================================
# SCENARIO 9.11: Administrator Resolves a Disputed Incident
# ====================================================================
def test_scenario_9_11_admin_resolves_dispute():
    b, _ = create_booking_request({
        "booking_id": "B101",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    incident = create_incident({
        "incident_id": "D601",
        "booking_id": "B101",
        "incident_type": "Damage",
        "description": "Pre-existing scratches disputed by tourist",
        "amount": 500.0,
    })
    assert incident["resolution_status"] == "Under review"

    # Admin decides damage was pre-existing -> Waived
    resolved = resolve_incident("D601", "Waived")
    assert resolved["resolution_status"] == "Waived"


# ====================================================================
# SCENARIO 9.12: Fuel Handover - No Odometer Tracking
# ====================================================================
def test_scenario_9_12_fuel_handover_no_odometer():
    b, _ = create_booking_request({
        "booking_id": "B101",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    insp = create_inspection({
        "inspection_id": "I501",
        "booking_id": "B101",
        "inspection_type": "Pickup",
        "vehicle_condition": "Good",
        "fuel_status": "Full",
        "notes": "Handed over with full tank. Renter pays fuel onwards.",
    })
    # Confirms fuel_status is stored for reference only without odometer column
    assert insp["fuel_status"] == "Full"
    payments = get_payments_for_booking("B101")
    # Confirms payments table has no fuel charges
    for p in payments:
        assert p["payment_type"] != "Fuel"
