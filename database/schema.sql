-- ============================================
-- GROWTHPILOT DATABASE SCHEMA
-- ============================================

-- 1. CUSTOMERS
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    age INTEGER,
    gender VARCHAR(20),
    city VARCHAR(100),
    segment VARCHAR(50),
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    aov DECIMAL(12,2) DEFAULT 0,
    last_purchase TIMESTAMP
);


-- 2. PRODUCTS
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(12,2) NOT NULL,
    cost DECIMAL(12,2) NOT NULL,
    stock INTEGER DEFAULT 0
);


-- 3. EXPERIMENTS
CREATE TABLE experiments (
    experiment_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    hypothesis TEXT,
    objective TEXT,
    target_segment VARCHAR(100),
    control_description TEXT,
    variant_a_description TEXT,
    variant_b_description TEXT,
    status VARCHAR(50) DEFAULT 'DRAFT',
    budget DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 4. TRANSACTIONS
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    discount DECIMAL(12,2) DEFAULT 0,
    revenue DECIMAL(12,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


-- 5. EXPERIMENT ASSIGNMENTS
CREATE TABLE experiment_assignments (
    experiment_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    "group" VARCHAR(50) NOT NULL,

    PRIMARY KEY (experiment_id, customer_id),

    FOREIGN KEY (experiment_id)
        REFERENCES experiments(experiment_id),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


-- 6. EXPERIMENT RESULTS
CREATE TABLE experiment_results (
    experiment_id VARCHAR(50) NOT NULL,
    "group" VARCHAR(50) NOT NULL,
    users INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(8,4) DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0,
    aov DECIMAL(12,2) DEFAULT 0,
    revenue_per_user DECIMAL(12,2) DEFAULT 0,

    PRIMARY KEY (experiment_id, "group"),

    FOREIGN KEY (experiment_id)
        REFERENCES experiments(experiment_id)
);


-- 7. AI ACTIONS
CREATE TABLE ai_actions (
    action_id SERIAL PRIMARY KEY,
    experiment_id VARCHAR(50),
    action_type VARCHAR(100) NOT NULL,
    description TEXT,
    reason TEXT,
    expected_impact TEXT,
    status VARCHAR(50) DEFAULT 'PROPOSED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (experiment_id)
        REFERENCES experiments(experiment_id)
);