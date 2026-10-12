-- ====================================================================
-- Initial Seed Data for Tourist Bike Rental Management System
-- Mirrors the characters and real-world scenarios from the report
-- ====================================================================

-- 1. Insert Locations
INSERT INTO LOCATION (location_id, address, city, state, pincode, pickup_instructions) VALUES
('L01', 'Near Mall Road, Old Manali', 'Manali', 'Himachal Pradesh', '175131', 'Pickup point is behind the main taxi stand. Look for Green Valley Garage.'),
('L02', 'Aleo, Naggar Road', 'Manali', 'Himachal Pradesh', '175103', 'Near Himalayan River Resort, landmark Cafe 1947.'),
('L03', 'The Ridge, Near Christ Church', 'Shimla', 'Himachal Pradesh', '171001', 'Walk towards Lakkar Bazaar ramp, shop number 14.');

-- 2. Insert Users
-- Admin
INSERT INTO USER (user_id, name, email, phone, password, role, verification_status, account_status) VALUES
('U100', 'Anjali Sharma (Admin)', 'admin@bikerental.com', '9811001122', 'admin123', 'Admin', 'Verified', 'Active');

-- Owners
INSERT INTO USER (user_id, name, email, phone, password, role, verification_status, account_status) VALUES
('U150', 'Rakesh Verma', 'rakesh.verma@example.com', '9816012345', 'rakesh123', 'Owner', 'Verified', 'Active'),
('U151', 'Vikram Negi', 'vikram.negi@example.com', '9816098765', 'vikram123', 'Owner', 'Verified', 'Active'),
('U152', 'Suresh Raina', 'suresh.newowner@example.com', '9876543210', 'suresh123', 'Owner', 'Pending', 'Inactive'); -- New owner needing verification (Scenario 9.10)

-- Tourists
INSERT INTO USER (user_id, name, email, phone, password, role, verification_status, account_status) VALUES
('U201', 'Aarav Mehta', 'aarav.tourist@example.com', '9988776655', 'aarav123', 'Tourist', 'Verified', 'Active'),
('U202', 'Priya Kapoor', 'priya.tourist@example.com', '9988112233', 'priya123', 'Tourist', 'Verified', 'Active'),
('U205', 'Rahul Sen', 'rahul.tourist@example.com', '9977665544', 'rahul123', 'Tourist', 'Verified', 'Active');

-- 3. Insert Vehicles
INSERT INTO VEHICLE (vehicle_id, owner_id, location_id, vehicle_number, vehicle_type, brand, model, year, rental_rate_per_day, security_deposit, vehicle_status) VALUES
('V301', 'U150', 'L01', 'HP-01-AA-1001', 'Scooter', 'Honda', 'Activa 6G', 2023, 500.0, 1000.0, 'Available'),
('V302', 'U150', 'L02', 'HP-01-BB-2002', 'Cruiser', 'Royal Enfield', 'Classic 350', 2022, 1200.0, 2500.0, 'Available'),
('V303', 'U150', 'L01', 'HP-01-CC-3003', 'Scooter', 'TVS', 'Jupiter 125', 2023, 550.0, 1000.0, 'Available'),
('V355', 'U151', 'L03', 'HP-02-DD-4004', 'Motorcycle', 'Yamaha', 'FZ-S V3', 2022, 700.0, 1500.0, 'Available');
