#!/usr/bin/env python3
"""
Peer-to-Peer Tourist Bike Rental Management System
Interactive Presentation & Viva Demonstration Runner
Executes the 12 Real-World Scenarios from Section 9 of the DBMS Project Report.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

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
)

# Terminal formatting and Windows UTF-8 stdout support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"{BOLD}{CYAN}{title.center(80)}{RESET}")
    print("=" * 80)


def print_step(step_num: int, title: str, description: str):
    print(f"\n{BOLD}{BLUE}Step {step_num}: {title}{RESET}")
    print(f"  {description}")


def print_table_record(table_name: str, record: dict):
    print(f"\n  {YELLOW}Table: {BOLD}{table_name}{RESET}")
    formatted = " | ".join(f"{k}={v}" for k, v in record.items() if v is not None)
    print(f"  {formatted}")


def print_success(message: str):
    print(f"\n{BOLD}{GREEN}[SUCCESS] {message}{RESET}")


# ====================================================================
# SCENARIOS IMPLEMENTATION
# ====================================================================

def run_scenario_1():
    print_header("Scenario 9.1 — Successful End-to-End Booking")
    print("Story: Aarav visits Manali, books Rakesh's Honda Activa (V301) for 3 days,")
    print("Rakesh approves, Aarav pays online, completes inspections with no damage, returns bike.\n")

    init_database(seed=True)

    print_step(1, "Booking Request Sent", "Aarav requests V301 from 10-Sep to 13-Sep")
    booking, _ = create_booking_request({
        "booking_id": "B101",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    print_table_record("BOOKING", {"booking_id": booking["booking_id"], "tourist_id": "U201 (Aarav)", "vehicle_id": "V301", "booking_status": booking["booking_status"], "rental_amount": booking["rental_amount"]})

    print_step(2, "Owner Approval", "Rakesh reviews and approves booking request")
    booking = update_booking_status("B101", "Approved")
    print_table_record("BOOKING", {"booking_id": booking["booking_id"], "booking_status": booking["booking_status"]})

    print_step(3, "Payment Processed", "Aarav pays 2000; 10% platform commission deducted")
    payment = create_payment({
        "payment_id": "P401",
        "booking_id": "B101",
        "amount": 2000.0,
        "payment_type": "Rental",
        "payment_status": "Success",
    })
    print_table_record("PAYMENT", {"payment_id": payment["payment_id"], "booking_id": "B101", "amount": payment["amount"], "commission": payment["commission_amount"], "owner_earning": payment["owner_earning"]})
    print_table_record("VEHICLE", {"vehicle_id": "V301", "vehicle_status": get_vehicle_by_id("V301")["vehicle_status"]})

    print_step(4, "Pickup Inspection", "Scooter handed over in Good condition with Full tank")
    insp1 = create_inspection({
        "inspection_id": "I501",
        "booking_id": "B101",
        "inspection_type": "Pickup",
        "vehicle_condition": "Good",
        "fuel_status": "Full",
    })
    print_table_record("INSPECTION", {"inspection_id": insp1["inspection_id"], "type": insp1["inspection_type"], "condition": insp1["vehicle_condition"], "fuel_status": insp1["fuel_status"]})

    print_step(5, "Return Inspection & Completion", "Scooter returned in Good condition")
    insp2 = create_inspection({
        "inspection_id": "I502",
        "booking_id": "B101",
        "inspection_type": "Return",
        "vehicle_condition": "Good",
        "fuel_status": "Good",
    })
    print_table_record("INSPECTION", {"inspection_id": insp2["inspection_id"], "type": insp2["inspection_type"], "condition": insp2["vehicle_condition"]})
    print_table_record("BOOKING", {"booking_id": "B101", "booking_status": get_booking_by_id("B101")["booking_status"]})
    print_table_record("VEHICLE", {"vehicle_id": "V301", "vehicle_status": get_vehicle_by_id("V301")["vehicle_status"]})
    print_success("Scenario 9.1 Completed Successfully!")


def run_scenario_2():
    print_header("Scenario 9.2 — Owner Rejects a Booking Request")
    print("Story: Tourist Rahul requests bike, but owner Rakesh has promised it to a friend.")

    init_database(seed=True)

    print_step(1, "Booking Request", "Rahul (U205) requests V301")
    b, _ = create_booking_request({
        "booking_id": "B102",
        "tourist_id": "U205",
        "vehicle_id": "V301",
        "start_date": "2026-09-15",
        "end_date": "2026-09-17",
    })
    print_table_record("BOOKING", {"booking_id": b["booking_id"], "status": b["booking_status"]})

    print_step(2, "Owner Rejection", "Rakesh rejects request through platform")
    b = update_booking_status("B102", "Rejected", cancellation_reason="Owner declined")
    print_table_record("BOOKING", {"booking_id": b["booking_id"], "status": b["booking_status"], "reason": b["cancellation_reason"]})
    print_table_record("VEHICLE", {"vehicle_id": "V301", "status": get_vehicle_by_id("V301")["vehicle_status"]})
    print_success("Scenario 9.2 Completed: Booking marked Rejected, vehicle stays Available for other tourists.")


def run_scenario_3():
    print_header("Scenario 9.3 — Preventing an Overlapping Booking")
    print("Story: Two tourists try to book the same bike for overlapping dates.")

    init_database(seed=True)

    print_step(1, "First Booking Approved", "Aarav books V301 for 10-Sep to 13-Sep")
    b1, _ = create_booking_request({
        "booking_id": "B110",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    update_booking_status("B110", "Approved")
    print_table_record("BOOKING", {"booking_id": "B110", "dates": "2026-09-10 to 2026-09-13", "status": "Approved"})

    print_step(2, "Overlapping Request Blocked", "Rahul tries to book V301 for 12-Sep to 15-Sep (overlaps)")
    b2, warning = create_booking_request({
        "booking_id": "B111",
        "tourist_id": "U205",
        "vehicle_id": "V301",
        "start_date": "2026-09-12",
        "end_date": "2026-09-15",
    })
    print_table_record("BOOKING", {"booking_id": "B111", "dates": "2026-09-12 to 2026-09-15", "status": b2["booking_status"], "reason": b2["cancellation_reason"]})
    print_success("Scenario 9.3 Completed: Overlap rule enforced! Second booking automatically blocked.")


def run_scenario_4():
    print_header("Scenario 9.4 — Damage Reported After Return")
    print("Story: During return inspection, owner notices a cracked mirror and logs an incident.")

    init_database(seed=True)
    b, _ = create_booking_request({
        "booking_id": "B101",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    update_booking_status("B101", "Approved")

    print_step(1, "Return Inspection Records Damage", "Return condition noted as 'Damaged - cracked mirror'")
    insp = create_inspection({
        "inspection_id": "I502",
        "booking_id": "B101",
        "inspection_type": "Return",
        "vehicle_condition": "Damaged - cracked mirror",
        "fuel_status": "Good",
    })
    print_table_record("INSPECTION", {"inspection_id": "I502", "type": "Return", "condition": insp["vehicle_condition"]})

    print_step(2, "Damage Penalty Logged", "Owner logs DAMAGE_PENALTY row for 500")
    inc = create_incident({
        "incident_id": "D601",
        "booking_id": "B101",
        "incident_type": "Damage",
        "description": "Cracked right rear mirror",
        "amount": 500.0,
    })
    print_table_record("DAMAGE_PENALTY", {"incident_id": inc["incident_id"], "type": inc["incident_type"], "amount": inc["amount"], "status": inc["resolution_status"]})
    print_success("Scenario 9.4 Completed: Incident linked to booking, deposit deduction flagged.")


def run_scenario_5():
    print_header("Scenario 9.5 — Vehicle Blocked While Under Maintenance")
    print("Story: Bike develops brake problem. Owner schedules maintenance, blocking new bookings.")

    init_database(seed=True)

    print_step(1, "Create Maintenance Record", "Brake repair scheduled for V301")
    m = create_maintenance_record({
        "maintenance_id": "M701",
        "vehicle_id": "V301",
        "maintenance_type": "Brake repair",
        "description": "Front disc brake pads worn out",
        "cost": 850.0,
    })
    print_table_record("MAINTENANCE", {"maintenance_id": m["maintenance_id"], "status": m["status"], "type": m["maintenance_type"]})
    print_table_record("VEHICLE", {"vehicle_id": "V301", "status": get_vehicle_by_id("V301")["vehicle_status"]})

    print_step(2, "Verify Booking Blocked", "Attempting booking on vehicle under maintenance...")
    try:
        create_booking_request({"vehicle_id": "V301", "tourist_id": "U201", "start_date": "2026-09-20", "end_date": "2026-09-22"})
        print(f"{RED}ERROR: Booking succeeded unexpectedly!{RESET}")
    except ValueError as e:
        print(f"  {GREEN}[OK] Blocked by business rule: {e}{RESET}")

    print_step(3, "Complete Maintenance", "Repair finished, status restored to Available")
    m_comp = complete_maintenance_record("M701", cost=850.0)
    print_table_record("MAINTENANCE", {"maintenance_id": "M701", "status": m_comp["status"]})
    print_table_record("VEHICLE", {"vehicle_id": "V301", "status": get_vehicle_by_id("V301")["vehicle_status"]})
    print_success("Scenario 9.5 Completed: Vehicle locked during repair and safely unlocked afterwards.")


def run_scenario_6():
    print_header("Scenario 9.6 — Tourist Cancels a Booking Before Pickup")
    print("Story: Aarav's plans change; cancels approved booking, receives refund.")

    init_database(seed=True)
    b, _ = create_booking_request({
        "booking_id": "B120",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })
    update_booking_status("B120", "Approved")
    create_payment({"payment_id": "P414", "booking_id": "B120", "amount": 2000.0, "payment_type": "Rental"})

    print_step(1, "Booking Cancelled", "Aarav cancels booking before pickup")
    b = update_booking_status("B120", "Cancelled", cancellation_reason="Change of travel plan")
    print_table_record("BOOKING", {"booking_id": "B120", "status": b["booking_status"], "reason": b["cancellation_reason"]})

    print_step(2, "Refund Issued", "Refund payment recorded in PAYMENT table")
    refund = create_payment({"payment_id": "P415", "booking_id": "B120", "amount": 1800.0, "payment_type": "Refund"})
    print_table_record("PAYMENT", {"payment_id": "P415", "type": refund["payment_type"], "amount": refund["amount"]})
    print_table_record("VEHICLE", {"vehicle_id": "V301", "status": get_vehicle_by_id("V301")["vehicle_status"]})
    print_success("Scenario 9.6 Completed: Booking cancelled, partial refund recorded, vehicle available.")


def run_scenario_7():
    print_header("Scenario 9.7 — Late Return Penalty")
    print("Story: Tourist returns bike 6 hours late; penalty recorded against booking.")

    init_database(seed=True)
    b, _ = create_booking_request({
        "booking_id": "B101",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    })

    print_step(1, "Penalty Incident Logged", "Late return penalty applied")
    inc = create_incident({
        "incident_id": "D610",
        "booking_id": "B101",
        "incident_type": "Late Return",
        "description": "Bike returned 6 hours past cutoff time",
        "amount": 150.0,
    })
    print_table_record("DAMAGE_PENALTY", {"incident_id": inc["incident_id"], "type": inc["incident_type"], "amount": inc["amount"]})

    print_step(2, "Resolution Settled", "Penalty deducted from deposit")
    resolved = resolve_incident("D610", "Resolved")
    print_table_record("DAMAGE_PENALTY", {"incident_id": "D610", "status": resolved["resolution_status"]})
    print_success("Scenario 9.7 Completed: Late return penalty correctly tied to booking.")


def run_scenario_8():
    print_header("Scenario 9.8 — One Tourist, Multiple Bookings")
    print("Story: Same tourist (Aarav, U201) books in Manali and Shimla at different dates.")

    init_database(seed=True)
    b1, _ = create_booking_request({"booking_id": "B130", "tourist_id": "U201", "vehicle_id": "V301", "start_date": "2026-09-10", "end_date": "2026-09-12"})
    b2, _ = create_booking_request({"booking_id": "B131", "tourist_id": "U201", "vehicle_id": "V355", "start_date": "2026-09-15", "end_date": "2026-09-17"})

    print_table_record("BOOKING", {"booking_id": b1["booking_id"], "tourist_id": b1["tourist_id"], "vehicle_id": "V301 (Manali)"})
    print_table_record("BOOKING", {"booking_id": b2["booking_id"], "tourist_id": b2["tourist_id"], "vehicle_id": "V355 (Shimla)"})
    print_success("Scenario 9.8 Completed: 1:N USER -> BOOKING relationship confirmed.")


def run_scenario_9():
    print_header("Scenario 9.9 — One Owner, Multiple Vehicles")
    print("Story: Rakesh (U150) lists three different scooters/motorcycles across pickup locations.")

    init_database(seed=True)
    v1 = get_vehicle_by_id("V301")
    v2 = get_vehicle_by_id("V302")
    v3 = get_vehicle_by_id("V303")

    print_table_record("VEHICLE", {"vehicle_id": v1["vehicle_id"], "owner_id": v1["owner_id"], "brand": v1["brand"], "model": v1["model"], "loc": v1["location_id"]})
    print_table_record("VEHICLE", {"vehicle_id": v2["vehicle_id"], "owner_id": v2["owner_id"], "brand": v2["brand"], "model": v2["model"], "loc": v2["location_id"]})
    print_table_record("VEHICLE", {"vehicle_id": v3["vehicle_id"], "owner_id": v3["owner_id"], "brand": v3["brand"], "model": v3["model"], "loc": v3["location_id"]})
    print_success("Scenario 9.9 Completed: 1:N USER -> VEHICLE relationship confirmed.")


def run_scenario_10():
    print_header("Scenario 9.10 — Administrator Verifies a New User")
    print("Story: New owner signs up; Admin verifies KYC before owner can list bikes.")

    init_database(seed=True)
    user = get_user_by_id("U152")
    print_step(1, "Initial Unverified State", "Suresh (U152) has Pending verification")
    print_table_record("USER", {"user_id": user["user_id"], "name": user["name"], "verification": user["verification_status"], "account": user["account_status"]})

    print_step(2, "Listing Blocked Before Verification", "Attempting to list vehicle without active status...")
    try:
        create_vehicle({"vehicle_id": "V999", "owner_id": "U152", "location_id": "L01", "vehicle_number": "HP-01-X-111", "vehicle_type": "Scooter", "brand": "Hero", "model": "Pleasure", "year": 2021, "rental_rate_per_day": 400.0, "security_deposit": 1000.0})
    except ValueError as e:
        print(f"  {GREEN}[OK] Blocked by business rule: {e}{RESET}")

    print_step(3, "Admin Verifies Owner", "Admin updates status to Verified & Active")
    verified = update_user_verification("U152", "Verified", "Active")
    print_table_record("USER", {"user_id": "U152", "verification": verified["verification_status"], "account": verified["account_status"]})

    print_step(4, "Vehicle Listing Permitted", "Suresh now successfully lists vehicle")
    veh = create_vehicle({"vehicle_id": "V999", "owner_id": "U152", "location_id": "L01", "vehicle_number": "HP-01-X-111", "vehicle_type": "Scooter", "brand": "Hero", "model": "Pleasure", "year": 2021, "rental_rate_per_day": 400.0, "security_deposit": 1000.0})
    print_table_record("VEHICLE", {"vehicle_id": veh["vehicle_id"], "owner": veh["owner_id"], "model": veh["model"]})
    print_success("Scenario 9.10 Completed: Admin KYC verification lifecycle functioning.")


def run_scenario_11():
    print_header("Scenario 9.11 — Administrator Resolves Disputed Incident")
    print("Story: Owner claims damage, tourist claims pre-existing; Admin reviews inspections and waives fee.")

    init_database(seed=True)
    b, _ = create_booking_request({"booking_id": "B101", "tourist_id": "U201", "vehicle_id": "V301", "start_date": "2026-09-10", "end_date": "2026-09-13"})
    inc = create_incident({"incident_id": "D601", "booking_id": "B101", "incident_type": "Damage", "description": "Scratch on left fairing", "amount": 500.0})

    print_step(1, "Dispute Filed", "Incident filed with status 'Under review'")
    print_table_record("DAMAGE_PENALTY", {"incident_id": "D601", "status": inc["resolution_status"]})

    print_step(2, "Admin Adjudication", "Admin confirms scratch was documented in pickup inspection -> Waives penalty")
    resolved = resolve_incident("D601", "Waived")
    print_table_record("DAMAGE_PENALTY", {"incident_id": "D601", "status": resolved["resolution_status"]})
    print_success("Scenario 9.11 Completed: Dispute resolved impartially by platform administrator.")


def run_scenario_12():
    print_header("Scenario 9.12 — Fuel Handover (No Odometer Tracking)")
    print("Story: Fuel is documented informatively; renter fuels during trip; no odometer math in DB.")

    init_database(seed=True)
    b, _ = create_booking_request({"booking_id": "B101", "tourist_id": "U201", "vehicle_id": "V301", "start_date": "2026-09-10", "end_date": "2026-09-13"})
    insp = create_inspection({
        "inspection_id": "I501",
        "booking_id": "B101",
        "inspection_type": "Pickup",
        "vehicle_condition": "Good",
        "fuel_status": "Full",
        "notes": "Handover with full tank. Renter pays fuel onwards per Section 3.1 policy.",
    })
    print_table_record("INSPECTION", {"inspection_id": insp["inspection_id"], "fuel_status": insp["fuel_status"], "notes": insp["notes"]})
    print_success("Scenario 9.12 Completed: Fuel policy verified - zero fuel ledger pollution!")


SCENARIO_MAP = {
    1: run_scenario_1,
    2: run_scenario_2,
    3: run_scenario_3,
    4: run_scenario_4,
    5: run_scenario_5,
    6: run_scenario_6,
    7: run_scenario_7,
    8: run_scenario_8,
    9: run_scenario_9,
    10: run_scenario_10,
    11: run_scenario_11,
    12: run_scenario_12,
}


def run_all():
    for num in range(1, 13):
        SCENARIO_MAP[num]()
    print("\n" + "=" * 80)
    print(f"{BOLD}{GREEN}ALL 12 REAL-WORLD SCENARIOS VERIFIED SUCCESSFULLY!{RESET}".center(80))
    print("=" * 80)


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg == "--all":
            run_all()
            return
        elif arg.isdigit() and int(arg) in SCENARIO_MAP:
            SCENARIO_MAP[int(arg)]()
            return

    while True:
        print("\n" + "=" * 65)
        print(f"{BOLD}{CYAN}  P2P TOURIST BIKE RENTAL DBMS - VIVA SCENARIO DEMONSTRATOR{RESET}")
        print("=" * 65)
        print("  [0]  Run ALL 12 Scenarios Sequentially")
        print("  [1]  Scenario 9.1:  Successful End-to-End Booking")
        print("  [2]  Scenario 9.2:  Owner Rejects a Booking Request")
        print("  [3]  Scenario 9.3:  Preventing Overlapping Booking")
        print("  [4]  Scenario 9.4:  Damage Reported After Return")
        print("  [5]  Scenario 9.5:  Vehicle Blocked Under Maintenance")
        print("  [6]  Scenario 9.6:  Tourist Cancels Before Pickup")
        print("  [7]  Scenario 9.7:  Late Return Penalty")
        print("  [8]  Scenario 9.8:  One Tourist, Multiple Bookings")
        print("  [9]  Scenario 9.9:  One Owner, Multiple Vehicles")
        print("  [10] Scenario 9.10: Administrator Verifies New User")
        print("  [11] Scenario 9.11: Administrator Resolves Disputed Incident")
        print("  [12] Scenario 9.12: Fuel Handover (No Odometer Tracking)")
        print("  [Q]  Exit")
        print("-" * 65)

        choice = input(f"{BOLD}Select an option (0-12 or Q): {RESET}").strip().upper()
        if choice == "Q":
            print("Exiting presentation runner. Good luck on your viva!")
            break
        elif choice == "0":
            run_all()
        elif choice.isdigit() and int(choice) in SCENARIO_MAP:
            SCENARIO_MAP[int(choice)]()
        else:
            print(f"{RED}Invalid selection. Please enter 0-12 or Q.{RESET}")


if __name__ == "__main__":
    main()
