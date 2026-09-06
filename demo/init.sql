-- Schema
CREATE TABLE categories (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL);
CREATE TABLE regions (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL);
CREATE TABLE customers (id SERIAL PRIMARY KEY, name VARCHAR(150) NOT NULL, email VARCHAR(255) UNIQUE NOT NULL, region_id INT REFERENCES regions(id), created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE products (id SERIAL PRIMARY KEY, name VARCHAR(150) NOT NULL, category_id INT REFERENCES categories(id), price NUMERIC(10,2) NOT NULL);
CREATE TABLE orders (id SERIAL PRIMARY KEY, customer_id INT NOT NULL REFERENCES customers(id), order_date DATE NOT NULL, total_amount NUMERIC(12,2) NOT NULL);
CREATE TABLE order_items (id SERIAL PRIMARY KEY, order_id INT NOT NULL REFERENCES orders(id), product_id INT NOT NULL REFERENCES products(id), quantity INT NOT NULL, unit_price NUMERIC(10,2) NOT NULL);

-- Categories
INSERT INTO categories (name) VALUES ('Hardware'), ('Software'), ('Services'), ('Cloud'), ('Security'), ('Analytics'), ('Networking'), ('Storage');

-- Regions
INSERT INTO regions (name) VALUES ('North America'), ('Europe'), ('Asia Pacific'), ('Latin America'), ('Middle East'), ('Africa');

-- Customers (50)
INSERT INTO customers (name, email, region_id, created_at) VALUES
('Ava Patel','ava.patel@techcorp.com',1,'2024-03-15'),
('Noah Smith','noah.smith@dataflow.io',2,'2024-04-02'),
('Mia Chen','mia.chen@cloudnine.cn',3,'2024-05-18'),
('Liam Johnson','liam.j@megasys.com',1,'2024-06-01'),
('Sophia Williams','sophia.w@eurotech.de',2,'2024-06-22'),
('James Brown','james.b@innovate.co.uk',2,'2024-07-10'),
('Isabella Davis','isabella.d@westcoast.com',1,'2024-07-30'),
('Ethan Wilson','ethan.w@pacific.jp',3,'2024-08-15'),
('Charlotte Moore','charlotte.m@finserv.com',1,'2024-08-28'),
('Oliver Taylor','oliver.t@nordics.se',2,'2024-09-05'),
('Amelia Anderson','amelia.a@southtech.br',4,'2024-09-20'),
('Lucas Thomas','lucas.t@desert.ae',5,'2024-10-01'),
('Harper Jackson','harper.j@silicon.com',1,'2024-10-15'),
('Mason White','mason.w@berlintech.de',2,'2024-10-28'),
('Evelyn Harris','evelyn.h@tokyodata.jp',3,'2024-11-05'),
('Logan Martin','logan.m@lagos.ng',6,'2024-11-18'),
('Aria Thompson','aria.t@vancouver.ca',1,'2024-12-01'),
('Aiden Garcia','aiden.g@madrid.es',2,'2024-12-15'),
('Chloe Martinez','chloe.m@sydney.au',3,'2025-01-05'),
('Elijah Robinson','elijah.r@miami.com',1,'2025-01-18'),
('Luna Clark','luna.c@paris.fr',2,'2025-02-01'),
('Sebastian Lewis','seb.l@mumbai.in',3,'2025-02-15'),
('Mila Lee','mila.l@seoul.kr',3,'2025-03-01'),
('Jack Walker','jack.w@chicago.com',1,'2025-03-12'),
('Layla Hall','layla.h@london.co.uk',2,'2025-03-25'),
('Benjamin Allen','ben.a@houston.com',1,'2025-04-05'),
('Zoe Young','zoe.y@zurich.ch',2,'2025-04-18'),
('Henry King','henry.k@singapore.sg',3,'2025-05-01'),
('Penelope Wright','penny.w@boston.com',1,'2025-05-15'),
('Alexander Lopez','alex.l@mexico.mx',4,'2025-05-28'),
('Riley Hill','riley.h@toronto.ca',1,'2025-06-08'),
('Daniel Scott','daniel.s@amsterdam.nl',2,'2025-06-20'),
('Nora Green','nora.g@melbourne.au',3,'2025-07-01'),
('Matthew Adams','matt.a@dallas.com',1,'2025-07-15'),
('Lily Baker','lily.b@dublin.ie',2,'2025-07-28'),
('David Nelson','david.n@jakarta.id',3,'2025-08-05'),
('Stella Carter','stella.c@seattle.com',1,'2025-08-18'),
('Joseph Mitchell','joe.m@cairo.eg',5,'2025-09-01'),
('Hannah Roberts','hannah.r@denver.com',1,'2025-09-12'),
('Samuel Turner','sam.t@lisbon.pt',2,'2025-09-25'),
('Grace Phillips','grace.p@osaka.jp',3,'2025-10-05'),
('Carter Campbell','carter.c@atlanta.com',1,'2025-10-18'),
('Victoria Parker','vicky.p@rome.it',2,'2025-11-01'),
('Owen Evans','owen.e@bangkok.th',3,'2025-11-15'),
('Scarlett Edwards','scarlett.e@phoenix.com',1,'2025-11-28'),
('Dylan Collins','dylan.c@warsaw.pl',2,'2025-12-05'),
('Hazel Stewart','hazel.s@hanoi.vn',3,'2025-12-18'),
('Luke Sanchez','luke.s@saopaulo.br',4,'2026-01-05'),
('Violet Morris','violet.m@nairobi.ke',6,'2026-01-18'),
('Wyatt Rogers','wyatt.r@nyc.com',1,'2026-02-01');

-- Products (20)
INSERT INTO products (name, category_id, price) VALUES
('Analytics Suite Pro',6,499.00),
('Data Gateway X1',1,129.00),
('Advisory Hours Pack',3,180.00),
('CloudScale Platform',4,899.00),
('SecureVault Enterprise',5,649.00),
('NetFlow Monitor',7,299.00),
('StorageMax SSD 2TB',8,189.00),
('DevOps Toolkit',2,349.00),
('AI Insights Engine',6,1299.00),
('Firewall Pro 500',5,449.00),
('Wireless Access Point',7,159.00),
('Backup Cloud 10TB',8,399.00),
('CRM Integration Module',2,249.00),
('Server Rack Unit',1,2499.00),
('Compliance Auditor',5,599.00),
('Data Pipeline Builder',6,749.00),
('Managed IT Support',3,1200.00),
('Network Switch 48-Port',7,899.00),
('Edge Computing Node',1,1899.00),
('Training Workshop',3,350.00);

-- Generate orders and order_items across 2024-2026
-- 2024 orders (100 orders)
DO $$
DECLARE
  v_order_id INT;
  v_customer_id INT;
  v_product_id INT;
  v_qty INT;
  v_price NUMERIC;
  v_total NUMERIC;
  v_date DATE;
  v_items INT;
BEGIN
  FOR i IN 1..100 LOOP
    v_customer_id := (i % 50) + 1;
    v_date := '2024-01-01'::date + (random() * 364)::int;
    v_total := 0;
    INSERT INTO orders (customer_id, order_date, total_amount) VALUES (v_customer_id, v_date, 0) RETURNING id INTO v_order_id;
    v_items := 1 + (random() * 3)::int;
    FOR j IN 1..v_items LOOP
      v_product_id := 1 + (random() * 19)::int;
      v_qty := 1 + (random() * 4)::int;
      SELECT price INTO v_price FROM products WHERE id = v_product_id;
      INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (v_order_id, v_product_id, v_qty, v_price);
      v_total := v_total + (v_qty * v_price);
    END LOOP;
    UPDATE orders SET total_amount = v_total WHERE id = v_order_id;
  END LOOP;
END $$;

-- 2025 orders (200 orders — business grew)
DO $$
DECLARE
  v_order_id INT;
  v_customer_id INT;
  v_product_id INT;
  v_qty INT;
  v_price NUMERIC;
  v_total NUMERIC;
  v_date DATE;
  v_items INT;
BEGIN
  FOR i IN 1..200 LOOP
    v_customer_id := 1 + (random() * 49)::int;
    v_date := '2025-01-01'::date + (random() * 364)::int;
    v_total := 0;
    INSERT INTO orders (customer_id, order_date, total_amount) VALUES (v_customer_id, v_date, 0) RETURNING id INTO v_order_id;
    v_items := 1 + (random() * 4)::int;
    FOR j IN 1..v_items LOOP
      v_product_id := 1 + (random() * 19)::int;
      v_qty := 1 + (random() * 5)::int;
      SELECT price INTO v_price FROM products WHERE id = v_product_id;
      INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (v_order_id, v_product_id, v_qty, v_price);
      v_total := v_total + (v_qty * v_price);
    END LOOP;
    UPDATE orders SET total_amount = v_total WHERE id = v_order_id;
  END LOOP;
END $$;

-- 2026 orders (150 orders — YTD through August)
DO $$
DECLARE
  v_order_id INT;
  v_customer_id INT;
  v_product_id INT;
  v_qty INT;
  v_price NUMERIC;
  v_total NUMERIC;
  v_date DATE;
  v_items INT;
BEGIN
  FOR i IN 1..150 LOOP
    v_customer_id := 1 + (random() * 49)::int;
    v_date := '2026-01-01'::date + (random() * 243)::int;
    v_total := 0;
    INSERT INTO orders (customer_id, order_date, total_amount) VALUES (v_customer_id, v_date, 0) RETURNING id INTO v_order_id;
    v_items := 1 + (random() * 4)::int;
    FOR j IN 1..v_items LOOP
      v_product_id := 1 + (random() * 19)::int;
      v_qty := 1 + (random() * 5)::int;
      SELECT price INTO v_price FROM products WHERE id = v_product_id;
      INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (v_order_id, v_product_id, v_qty, v_price);
      v_total := v_total + (v_qty * v_price);
    END LOOP;
    UPDATE orders SET total_amount = v_total WHERE id = v_order_id;
  END LOOP;
END $$;
