INSERT INTO customers
(customer_id, age, gender, city, segment, total_orders, total_spent, aov, last_purchase)
VALUES
('C001', 22, 'F', 'Jaipur', 'STUDENT', 5, 4500, 900, '2026-08-20'),
('C002', 28, 'M', 'Delhi', 'REGULAR', 8, 9200, 1150, '2026-08-22'),
('C003', 35, 'F', 'Mumbai', 'PREMIUM', 12, 18500, 1541.67, '2026-08-25'),
('C004', 24, 'M', 'Bangalore', 'STUDENT', 3, 2100, 700, '2026-08-18'),
('C005', 31, 'F', 'Hyderabad', 'REGULAR', 7, 7800, 1114.29, '2026-08-23');

INSERT INTO products
(product_id, name, category, price, cost, stock)
VALUES
('P001', 'Wireless Headphones', 'Electronics', 2999, 1800, 50),
('P002', 'Smart Watch', 'Electronics', 4999, 3000, 35),
('P003', 'Laptop Backpack', 'Accessories', 1499, 800, 100),
('P004', 'Running Shoes', 'Fashion', 3499, 2000, 60),
('P005', 'Bluetooth Speaker', 'Electronics', 1999, 1100, 75);

INSERT INTO experiments
(
    experiment_id,
    name,
    hypothesis,
    objective,
    target_segment,
    control_description,
    variant_a_description,
    variant_b_description,
    status,
    budget
)
VALUES
(
    'EXP001',
    'Discount vs Free Shipping',
    'Different incentives will increase customer conversion.',
    'Increase conversion rate and revenue.',
    'STUDENT',
    'No additional offer',
    '10% discount',
    'Free shipping',
    'RUNNING',
    10000
);

INSERT INTO experiment_assignments
(experiment_id, customer_id, "group")
VALUES
('EXP001', 'C001', 'CONTROL'),
('EXP001', 'C002', 'VARIANT_A'),
('EXP001', 'C003', 'VARIANT_B'),
('EXP001', 'C004', 'CONTROL'),
('EXP001', 'C005', 'VARIANT_A');

INSERT INTO experiment_results
(
    experiment_id,
    "group",
    users,
    conversions,
    conversion_rate,
    revenue,
    aov,
    revenue_per_user
)
VALUES
('EXP001', 'CONTROL', 2, 1, 0.5000, 2999, 2999, 1499.50),
('EXP001', 'VARIANT_A', 2, 2, 1.0000, 8998, 4499, 4499),
('EXP001', 'VARIANT_B', 1, 1, 1.0000, 4999, 4999, 4999);

INSERT INTO transactions
(transaction_id, customer_id, product_id, quantity, price, discount, revenue, timestamp)
VALUES
('T001', 'C001', 'P001', 1, 2999, 0, 2999, '2026-08-20 10:30:00'),
('T002', 'C002', 'P002', 1, 4999, 500, 4499, '2026-08-22 14:15:00'),
('T003', 'C003', 'P003', 2, 1499, 0, 2998, '2026-08-25 16:20:00'),
('T004', 'C004', 'P004', 1, 3499, 500, 2999, '2026-08-18 11:45:00'),
('T005', 'C005', 'P005', 2, 1999, 0, 3998, '2026-08-23 19:10:00');

INSERT INTO ai_actions
(
    experiment_id,
    action_type,
    description,
    reason,
    expected_impact,
    status
)
VALUES
(
    'EXP001',
    'OPTIMIZE_EXPERIMENT',
    'Increase traffic allocation to Variant A.',
    'Variant A is showing higher conversion and revenue.',
    'Potential increase in conversion rate and revenue.',
    'PROPOSED'
);

