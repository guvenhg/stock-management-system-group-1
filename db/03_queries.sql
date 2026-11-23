-- Stock Management System - example queries

-- Query 1 (JOIN): list every stock movement together with the product,
-- the warehouse and the user who recorded it.
SELECT m.movement_id,
       p.name      AS product,
       w.name      AS warehouse,
       u.full_name AS recorded_by,
       m.movement_type,
       m.quantity,
       m.movement_date
FROM stock_movement m
JOIN product   p ON p.product_id   = m.product_id
JOIN warehouse w ON w.warehouse_id = m.warehouse_id
JOIN app_user  u ON u.user_id      = m.user_id
ORDER BY m.movement_date, m.movement_id;

-- Query 2 (GROUP BY / ORDER BY): current stock quantity of every product,
-- calculated from the IN and OUT movements, lowest stock first.
SELECT p.name AS product,
       SUM(CASE WHEN m.movement_type = 'IN' THEN m.quantity
                ELSE -m.quantity END) AS current_stock
FROM product p
JOIN stock_movement m ON m.product_id = p.product_id
GROUP BY p.product_id, p.name
ORDER BY current_stock, p.name;

-- Query 3 (SUBQUERY): products that are more expensive than the average
-- product price.
SELECT name, unit_price
FROM product
WHERE unit_price > (SELECT AVG(unit_price) FROM product)
ORDER BY unit_price DESC;
