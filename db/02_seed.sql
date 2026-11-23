-- Stock Management System - sample data

-- Passwords are stored hashed (PBKDF2-SHA256).
-- admin / admin123   (role: admin)
-- user  / user123    (role: user)
-- ayse  / user123    (role: user)
INSERT INTO app_user (username, password_hash, full_name, role) VALUES
('admin', 'pbkdf2:sha256:600000$Xk2pQ9vLm4Zt7RbA$5d2826ded5beeb10ba091baae435183aebde895642f100a91c60efb5b7eb1234', 'System Admin', 'admin'),
('user',  'pbkdf2:sha256:600000$Hn5cW8yJd3Uf6GsE$66925784f02a37b7d1cda3944e5ec9e5aa990d1a9c7fbc1bc6a9c8bf84eb3cfa', 'Mehmet Kaya',  'user'),
('ayse',  'pbkdf2:sha256:600000$Tq7mB2xKe9Vr4NpC$082b7cf596413a52ffe64472fd993055f6896fa740e5001e5cb88d8591011adf', 'Ayse Demir',   'user');

INSERT INTO category (name, description) VALUES
('Electronics', 'Computers, phones and accessories'),
('Stationery',  'Office and school supplies'),
('Cleaning',    'Cleaning products'),
('Food',        'Packaged food and drinks');

INSERT INTO supplier (name, phone, email, city) VALUES
('Anadolu Teknoloji', '0312 555 10 10', 'info@anadoluteknoloji.example', 'Ankara'),
('Kirtasiye Dunyasi', '0212 555 20 20', 'satis@kirtasiyedunyasi.example', 'Istanbul'),
('Temiz Is Ltd.',     '0232 555 30 30', 'siparis@temizis.example',       'Izmir');

INSERT INTO warehouse (name, location) VALUES
('Main Warehouse', 'Ankara - Incek'),
('Store Depot',    'Ankara - Kizilay'),
('Izmir Depot',    'Izmir - Bornova');

INSERT INTO product (name, unit_price, min_stock, category_id, supplier_id) VALUES
('Wireless Mouse',      350.00, 10, 1, 1),
('USB-C Cable 1m',      120.00, 20, 1, 1),
('Keyboard',            900.00,  5, 1, 1),
('A4 Paper (500 pcs)',  180.00, 30, 2, 2),
('Ballpoint Pen',        15.00, 50, 2, 2),
('Notebook',             60.00, 25, 2, 2),
('Surface Cleaner 1L',   95.00, 15, 3, 3),
('Bottled Water 0.5L',   10.00, 40, 4, NULL);

INSERT INTO stock_movement (product_id, warehouse_id, user_id, movement_type, quantity, movement_date, note) VALUES
(1, 1, 1, 'IN',   50, '2026-11-02 09:15', 'Initial stock'),
(2, 1, 1, 'IN',  100, '2026-11-02 09:20', 'Initial stock'),
(3, 1, 1, 'IN',   20, '2026-11-02 09:25', 'Initial stock'),
(4, 1, 2, 'IN',  200, '2026-11-03 10:00', 'Purchase order 1001'),
(5, 2, 2, 'IN',  300, '2026-11-03 10:10', 'Purchase order 1001'),
(6, 2, 2, 'IN',   80, '2026-11-03 10:20', 'Purchase order 1001'),
(7, 3, 3, 'IN',   40, '2026-11-04 11:00', 'Purchase order 1002'),
(8, 2, 3, 'IN',  120, '2026-11-04 11:30', 'Purchase order 1003'),
(1, 1, 2, 'OUT',  45, '2026-11-05 14:00', 'Sale'),
(3, 1, 2, 'OUT',  12, '2026-11-06 15:30', 'Sale'),
(4, 1, 3, 'OUT', 150, '2026-11-09 09:45', 'Sent to store'),
(4, 2, 3, 'IN',  150, '2026-11-09 09:50', 'Received from main warehouse'),
(5, 2, 2, 'OUT', 270, '2026-11-10 13:00', 'Sale'),
(8, 2, 2, 'OUT',  90, '2026-11-11 16:20', 'Sale'),
(7, 3, 3, 'OUT',  10, '2026-11-12 10:05', 'Sale');
