-- Stock Management System - table definitions (PostgreSQL)

CREATE TABLE app_user (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(30)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(80)  NOT NULL,
    role          VARCHAR(10)  NOT NULL DEFAULT 'user'
                  CHECK (role IN ('admin', 'user'))
);

CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200)
);

CREATE TABLE supplier (
    supplier_id SERIAL PRIMARY KEY,
    name        VARCHAR(80) NOT NULL,
    phone       VARCHAR(20),
    email       VARCHAR(80) UNIQUE,
    city        VARCHAR(40)
);

CREATE TABLE warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    name         VARCHAR(50) NOT NULL UNIQUE,
    location     VARCHAR(100)
);

CREATE TABLE product (
    product_id  SERIAL PRIMARY KEY,
    name        VARCHAR(80)   NOT NULL,
    unit_price  NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    min_stock   INTEGER       NOT NULL DEFAULT 0 CHECK (min_stock >= 0),
    category_id INTEGER       NOT NULL REFERENCES category (category_id),
    supplier_id INTEGER       REFERENCES supplier (supplier_id)
);

CREATE TABLE stock_movement (
    movement_id   SERIAL PRIMARY KEY,
    product_id    INTEGER     NOT NULL REFERENCES product (product_id),
    warehouse_id  INTEGER     NOT NULL REFERENCES warehouse (warehouse_id),
    user_id       INTEGER     NOT NULL REFERENCES app_user (user_id),
    movement_type VARCHAR(3)  NOT NULL CHECK (movement_type IN ('IN', 'OUT')),
    quantity      INTEGER     NOT NULL CHECK (quantity > 0),
    movement_date TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note          VARCHAR(200)
);
