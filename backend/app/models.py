from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import date, datetime


# ==========================================
# USER MODELS
# ==========================================
class UserBase(BaseModel):
    name: str
    email: str
    phone: str
    role: Literal["Tourist", "Owner", "Admin"]


class UserCreate(UserBase):
    user_id: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(UserBase):
    user_id: str
    verification_status: Literal["Pending", "Verified", "Rejected"]
    account_status: Literal["Active", "Inactive", "Suspended"]
    created_at: Optional[str] = None


class UserVerifyRequest(BaseModel):
    verification_status: Literal["Verified", "Rejected"]
    account_status: Literal["Active", "Inactive", "Suspended"] = "Active"


# ==========================================
# LOCATION MODELS
# ==========================================
class LocationCreate(BaseModel):
    location_id: Optional[str] = None
    address: str
    city: str
    state: str
    pincode: str
    pickup_instructions: Optional[str] = None


class LocationResponse(LocationCreate):
    location_id: str


# ==========================================
# VEHICLE MODELS
# ==========================================
class VehicleCreate(BaseModel):
    vehicle_id: Optional[str] = None
    owner_id: str
    location_id: str
    vehicle_number: str
    vehicle_type: str
    brand: str
    model: str
    year: int
    rental_rate_per_day: float
    security_deposit: float
    vehicle_status: Literal["Available", "Booked", "Under Maintenance", "Inactive"] = "Available"


class VehicleStatusUpdate(BaseModel):
    vehicle_status: Literal["Available", "Booked", "Under Maintenance", "Inactive"]


class VehicleResponse(VehicleCreate):
    vehicle_id: str
    location_city: Optional[str] = None
    location_address: Optional[str] = None
    owner_name: Optional[str] = None


# ==========================================
# BOOKING MODELS
# ==========================================
class BookingCreate(BaseModel):
    booking_id: Optional[str] = None
    tourist_id: str
    vehicle_id: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD


class BookingDecision(BaseModel):
    booking_status: Literal["Approved", "Rejected"]
    cancellation_reason: Optional[str] = None


class BookingCancel(BaseModel):
    cancellation_reason: str


class BookingResponse(BaseModel):
    booking_id: str
    tourist_id: str
    vehicle_id: str
    start_date: str
    end_date: str
    booking_date: Optional[str] = None
    rental_amount: float
    booking_status: Literal["Pending", "Approved", "Rejected", "Cancelled", "Completed"]
    cancellation_reason: Optional[str] = None
    tourist_name: Optional[str] = None
    vehicle_brand: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_number: Optional[str] = None
    security_deposit: Optional[float] = None
    is_paid: Optional[bool] = False
    payment_status: Optional[str] = None


# ==========================================
# PAYMENT MODELS
# ==========================================
class PaymentCreate(BaseModel):
    payment_id: Optional[str] = None
    booking_id: str
    amount: float
    payment_type: Literal["Rental", "Deposit", "Refund", "Penalty"]
    payment_status: Literal["Pending", "Success", "Failed", "Refunded"] = "Success"
    transaction_reference: Optional[str] = None
    commission_rate: float = 0.10  # 10% platform commission default


class PaymentResponse(BaseModel):
    payment_id: str
    booking_id: str
    amount: float
    payment_type: Literal["Rental", "Deposit", "Refund", "Penalty"]
    payment_status: Literal["Pending", "Success", "Failed", "Refunded"]
    payment_date: Optional[str] = None
    transaction_reference: str
    commission_amount: float
    owner_earning: float


# ==========================================
# INSPECTION MODELS
# ==========================================
class InspectionCreate(BaseModel):
    inspection_id: Optional[str] = None
    booking_id: str
    inspection_type: Literal["Pickup", "Return"]
    vehicle_condition: str
    fuel_status: Literal["Full", "Half", "Reserve", "Low", "Moderate"] = "Full"
    notes: Optional[str] = None


class InspectionResponse(InspectionCreate):
    inspection_id: str
    inspection_date: Optional[str] = None


# ==========================================
# DAMAGE & PENALTY MODELS
# ==========================================
class IncidentCreate(BaseModel):
    incident_id: Optional[str] = None
    booking_id: str
    incident_type: Literal["Damage", "Late Return", "Other"]
    description: str
    amount: float


class IncidentResolveRequest(BaseModel):
    resolution_status: Literal["Upheld", "Waived", "Resolved"]


class IncidentResponse(IncidentCreate):
    incident_id: str
    reported_date: Optional[str] = None
    resolution_status: Literal["Under review", "Upheld", "Waived", "Resolved"]


# ==========================================
# MAINTENANCE MODELS
# ==========================================
class MaintenanceCreate(BaseModel):
    maintenance_id: Optional[str] = None
    vehicle_id: str
    maintenance_type: str
    description: str
    cost: float = 0.0


class MaintenanceCompleteRequest(BaseModel):
    cost: Optional[float] = None


class MaintenanceResponse(MaintenanceCreate):
    maintenance_id: str
    maintenance_date: Optional[str] = None
    status: Literal["In Progress", "Completed"]
