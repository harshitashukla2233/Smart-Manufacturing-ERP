CREATE TABLE products (
 product_id VARCHAR(20) PRIMARY KEY, product_name VARCHAR(100) NOT NULL,
 product_type VARCHAR(30) NOT NULL, base_uom VARCHAR(10) NOT NULL,
 procurement_type VARCHAR(10) NOT NULL CHECK (procurement_type IN ('MAKE','BUY')),
 lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 0), active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE work_centres (
 work_centre_id VARCHAR(20) PRIMARY KEY, work_centre_name VARCHAR(100) NOT NULL,
 machine_type VARCHAR(50) NOT NULL, available_hours_per_day NUMERIC(6,2) NOT NULL CHECK (available_hours_per_day > 0),
 efficiency_pct NUMERIC(5,2) NOT NULL CHECK (efficiency_pct BETWEEN 0 AND 100), active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE bom (
 bom_id BIGSERIAL PRIMARY KEY, parent_product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
 component_product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
 quantity_per NUMERIC(12,4) NOT NULL CHECK (quantity_per > 0), uom VARCHAR(10) NOT NULL,
 scrap_factor_pct NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (scrap_factor_pct BETWEEN 0 AND 100),
 valid_from DATE NOT NULL, revision VARCHAR(10) NOT NULL,
 CHECK (parent_product_id <> component_product_id),
 UNIQUE(parent_product_id, component_product_id, revision)
);
CREATE TABLE routing (
 routing_id BIGSERIAL PRIMARY KEY, product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
 operation_no INTEGER NOT NULL, operation_name VARCHAR(100) NOT NULL,
 work_centre_id VARCHAR(20) NOT NULL REFERENCES work_centres(work_centre_id),
 setup_time_min NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (setup_time_min >= 0),
 processing_time_min_per_unit NUMERIC(10,2) NOT NULL CHECK (processing_time_min_per_unit >= 0),
 sequence INTEGER NOT NULL, UNIQUE(product_id, operation_no), UNIQUE(product_id, sequence)
);
CREATE TABLE inventory (
 inventory_id BIGSERIAL PRIMARY KEY, product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
 storage_location VARCHAR(30) NOT NULL, on_hand_qty NUMERIC(14,3) NOT NULL CHECK (on_hand_qty >= 0),
 reserved_qty NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (reserved_qty >= 0),
 safety_stock_qty NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (safety_stock_qty >= 0),
 uom VARCHAR(10) NOT NULL, as_of_date DATE NOT NULL,
 CHECK (reserved_qty <= on_hand_qty), UNIQUE(product_id, storage_location, as_of_date)
);
CREATE TABLE production_orders (
 production_order_id VARCHAR(20) PRIMARY KEY, product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
 order_qty NUMERIC(14,3) NOT NULL CHECK (order_qty > 0), due_date DATE NOT NULL,
 priority VARCHAR(10) NOT NULL CHECK (priority IN ('LOW','MEDIUM','HIGH')),
 status VARCHAR(20) NOT NULL CHECK (status IN ('PLANNED','RELEASED','IN_PROGRESS','COMPLETED','CANCELLED'))
);
