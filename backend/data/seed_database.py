"""Generate the sample SQLite database used in this tutorial.

Run it with:

    uv run data/seed_database.py        (or: python data/seed_database.py)

It creates data/sales.db: two years (2024-2025) of orders for "BrightCart",
a fictional retailer. The data is random but SEEDED, so everybody who runs
this script gets exactly the same database and the same numbers.

Only the Python standard library is used - no extra packages needed.
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "sales.db"
rng = random.Random(402)  # fixed seed -> same data every time

# --------------------------------------------------------------------------
# 1. Reference data
# --------------------------------------------------------------------------

# category -> [(product name, list price, cost to us)]
PRODUCTS = {
    "Electronics": [
        ("Wireless Earbuds", 79.00, 41.00),
        ("Bluetooth Speaker", 59.00, 30.00),
        ("Smart Watch", 199.00, 118.00),
        ("USB-C Charging Hub", 45.00, 19.00),
        ("Noise-Cancelling Headphones", 249.00, 142.00),
        ("Portable Power Bank", 39.00, 17.00),
    ],
    "Home & Kitchen": [
        ("Air Fryer", 129.00, 72.00),
        ("Pour-Over Coffee Set", 49.00, 21.00),
        ("Cast Iron Skillet", 42.00, 18.00),
        ("Robot Vacuum", 289.00, 176.00),
        ("Insulated Water Bottle", 28.00, 9.50),
        ("Bamboo Cutting Board", 24.00, 8.00),
    ],
    "Office Supplies": [
        ("Ergonomic Office Chair", 219.00, 128.00),
        ("Standing Desk Converter", 179.00, 101.00),
        ("Notebook 5-Pack", 14.00, 4.50),
        ("Gel Pen Set", 9.00, 2.60),
        ("Desk Organizer", 22.00, 8.20),
        ("Laser Printer Paper (Case)", 38.00, 24.00),
    ],
    "Sports & Outdoors": [
        ("Yoga Mat", 32.00, 11.00),
        ("Adjustable Dumbbells", 159.00, 92.00),
        ("Trail Running Shoes", 119.00, 58.00),
        ("Camping Tent (2-Person)", 149.00, 81.00),
        ("Cycling Helmet", 69.00, 31.00),
        ("Resistance Band Set", 25.00, 7.50),
    ],
    "Toys & Games": [
        ("Building Blocks Set", 54.00, 26.00),
        ("Strategy Board Game", 44.00, 19.00),
        ("Remote Control Car", 64.00, 33.00),
        ("1000-Piece Puzzle", 19.00, 6.80),
        ("Kids Science Kit", 36.00, 15.00),
        ("Plush Bear", 21.00, 7.20),
    ],
}

# How often each category shows up in an order line (relative weight).
CATEGORY_WEIGHT = {
    "Electronics": 0.27,
    "Home & Kitchen": 0.22,
    "Office Supplies": 0.23,
    "Sports & Outdoors": 0.16,
    "Toys & Games": 0.12,
}

# region -> (share of customers, cities)
REGIONS = {
    "West": (0.33, ["Westhaven", "Goldridge", "Redwood Falls"]),
    "East": (0.27, ["Eastbrook", "Harborview", "Maplewood"]),
    "North": (0.22, ["Northfield", "Pinecrest", "Frostburg"]),
    "South": (0.18, ["Southport", "Palm Bay", "Magnolia"]),
}

SEGMENT_WEIGHT = {"Consumer": 0.62, "Small Business": 0.26, "Corporate": 0.12}

FIRST_NAMES = [
    "Alex", "Maria", "James", "Sofia", "Daniel", "Grace", "Miguel", "Hannah",
    "Noah", "Chloe", "Ethan", "Isabella", "Lucas", "Amara", "Kenji", "Priya",
    "Omar", "Elena", "Mateo", "Zoe", "Liam", "Aisha", "Gabriel", "Nina",
    "Rafael", "Emma", "Diego", "Leah", "Samuel", "Bianca",
]
LAST_NAMES = [
    "Reyes", "Santos", "Cruz", "Garcia", "Kim", "Nguyen", "Patel", "Smith",
    "Johnson", "Lee", "Brown", "Martinez", "Davis", "Lopez", "Wilson", "Tan",
    "Anderson", "Thomas", "Moore", "Clark", "Lewis", "Walker", "Young", "Hall",
    "Torres", "Rivera", "Flores", "Ramos", "Mendoza", "Castillo",
]
COMPANY_WORDS_A = [
    "Summit", "Blue Harbor", "Evergreen", "Brightside", "Ironwood", "Lakeshore",
    "Pioneer", "Golden Gate", "Silverline", "Red Maple", "Clearwater", "Northstar",
    "Cedar", "Atlas", "Horizon", "Keystone", "Sunrise", "Granite", "Coastal", "Vertex",
]
COMPANY_WORDS_B = {
    "Small Business": ["Cafe", "Studio", "Bakery", "Fitness", "Books", "Design Co.", "Clinic", "Workshop"],
    "Corporate": ["Holdings", "Logistics", "Industries", "Technologies", "Group", "Partners", "Systems"],
}

# Seasonality: how busy each month is compared to an average month.
MONTH_WEIGHT = {1: 0.85, 2: 0.80, 3: 0.90, 4: 0.95, 5: 1.00, 6: 0.95,
                7: 0.90, 8: 1.00, 9: 1.00, 10: 1.10, 11: 1.40, 12: 1.55}
# Growth: 2025 is busier than 2024.
YEAR_WEIGHT = {2024: 1.00, 2025: 1.22}

ORDERS_PER_AVERAGE_DAY = 6.4  # controls the size of the database
NUM_CUSTOMERS = 320


def weighted_choice(weights: dict):
    """Pick one key from a {key: weight} dictionary."""
    keys = list(weights)
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


# --------------------------------------------------------------------------
# 2. Create the tables
# --------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    unit_price   REAL NOT NULL,   -- list price in USD
    unit_cost    REAL NOT NULL    -- what the product costs BrightCart
);

CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment       TEXT NOT NULL,  -- Consumer | Small Business | Corporate
    region        TEXT NOT NULL,  -- North | South | East | West
    city          TEXT NOT NULL,
    signup_date   TEXT NOT NULL   -- YYYY-MM-DD
);

CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date  TEXT NOT NULL,    -- YYYY-MM-DD
    channel     TEXT NOT NULL,    -- Online | Retail Store | Wholesale
    status      TEXT NOT NULL     -- Completed | Returned | Cancelled
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL,
    unit_price    REAL NOT NULL,  -- price actually charged per unit, after discount
    discount_pct  REAL NOT NULL   -- 0, 5, 10, 15 or 20
);

CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_items_order ON order_items(order_id);

-- A ready-to-use reporting view: one row per order line of COMPLETED orders,
-- with customer and product details already joined in.
CREATE VIEW sales AS
SELECT
    o.order_id,
    o.order_date,
    substr(o.order_date, 1, 4) AS order_year,    -- '2024' or '2025'
    substr(o.order_date, 1, 7) AS order_month,   -- e.g. '2025-03'
    o.channel,
    c.customer_id,
    c.customer_name,
    c.segment,
    c.region,
    c.city,
    p.product_id,
    p.product_name,
    p.category,
    oi.quantity,
    ROUND(oi.quantity * oi.unit_price, 2)                 AS revenue,
    ROUND(oi.quantity * p.unit_cost, 2)                   AS cost,
    ROUND(oi.quantity * (oi.unit_price - p.unit_cost), 2) AS profit
FROM order_items oi
JOIN orders    o ON o.order_id    = oi.order_id
JOIN customers c ON c.customer_id = o.customer_id
JOIN products  p ON p.product_id  = oi.product_id
WHERE o.status = 'Completed';
"""


