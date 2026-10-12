import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database(seed=True)


def test_api_root_and_health():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Operational"
    assert "USER" in data["entities"]

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"


def test_api_users_and_auth():
    # List users
    res = client.get("/api/users")
    assert res.status_code == 200
    assert len(res.json()) >= 6

    # Login Aarav
    login_res = client.post("/api/users/login", json={"email": "aarav.tourist@example.com", "password": "aarav123"})
    assert login_res.status_code == 200
    assert login_res.json()["name"] == "Aarav Mehta"


def test_api_vehicles_and_locations():
    # List locations
    loc_res = client.get("/api/locations")
    assert loc_res.status_code == 200
    assert len(loc_res.json()) >= 3

    # List vehicles in Manali
    veh_res = client.get("/api/vehicles?city=Manali")
    assert veh_res.status_code == 200
    assert len(veh_res.json()) >= 3


def test_api_booking_and_payment_flow():
    # 1. Request booking
    booking_res = client.post("/api/bookings", json={
        "booking_id": "B_API_01",
        "tourist_id": "U201",
        "vehicle_id": "V301",
        "start_date": "2026-10-10",
        "end_date": "2026-10-12",
    })
    assert booking_res.status_code == 201
    assert booking_res.json()["booking_status"] == "Pending"

    # 2. Owner approves
    appr_res = client.post("/api/bookings/B_API_01/decision", json={"booking_status": "Approved"})
    assert appr_res.status_code == 200
    assert appr_res.json()["booking_status"] == "Approved"

    # 3. Tourist pays
    pay_res = client.post("/api/payments", json={
        "booking_id": "B_API_01",
        "amount": 1500.0,
        "payment_type": "Rental",
        "payment_status": "Success",
    })
    assert pay_res.status_code == 201
    assert pay_res.json()["commission_amount"] == 150.0
    assert pay_res.json()["owner_earning"] == 1350.0

    # 4. Pickup Inspection
    pickup_res = client.post("/api/inspections", json={
        "booking_id": "B_API_01",
        "inspection_type": "Pickup",
        "vehicle_condition": "Good",
        "fuel_status": "Full",
    })
    assert pickup_res.status_code == 201

    # 5. Return Inspection
    return_res = client.post("/api/inspections", json={
        "booking_id": "B_API_01",
        "inspection_type": "Return",
        "vehicle_condition": "Good",
        "fuel_status": "Full",
    })
    assert return_res.status_code == 201

    # Booking must now be Completed
    get_b = client.get("/api/bookings/B_API_01")
    assert get_b.json()["booking_status"] == "Completed"
