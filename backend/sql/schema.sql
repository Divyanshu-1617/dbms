-- ====================================================================
-- Peer-to-Peer Tourist Bike Rental Management System
-- Relational Database Schema (DDL) with Advanced Database Features
-- ====================================================================

PRAGMA foreign_keys = ON;

-- Clean existing views and tables
DROP VIEW IF EXISTS VIEW_ACTIVE_RENTALS;
DROP VIEW IF EXISTS VIEW_OWNER_REVENUE_SUMMARY;
DROP TRIGGER IF EXISTS trg_payment_update_vehicle_booked;
DROP TRIGGER IF EXISTS trg_inspection_complete_booking;
DROP TRIGGER IF EXISTS trg_booking_prevent_unverified_owner;

DROP TABLE IF EXISTS DAMAGE_PENALTY;
DROP TABLE IF EXISTS INSPECTION;
DROP TABLE IF EXISTS PAYMENT;
DROP TABLE IF EXISTS BOOKING;
DROP TABLE IF EXISTS MAINTENANCE;
DROP TABLE IF EXISTS VEHICLE;
DROP TABLE IF EXISTS LOCATION;
DROP TABLE IF EXISTS USER;

-- 1. LOCATION Table
CREATE TABLE LOCATION (
    location_id TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    pincode TEXT NOT NULL,
    pickup_instructions TEXT
);