# --------------------------------------------------------------------------
# 3. Generate the rows
# --------------------------------------------------------------------------

def make_products():
    rows, product_id = [], 1
    for category, items in PRODUCTS.items():
        for name, price, cost in items:
            rows.append((product_id, name, category, price, cost))
            product_id += 1
    return rows


def make_customers():
    rows, used_names = [], set()
    region_weights = {region: share for region, (share, _) in REGIONS.items()}
    for customer_id in range(1, NUM_CUSTOMERS + 1):
        segment = weighted_choice(SEGMENT_WEIGHT)
        region = weighted_choice(region_weights)
        city = rng.choice(REGIONS[region][1])
        while True:  # keep trying until the name is unique
            if segment == "Consumer":
                name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            else:
                name = f"{rng.choice(COMPANY_WORDS_A)} {rng.choice(COMPANY_WORDS_B[segment])}"
            if name not in used_names:
                used_names.add(name)
                break
        signup = date(2022, 1, 1) + timedelta(days=rng.randint(0, 729))  # 2022-2023
        rows.append((customer_id, name, segment, region, city, signup.isoformat()))
    return rows


def make_orders(products, customers):
    """Walk through every day of 2024-2025 and create that day's orders."""
    by_category = {}
    for product in products:
        by_category.setdefault(product[2], []).append(product)

    # Business customers order more often than consumers.
    order_frequency = {"Consumer": 1.0, "Small Business": 1.8, "Corporate": 2.4}
    customer_weights = [order_frequency[c[2]] for c in customers]

    orders, items = [], []
    order_id = item_id = 1
    day = date(2024, 1, 1)
    while day <= date(2025, 12, 31):
        expected = ORDERS_PER_AVERAGE_DAY * MONTH_WEIGHT[day.month] * YEAR_WEIGHT[day.year]
        if day.weekday() >= 5:  # weekends are a little busier
            expected *= 1.15
        orders_today = max(0, round(rng.gauss(expected, expected * 0.25)))

        for _ in range(orders_today):
            customer = rng.choices(customers, weights=customer_weights, k=1)[0]
            customer_id, _, segment, region, _, _ = customer

            # Sales channel depends on the kind of customer. Online grows in 2025.
            online_boost = 0.08 if day.year == 2025 else 0.0
            if segment == "Consumer":
                channel_weights = {"Online": 0.58 + online_boost, "Retail Store": 0.42 - online_boost}
            elif segment == "Small Business":
                channel_weights = {"Online": 0.47 + online_boost, "Retail Store": 0.28 - online_boost, "Wholesale": 0.25}
            else:
                channel_weights = {"Online": 0.40, "Wholesale": 0.60}
            channel = weighted_choice(channel_weights)

            status = weighted_choice({"Completed": 0.92, "Returned": 0.05, "Cancelled": 0.03})
            orders.append((order_id, customer_id, day.isoformat(), channel, status))

            # 1 to 4 different products per order
            chosen = set()
            for _ in range(rng.choices([1, 2, 3, 4], weights=[0.45, 0.30, 0.17, 0.08], k=1)[0]):
                category_weights = dict(CATEGORY_WEIGHT)
                if day.month in (11, 12):   # holiday season
                    category_weights["Toys & Games"] *= 2.2
                    category_weights["Electronics"] *= 1.3
                if region == "South":       # warm weather -> more outdoor gear
                    category_weights["Sports & Outdoors"] *= 1.5
                product = rng.choice(by_category[weighted_choice(category_weights)])
                product_id, _, _, list_price, _ = product
                if product_id in chosen:
                    continue
                chosen.add(product_id)

                if channel == "Wholesale":  # bulk orders with a bigger discount
                    quantity = rng.randint(3, 9)
                    discount = rng.choice([10, 15, 20])
                else:
                    quantity = rng.choices([1, 2, 3], weights=[0.70, 0.22, 0.08], k=1)[0]
                    discount = rng.choices([0, 5, 10, 15], weights=[0.60, 0.18, 0.15, 0.07], k=1)[0]
                charged = round(list_price * (1 - discount / 100), 2)
                items.append((item_id, order_id, product_id, quantity, charged, discount))
                item_id += 1
            order_id += 1
        day += timedelta(days=1)
    return orders, items


# --------------------------------------------------------------------------
# 4. Write everything to data/sales.db
# --------------------------------------------------------------------------

def main():
    DB_PATH.unlink(missing_ok=True)  # always start from an empty file

    products = make_products()
    customers = make_customers()
    orders, items = make_orders(products, customers)

    connection = sqlite3.connect(DB_PATH)
    connection.executescript(SCHEMA)
    connection.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
    connection.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)", customers)
    connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)
    connection.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)", items)
    connection.commit()

    print(f"Created {DB_PATH}")
    for table in ("products", "customers", "orders", "order_items", "sales"):
        count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<12} {count:>6,} rows")
    revenue = connection.execute("SELECT SUM(revenue) FROM sales").fetchone()[0]
    print(f"  total revenue (completed orders): ${revenue:,.2f}")
    connection.close()


if __name__ == "__main__":
    main()
