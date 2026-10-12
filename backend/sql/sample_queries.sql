-- ====================================================================
-- DBMS Lab Assessment - Sample SQL Queries
-- DDL, DML, Constraints, Joins, Subqueries, Aggregations, Window Functions
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. DDL: Create Table with Constraints
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS AUDIT_LOG (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- --------------------------------------------------------------------
-- 2. DML: INSERT, UPDATE, DELETE Operations
-- --------------------------------------------------------------------
-- Insert new location
INSERT INTO LOCATION (location_id, address, city, state, pincode, pickup_instructions)
VALUES ('L04', 'Mall Road, Near Christ Church', 'Shimla', 'Himachal Pradesh', '171001', 'Pickup near town hall parking');

-- Update vehicle rental rate
UPDATE VEHICLE
SET rental_rate_per_day = 600.00
WHERE vehicle_id = 'V303' AND vehicle_status = 'Available';

-- Delete cancelled bookings older than retention window
DELETE FROM BOOKING
WHERE booking_status = 'Cancelled' 
  AND booking_date < datetime('now', '-90 days');

-- --------------------------------------------------------------------
-- 3. SQL FUNCTIONS & STRING / DATE MANIPULATIONS
-- --------------------------------------------------------------------
-- Calculate rental duration in days and formatted period
SELECT 
    booking_id,
    tourist_id,
    start_date,
    end_date,
    (julianday(end_date) - julianday(start_date) + 1) AS total_days,
    UPPER(booking_status) AS uppercase_status,
    strftime('%Y-%m', booking_date) AS booking_month
FROM BOOKING;

-- --------------------------------------------------------------------
-- 4. COMPLEX JOINS: Multi-table relational lookup
-- --------------------------------------------------------------------
-- Comprehensive booking report joining 5 entities
SELECT 
    b.booking_id,
    u.name AS tourist_name,
    u.phone AS tourist_phone,
    v.brand || ' ' || v.model AS bike_name,
    v.vehicle_number,
    l.city AS pickup_city,
    l.address AS pickup_location,
    owner.name AS bike_owner,
    b.start_date,
    b.end_date,
    b.rental_amount,
    COALESCE(p.amount, 0.0) AS paid_amount,
    COALESCE(p.payment_status, 'Unpaid') AS payment_status
FROM BOOKING b
JOIN USER u ON b.tourist_id = u.user_id
JOIN VEHICLE v ON b.vehicle_id = v.vehicle_id
JOIN LOCATION l ON v.location_id = l.location_id
JOIN USER owner ON v.owner_id = owner.user_id
LEFT JOIN PAYMENT p ON b.booking_id = p.booking_id AND p.payment_type = 'Rental';

-- --------------------------------------------------------------------
-- 5. SUBQUERIES: Non-correlated and Correlated
-- --------------------------------------------------------------------
-- Non-correlated: Find tourists who have spent more than the platform average
SELECT user_id, name, email
FROM USER
WHERE user_id IN (
    SELECT tourist_id
    FROM BOOKING
    GROUP BY tourist_id
    HAVING SUM(rental_amount) > (
        SELECT AVG(total_spent)
        FROM (
            SELECT SUM(rental_amount) AS total_spent
            FROM BOOKING
            WHERE booking_status != 'Cancelled'
            GROUP BY tourist_id
        )
    )
);

-- Correlated Subquery: Find vehicles that have never had a damage incident reported
SELECT v.vehicle_id, v.brand, v.model, v.vehicle_number
FROM VEHICLE v
WHERE NOT EXISTS (
    SELECT 1 
    FROM BOOKING b
    JOIN DAMAGE_PENALTY dp ON b.booking_id = dp.booking_id
    WHERE b.vehicle_id = v.vehicle_id
);

-- --------------------------------------------------------------------
-- 6. AGGREGATE FUNCTIONS & GROUP BY / HAVING
-- --------------------------------------------------------------------
-- Revenue, booking count, and average rental rate grouped by city
SELECT 
    l.city,
    COUNT(DISTINCT v.vehicle_id) AS total_fleet_in_city,
    COUNT(b.booking_id) AS total_bookings,
    ROUND(AVG(v.rental_rate_per_day), 2) AS avg_daily_rate,
    COALESCE(SUM(p.amount), 0.0) AS total_city_revenue,
    COALESCE(SUM(p.commission_amount), 0.0) AS platform_commission
FROM LOCATION l
JOIN VEHICLE v ON l.location_id = v.location_id
LEFT JOIN BOOKING b ON v.vehicle_id = b.vehicle_id
LEFT JOIN PAYMENT p ON b.booking_id = p.booking_id AND p.payment_status = 'Success'
GROUP BY l.city
HAVING COUNT(DISTINCT v.vehicle_id) > 0
ORDER BY total_city_revenue DESC;
