-- ====================================================================
-- Peer-to-Peer Tourist Bike Rental Management System
-- MySQL DDL Schema, Stored Procedures, Functions, Triggers, Views,
-- and ACID Transaction Management Demonstration
-- Target Database: MySQL 8.0+ / MariaDB
-- ====================================================================

DROP DATABASE IF EXISTS bikerental_db;
CREATE DATABASE bikerental_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bikerental_db;

-- --------------------------------------------------------------------
-- 1. LOCATION Table
-- --------------------------------------------------------------------
CREATE TABLE LOCATION (
    location_id VARCHAR(32) PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(20) NOT NULL,
    pickup_instructions TEXT
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 2. USER Table
-- --------------------------------------------------------------------
CREATE TABLE USER (
    user_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Tourist', 'Owner', 'Admin') NOT NULL,
    verification_status ENUM('Pending', 'Verified', 'Rejected') NOT NULL DEFAULT 'Pending',
    account_status ENUM('Active', 'Inactive', 'Suspended') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 3. VEHICLE Table
-- --------------------------------------------------------------------
CREATE TABLE VEHICLE (
    vehicle_id VARCHAR(32) PRIMARY KEY,
    owner_id VARCHAR(32) NOT NULL,
    location_id VARCHAR(32) NOT NULL,
    vehicle_number VARCHAR(50) NOT NULL UNIQUE,
    vehicle_type VARCHAR(50) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    rental_rate_per_day DECIMAL(10,2) NOT NULL CHECK (rental_rate_per_day > 0),
    security_deposit DECIMAL(10,2) NOT NULL CHECK (security_deposit >= 0),
    vehicle_status ENUM('Available', 'Booked', 'Under Maintenance', 'Inactive') NOT NULL DEFAULT 'Available',
    FOREIGN KEY (owner_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES LOCATION(location_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 4. BOOKING Table
-- --------------------------------------------------------------------
CREATE TABLE BOOKING (
    booking_id VARCHAR(32) PRIMARY KEY,
    tourist_id VARCHAR(32) NOT NULL,
    vehicle_id VARCHAR(32) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rental_amount DECIMAL(10,2) NOT NULL CHECK (rental_amount >= 0),
    booking_status ENUM('Pending', 'Approved', 'Rejected', 'Cancelled', 'Completed') NOT NULL DEFAULT 'Pending',
    cancellation_reason TEXT,
    FOREIGN KEY (tourist_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES VEHICLE(vehicle_id) ON DELETE CASCADE,
    CHECK (end_date >= start_date)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 5. PAYMENT Table
-- --------------------------------------------------------------------
CREATE TABLE PAYMENT (
    payment_id VARCHAR(32) PRIMARY KEY,
    booking_id VARCHAR(32) NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    payment_type ENUM('Rental', 'Deposit', 'Refund', 'Penalty') NOT NULL,
    payment_status ENUM('Pending', 'Success', 'Failed', 'Refunded') NOT NULL DEFAULT 'Success',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_reference VARCHAR(100) UNIQUE NOT NULL,
    commission_amount DECIMAL(10,2) DEFAULT 0.00 CHECK (commission_amount >= 0),
    owner_earning DECIMAL(10,2) DEFAULT 0.00 CHECK (owner_earning >= 0),
    FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 6. INSPECTION Table
-- --------------------------------------------------------------------
CREATE TABLE INSPECTION (
    inspection_id VARCHAR(32) PRIMARY KEY,
    booking_id VARCHAR(32) NOT NULL,
    inspection_type ENUM('Pickup', 'Return') NOT NULL,
    inspection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vehicle_condition VARCHAR(100) NOT NULL,
    fuel_status VARCHAR(50) NOT NULL DEFAULT 'Full',
    notes TEXT,
    FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 7. DAMAGE_PENALTY Table
-- --------------------------------------------------------------------
CREATE TABLE DAMAGE_PENALTY (
    incident_id VARCHAR(32) PRIMARY KEY,
    booking_id VARCHAR(32) NOT NULL,
    incident_type ENUM('Damage', 'Late Return', 'Other') NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolution_status ENUM('Under review', 'Upheld', 'Waived', 'Resolved') NOT NULL DEFAULT 'Under review',
    FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- 8. MAINTENANCE Table
-- --------------------------------------------------------------------
CREATE TABLE MAINTENANCE (
    maintenance_id VARCHAR(32) PRIMARY KEY,
    vehicle_id VARCHAR(32) NOT NULL,
    maintenance_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    maintenance_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cost DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK (cost >= 0),
    status ENUM('In Progress', 'Completed') NOT NULL DEFAULT 'In Progress',
    FOREIGN KEY (vehicle_id) REFERENCES VEHICLE(vehicle_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------------------
-- INDEXES
-- --------------------------------------------------------------------
CREATE INDEX idx_vehicle_owner ON VEHICLE(owner_id);
CREATE INDEX idx_vehicle_status ON VEHICLE(vehicle_status);
CREATE INDEX idx_booking_vehicle ON BOOKING(vehicle_id, booking_status);
CREATE INDEX idx_booking_tourist ON BOOKING(tourist_id);
CREATE INDEX idx_payment_booking ON PAYMENT(booking_id);
CREATE INDEX idx_inspection_booking ON INSPECTION(booking_id);
CREATE INDEX idx_damage_booking ON DAMAGE_PENALTY(booking_id);
CREATE INDEX idx_maintenance_vehicle ON MAINTENANCE(vehicle_id, status);

-- ====================================================================
-- ADVANCED DATABASE FEATURES: 2 VIEWS
-- ====================================================================

-- VIEW 1: Active Rentals with tourist, vehicle, and pickup details
CREATE OR REPLACE VIEW VIEW_ACTIVE_RENTALS AS
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
    CONCAT(v.brand, ' ', v.model) AS vehicle_name,
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
WHERE b.booking_status IN ('Pending', 'Approved');

-- VIEW 2: Owner Revenue, Booking Volume, and Commission Summary
CREATE OR REPLACE VIEW VIEW_OWNER_REVENUE_SUMMARY AS
SELECT 
    o.user_id AS owner_id,
    o.name AS owner_name,
    o.email AS owner_email,
    COUNT(DISTINCT v.vehicle_id) AS total_vehicles_listed,
    COUNT(DISTINCT b.booking_id) AS total_bookings_received,
    COALESCE(SUM(p.amount), 0.00) AS total_gross_revenue,
    COALESCE(SUM(p.commission_amount), 0.00) AS total_platform_commission,
    COALESCE(SUM(p.owner_earning), 0.00) AS net_owner_earnings
FROM USER o
LEFT JOIN VEHICLE v ON o.user_id = v.owner_id
LEFT JOIN BOOKING b ON v.vehicle_id = b.vehicle_id AND b.booking_status != 'Cancelled'
LEFT JOIN PAYMENT p ON b.booking_id = p.booking_id AND p.payment_type = 'Rental' AND p.payment_status = 'Success'
WHERE o.role = 'Owner'
GROUP BY o.user_id, o.name, o.email;

-- ====================================================================
-- ADVANCED DATABASE FEATURES: 1 STORED FUNCTION
-- ====================================================================

DELIMITER $$

-- FUNCTION: Calculate Total Rental Price (Daily rate * (Days between dates + 1))
CREATE FUNCTION fn_calculate_rental_cost(
    p_vehicle_id VARCHAR(32),
    p_start_date DATE,
    p_end_date DATE
)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_daily_rate DECIMAL(10,2);
    DECLARE v_days INT;
    DECLARE v_total DECIMAL(10,2);

    IF p_end_date < p_start_date THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'End date cannot be prior to start date';
    END IF;

    SELECT rental_rate_per_day INTO v_daily_rate
    FROM VEHICLE
    WHERE vehicle_id = p_vehicle_id;

    SET v_days = DATEDIFF(p_end_date, p_start_date) + 1;
    SET v_total = v_days * v_daily_rate;

    RETURN v_total;
END$$

-- ====================================================================
-- ADVANCED DATABASE FEATURES: 2 STORED PROCEDURES
-- ====================================================================

-- PROCEDURE 1: Process Booking Payment with 10% Platform Commission Split
CREATE PROCEDURE sp_process_rental_payment(
    IN p_payment_id VARCHAR(32),
    IN p_booking_id VARCHAR(32),
    IN p_amount DECIMAL(10,2),
    IN p_tx_ref VARCHAR(100),
    OUT p_commission DECIMAL(10,2),
    OUT p_owner_earning DECIMAL(10,2),
    OUT p_status VARCHAR(50)
)
proc_label: BEGIN
    DECLARE v_booking_status VARCHAR(50);
    DECLARE v_vehicle_id VARCHAR(32);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR: Payment transaction failed';
    END;

    START TRANSACTION;

    SELECT booking_status, vehicle_id INTO v_booking_status, v_vehicle_id
    FROM BOOKING
    WHERE booking_id = p_booking_id
    FOR UPDATE;

    IF v_booking_status IS NULL THEN
        SET p_status = 'Booking does not exist';
        ROLLBACK;
        LEAVE proc_label;
    END IF;

    IF v_booking_status != 'Approved' THEN
        SET p_status = 'Booking is not in Approved state';
        ROLLBACK;
        LEAVE proc_label;
    END IF;

    -- Compute 10% commission split
    SET p_commission = ROUND(p_amount * 0.10, 2);
    SET p_owner_earning = p_amount - p_commission;

    -- Insert payment ledger record
    INSERT INTO PAYMENT (
        payment_id, booking_id, amount, payment_type, payment_status,
        transaction_reference, commission_amount, owner_earning
    ) VALUES (
        p_payment_id, p_booking_id, p_amount, 'Rental', 'Success',
        p_tx_ref, p_commission, p_owner_earning
    );

    -- Update vehicle status to Booked
    UPDATE VEHICLE SET vehicle_status = 'Booked' WHERE vehicle_id = v_vehicle_id;

    COMMIT;
    SET p_status = 'SUCCESS';
END$$

-- PROCEDURE 2: Check Overlap & Create Booking Request atomically
CREATE PROCEDURE sp_create_booking_request(
    IN p_booking_id VARCHAR(32),
    IN p_tourist_id VARCHAR(32),
    IN p_vehicle_id VARCHAR(32),
    IN p_start_date DATE,
    IN p_end_date DATE,
    OUT p_result VARCHAR(100)
)
proc_label: BEGIN
    DECLARE v_overlap_count INT;
    DECLARE v_veh_status VARCHAR(50);
    DECLARE v_total_cost DECIMAL(10,2);
    DECLARE v_owner_verif VARCHAR(50);

    -- 1. Check vehicle availability and owner KYC status
    SELECT v.vehicle_status, u.verification_status 
    INTO v_veh_status, v_owner_verif
    FROM VEHICLE v
    JOIN USER u ON v.owner_id = u.user_id
    WHERE v.vehicle_id = p_vehicle_id;

    IF v_owner_verif != 'Verified' THEN
        SET p_result = 'REJECTED: Vehicle owner KYC is not verified';
        LEAVE proc_label;
    END IF;

    IF v_veh_status = 'Under Maintenance' THEN
        SET p_result = 'REJECTED: Vehicle is under maintenance';
        LEAVE proc_label;
    END IF;

    -- 2. Check for overlapping Approved bookings
    SELECT COUNT(*) INTO v_overlap_count
    FROM BOOKING
    WHERE vehicle_id = p_vehicle_id
      AND booking_status = 'Approved'
      AND start_date <= p_end_date
      AND end_date >= p_start_date;

    IF v_overlap_count > 0 THEN
        SET p_result = 'REJECTED: Overlapping approved booking exists';
        LEAVE proc_label;
    END IF;

    -- 3. Calculate rental cost via stored function
    SET v_total_cost = fn_calculate_rental_cost(p_vehicle_id, p_start_date, p_end_date);

    -- 4. Create booking record
    INSERT INTO BOOKING (
        booking_id, tourist_id, vehicle_id, start_date, end_date, rental_amount, booking_status
    ) VALUES (
        p_booking_id, p_tourist_id, p_vehicle_id, p_start_date, p_end_date, v_total_cost, 'Pending'
    );

    SET p_result = 'SUCCESS: Booking request created';
END$$

-- ====================================================================
-- ADVANCED DATABASE FEATURES: 2 TRIGGERS
-- ====================================================================

-- TRIGGER 1: Automatically set vehicle to 'Booked' upon successful rental payment
CREATE TRIGGER trg_payment_after_insert
AFTER INSERT ON PAYMENT
FOR EACH ROW
BEGIN
    IF NEW.payment_type = 'Rental' AND NEW.payment_status = 'Success' THEN
        UPDATE VEHICLE
        SET vehicle_status = 'Booked'
        WHERE vehicle_id = (SELECT vehicle_id FROM BOOKING WHERE booking_id = NEW.booking_id);
    END IF;
END$$

-- TRIGGER 2: Complete booking and release vehicle to 'Available' upon Return inspection
CREATE TRIGGER trg_inspection_after_insert
AFTER INSERT ON INSPECTION
FOR EACH ROW
BEGIN
    IF NEW.inspection_type = 'Return' THEN
        UPDATE BOOKING
        SET booking_status = 'Completed'
        WHERE booking_id = NEW.booking_id;

        UPDATE VEHICLE
        SET vehicle_status = 'Available'
        WHERE vehicle_id = (SELECT vehicle_id FROM BOOKING WHERE booking_id = NEW.booking_id);
    END IF;
END$$

DELIMITER ;

-- ====================================================================
-- TRANSACTION MANAGEMENT: COMMIT, ROLLBACK, SAVEPOINT DEMO
-- ====================================================================

-- Transaction Scenario: Booking Settlement with Security Deposit Refund
-- Step 1: Start Transaction
START TRANSACTION;

-- Step 2: Insert Return Inspection
INSERT INTO INSPECTION (inspection_id, booking_id, inspection_type, vehicle_condition, fuel_status, notes)
VALUES ('I901', 'B101', 'Return', 'Minor scratch on mirror', 'Full', 'Handover completed');

-- Step 3: Set Savepoint before penalty assessment
SAVEPOINT before_penalty;

-- Step 4: Assess damage penalty
INSERT INTO DAMAGE_PENALTY (incident_id, booking_id, incident_type, description, amount, resolution_status)
VALUES ('D801', 'B101', 'Damage', 'Mirror scratch penalty', 250.00, 'Upheld');

-- If damage was found to be pre-existing on pickup inspection photo:
-- ROLLBACK TO SAVEPOINT before_penalty; 

-- Step 5: Process refund of remaining deposit
INSERT INTO PAYMENT (payment_id, booking_id, amount, payment_type, payment_status, transaction_reference)
VALUES ('P999', 'B101', 750.00, 'Refund', 'Success', 'TXN-REFUND-999');

-- Step 6: Commit entire transaction to permanently persist changes
COMMIT;