-- 2. USER Table (All actors: Tourist, Owner, Admin)
CREATE TABLE USER (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('Tourist', 'Owner', 'Admin')),
    verification_status TEXT NOT NULL DEFAULT 'Pending' CHECK (verification_status IN ('Pending', 'Verified', 'Rejected')),
    account_status TEXT NOT NULL DEFAULT 'Active' CHECK (account_status IN ('Active', 'Inactive', 'Suspended')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. VEHICLE Table
CREATE TABLE VEHICLE (
    vehicle_id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    location_id TEXT NOT NULL,
    vehicle_number TEXT NOT NULL UNIQUE,
    vehicle_type TEXT NOT NULL,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    rental_rate_per_day REAL NOT NULL CHECK (rental_rate_per_day > 0),
    security_deposit REAL NOT NULL CHECK (security_deposit >= 0),
    vehicle_status TEXT NOT NULL DEFAULT 'Available' CHECK (vehicle_status IN ('Available', 'Booked', 'Under Maintenance', 'Inactive')),
    FOREIGN KEY (owner_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES LOCATION(location_id) ON DELETE RESTRICT
);

-- 4. BOOKING Table
CREATE TABLE BOOKING (
    booking_id TEXT PRIMARY KEY,
    tourist_id TEXT NOT NULL,
    vehicle_id TEXT NOT NULL,
    start_date TEXT NOT NULL, -- Format: YYYY-MM-DD
    end_date TEXT NOT NULL,   -- Format: YYYY-MM-DD
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rental_amount REAL NOT NULL CHECK (rental_amount >= 0),
    booking_status TEXT NOT NULL DEFAULT 'Pending' CHECK (booking_status IN ('Pending', 'Approved', 'Rejected', 'Cancelled', 'Completed')),
    cancellation_reason TEXT,
    FOREIGN KEY (tourist_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES VEHICLE(vehicle_id) ON DELETE CASCADE,
    CHECK (end_date >= start_date)
);

-- 5. PAYMENT Table
CREATE TABLE PAYMENT (
    payment_id TEXT PRIMARY KEY,
    booking_id TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    payment_type TEXT NOT NULL CHECK (payment_type IN ('Rental', 'Deposit', 'Refund', 'Penalty')),
    payment_status TEXT NOT NULL DEFAULT 'Success' CHECK (payment_status IN ('Pending', 'Success', 'Failed', 'Refunded')),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_reference TEXT UNIQUE NOT NULL,
    commission_amount REAL DEFAULT 0.0 CHECK (commission_amount >= 0),
    owner_earning REAL DEFAULT 0.0 CHECK (owner_earning >= 0),
    FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE
);

-- 6. INSPECTION Table
CREATE TABLE INSPECTION (
    inspection_id TEXT PRIMARY KEY,
    booking_id TEXT NOT NULL,
    inspection_type TEXT NOT NULL CHECK (inspection_type IN ('Pickup', 'Return')),
    inspection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vehicle_condition TEXT NOT NULL,
    fuel_status TEXT NOT NULL DEFAULT 'Full',
    notes TEXT,
    FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE
);

-- 7. DAMAGE_PENALTY Table
CREATE TABLE DAMAGE_PENALTY (
    incident_id TEXT PRIMARY KEY,
    booking_id TEXT NOT NULL,
    incident_type TEXT NOT NULL CHECK (incident_type IN ('Damage', 'Late Return', 'Other')),
    description TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolution_status TEXT NOT NULL DEFAULT 'Under review' CHECK (resolution_status IN ('Under review', 'Upheld', 'Waived', 'Resolved')),
    FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE
);

-- 8. MAINTENANCE Table
CREATE TABLE MAINTENANCE (
    maintenance_id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    maintenance_type TEXT NOT NULL,
    description TEXT NOT NULL,
    maintenance_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cost REAL NOT NULL DEFAULT 0.0 CHECK (cost >= 0),
    status TEXT NOT NULL DEFAULT 'In Progress' CHECK (status IN ('In Progress', 'Completed')),
    FOREIGN KEY (vehicle_id) REFERENCES VEHICLE(vehicle_id) ON DELETE CASCADE
);

-- ====================================================================
-- Indexes for Performance & Rapid Query Retrieval
-- ====================================================================
CREATE INDEX idx_vehicle_owner ON VEHICLE(owner_id);
CREATE INDEX idx_vehicle_status ON VEHICLE(vehicle_status);
CREATE INDEX idx_booking_vehicle ON BOOKING(vehicle_id, booking_status);
CREATE INDEX idx_booking_tourist ON BOOKING(tourist_id);
CREATE INDEX idx_payment_booking ON PAYMENT(booking_id);
CREATE INDEX idx_inspection_booking ON INSPECTION(booking_id);
CREATE INDEX idx_damage_booking ON DAMAGE_PENALTY(booking_id);
CREATE INDEX idx_maintenance_vehicle ON MAINTENANCE(vehicle_id, status);

-- ====================================================================
-- ADVANCED DATABASE FEATURES: VIEWS
-- ====================================================================

-- VIEW 1: Active Rentals with Tourist, Vehicle, and Location details
CREATE VIEW VIEW_ACTIVE_RENTALS AS
SELECT 
    b.booking_id,
    b.start_date,
    b.end_date,
    b.booking_status,
    b.rental_amount,
    u.user_id AS tourist_id,
    u.name AS tourist_name,
    u.phone AS tourist_phone,
    v.vehicle_id,
    v.brand || ' ' || v.model AS vehicle_name,
    v.vehicle_number,
    v.vehicle_status,
    l.city AS pickup_city,
    l.address AS pickup_address,
    o.name AS owner_name
FROM BOOKING b
JOIN USER u ON b.tourist_id = u.user_id
JOIN VEHICLE v ON b.vehicle_id = v.vehicle_id
JOIN LOCATION l ON v.location_id = l.location_id
JOIN USER o ON v.owner_id = o.user_id
WHERE b.booking_status IN ('Pending', 'Approved', 'Booked');

-- VIEW 2: Owner Revenue & Commission Summary
CREATE VIEW VIEW_OWNER_REVENUE_SUMMARY AS
SELECT 
    o.user_id AS owner_id,
    o.name AS owner_name,
    o.email AS owner_email,
    COUNT(DISTINCT v.vehicle_id) AS total_vehicles_listed,
    COUNT(DISTINCT b.booking_id) AS total_bookings_received,
    COALESCE(SUM(p.amount), 0.0) AS total_gross_revenue,
    COALESCE(SUM(p.commission_amount), 0.0) AS total_platform_commission,
    COALESCE(SUM(p.owner_earning), 0.0) AS net_owner_earnings
FROM USER o
LEFT JOIN VEHICLE v ON o.user_id = v.owner_id
LEFT JOIN BOOKING b ON v.vehicle_id = b.vehicle_id AND b.booking_status != 'Cancelled'
LEFT JOIN PAYMENT p ON b.booking_id = p.booking_id AND p.payment_type = 'Rental' AND p.payment_status = 'Success'
WHERE o.role = 'Owner'
GROUP BY o.user_id, o.name, o.email;

-- ====================================================================
-- ADVANCED DATABASE FEATURES: TRIGGERS
-- ====================================================================

-- TRIGGER 1: Automatically update vehicle status to 'Booked' upon successful rental payment
CREATE TRIGGER trg_payment_update_vehicle_booked
AFTER INSERT ON PAYMENT
WHEN NEW.payment_type = 'Rental' AND NEW.payment_status = 'Success'
BEGIN
    UPDATE VEHICLE
    SET vehicle_status = 'Booked'
    WHERE vehicle_id = (SELECT vehicle_id FROM BOOKING WHERE booking_id = NEW.booking_id);
END;

-- TRIGGER 2: Automatically mark booking 'Completed' and release vehicle to 'Available' upon Return inspection
CREATE TRIGGER trg_inspection_complete_booking
AFTER INSERT ON INSPECTION
WHEN NEW.inspection_type = 'Return'
BEGIN
    UPDATE BOOKING
    SET booking_status = 'Completed'
    WHERE booking_id = NEW.booking_id;

    UPDATE VEHICLE
    SET vehicle_status = 'Available'
    WHERE vehicle_id = (SELECT vehicle_id FROM BOOKING WHERE booking_id = NEW.booking_id);
END;
