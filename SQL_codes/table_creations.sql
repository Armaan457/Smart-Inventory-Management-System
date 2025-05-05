CREATE TABLE Suppliers (
    supplier_id NUMBER PRIMARY KEY,
    name VARCHAR2(100) UNIQUE,
    location VARCHAR2(100),
    contact_info VARCHAR2(255)
);

CREATE TABLE Clusters (
    cluster_id NUMBER PRIMARY KEY,
    avg_quantity NUMBER,
    avg_price NUMBER(10,2),
    avg_sales NUMBER,
    avg_popularity_score NUMBER(3,2),
    category_distribution CLOB
);

CREATE TABLE Products (
    product_id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    category VARCHAR2(50),
    quantity NUMBER,
    price NUMBER(10,2),
    sales NUMBER,
    rating NUMBER(3,2),
    cluster_id NUMBER, 
    supplier_id NUMBER, 
    CONSTRAINT fk_product_cluster FOREIGN KEY (cluster_id) REFERENCES Clusters(cluster_id),
    CONSTRAINT fk_product_supplier FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
);

CREATE TABLE User_Data (
    user_id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    role VARCHAR2(50),
    password BLOB
);

CREATE TABLE Transactions (
    transaction_id NUMBER PRIMARY KEY,
    transaction_type VARCHAR2(50),
    quantity_change NUMBER,
    transaction_date DATE,
    product_id NUMBER,
    user_id NUMBER,
    CONSTRAINT fk_trans_product FOREIGN KEY (product_id) REFERENCES Products(product_id),
    CONSTRAINT fk_trans_user FOREIGN KEY (user_id) REFERENCES User_Data(user_id)
);

CREATE TABLE Inventory_Alerts (
    product_id NUMBER,
    alert_date DATE,
    alert_type VARCHAR2(50),
    message VARCHAR2(255),
    is_processed NUMBER(1) DEFAULT 0,
    PRIMARY KEY (product_id, alert_date), 
    CONSTRAINT fk_alert_product FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
