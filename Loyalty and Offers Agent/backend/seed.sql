
CREATE DATABASE IF NOT EXISTS retail_agent;
USE retail_agent;


DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS promotions;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;


CREATE TABLE customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(150),
  loyalty_points INT DEFAULT 0,
  tier ENUM('BRONZE','SILVER','GOLD') DEFAULT 'BRONZE'
);

INSERT INTO customers (name, email, loyalty_points, tier) VALUES
('Bronze User','bronze@example.com',30,'BRONZE'),
('Silver User','silver@example.com',200,'SILVER'),
('Gold User','gold@example.com',800,'GOLD');


CREATE TABLE products (
  sku VARCHAR(50) PRIMARY KEY,
  name VARCHAR(200),
  category VARCHAR(100),
  price DECIMAL(10,2)
);

INSERT INTO products (sku, name, category, price) VALUES
('YOGA100','Yoga Mat','fitness',999.00),
('DUMB25','Dumbbell 2.5kg','fitness',499.00),
('PROTEIN1','Protein Powder 1kg','fitness',1499.00),
('PBAR50','Protein Bar','snacks',125.00),
('ENERGY10','Electrolyte Drink','nutrition',75.00);


CREATE TABLE inventory (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(50),
  store VARCHAR(100),
  stock INT,
  FOREIGN KEY (sku) REFERENCES products(sku)
);

INSERT INTO inventory (sku, store, stock) VALUES
('PBAR50','Chennai Mall',150), 
('PBAR50','OMR Store',40),

('YOGA100','Chennai Mall',10),
('DUMB25','OMR Store',6),
('PROTEIN1','Chennai Mall',3),
('PROTEIN1','OMR Store',2);


CREATE TABLE promotions (
  code VARCHAR(50) PRIMARY KEY,
  type ENUM('PERCENT','FLAT','BOGO'),
  value DECIMAL(10,2),
  category_restriction VARCHAR(100),
  min_cart_value DECIMAL(10,2),
  expires_at DATETIME
);

INSERT INTO promotions (code,type,value,category_restriction,min_cart_value,expires_at) VALUES
('FIT30','PERCENT',30.0,'fitness',0,'2099-12-31'),
('CART20','PERCENT',20.0,NULL,1000,'2099-12-31'),
('PBAR49','FLAT',49.0,'snacks',0,'2099-12-31');


CREATE TABLE carts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);


CREATE TABLE cart_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cart_id INT,
  sku VARCHAR(50),
  qty INT,
  price_at_add DECIMAL(10,2),
  FOREIGN KEY (cart_id) REFERENCES carts(id),
  FOREIGN KEY (sku) REFERENCES products(sku)
);


INSERT INTO carts (customer_id) VALUES (1);
SET @cart1 = LAST_INSERT_ID();
INSERT INTO cart_items (cart_id, sku, qty, price_at_add) VALUES
(@cart1, 'YOGA100', 1, 999.00),
(@cart1, 'PBAR50', 2, 125.00);


INSERT INTO carts (customer_id) VALUES (2);
SET @cart2 = LAST_INSERT_ID();
INSERT INTO cart_items (cart_id, sku, qty, price_at_add) VALUES
(@cart2, 'DUMB25', 2, 499.00),
(@cart2, 'PBAR50', 3, 125.00),
(@cart2, 'PROTEIN1', 1, 1499.00);


INSERT INTO carts (customer_id) VALUES (3);
SET @cart3 = LAST_INSERT_ID();
INSERT INTO cart_items (cart_id, sku, qty, price_at_add) VALUES
(@cart3, 'PROTEIN1', 2, 1499.00),
(@cart3, 'YOGA100', 1, 999.00),
(@cart3, 'PBAR50', 5, 125.00);
