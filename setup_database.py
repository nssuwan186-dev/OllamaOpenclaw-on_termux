"""
setup_database.py
สร้างฐานข้อมูล hotel_account.db พร้อมโครงสร้างตารางและข้อมูลเริ่มต้น
สำหรับระบบ OpenClaw Hotel Accounting
"""

import sqlite3
import os

# ปรับ Path ให้ตรงกับ Workspace ของ OpenClaw
DB_DIR = "/data/data/com.termux/files/home/.openclaw/workspace"
DB_PATH = os.path.join(DB_DIR, "hotel_account.db")

os.makedirs(DB_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# =============================
# 1. ตารางห้องพัก (rooms)
# =============================
c.execute("""
CREATE TABLE IF NOT EXISTS rooms (
    room_number     TEXT PRIMARY KEY,
    building        TEXT NOT NULL,
    floor           INTEGER NOT NULL,
    room_type       TEXT NOT NULL,
    price_per_night INTEGER NOT NULL,
    price_monthly   INTEGER DEFAULT NULL,
    status          TEXT DEFAULT 'ว่าง',
    note            TEXT DEFAULT ''
)
""")

# นำเข้าข้อมูลห้องพัก
rooms_data = [
    ('A101','A',1,'Standard',400,None,'ว่าง',''),
    ('A102','A',1,'Standard',400,None,'ว่าง',''),
    ('A103','A',1,'Standard',400,None,'ว่าง',''),
    ('A104','A',1,'Standard',400,None,'ว่าง',''),
    ('A105','A',1,'Standard',400,None,'ว่าง',''),
    ('A106','A',1,'Standard Twin',500,None,'ว่าง',''),
    ('A107','A',1,'Standard Twin',500,None,'ว่าง',''),
    ('A108','A',1,'Standard Twin',500,None,'ว่าง',''),
    ('A109','A',1,'Standard Twin',500,None,'ว่าง',''),
    ('A110','A',1,'Standard Twin',500,None,'ว่าง',''),
    ('A111','A',1,'Standard',400,None,'ว่าง',''),
    ('A201','A',2,'Standard',400,None,'ปิดปรับปรุง','ปิดปรับปรุง'),
    ('A202','A',2,'Standard',400,None,'ว่าง',''),
    ('A203','A',2,'Standard',400,None,'ว่าง',''),
    ('A204','A',2,'Standard',400,3500,'ไม่ว่าง','เช่ารายเดือน'),
    ('A205','A',2,'Standard',400,3500,'ไม่ว่าง','เช่ารายเดือน'),
    ('A206','A',2,'Standard',400,3500,'ไม่ว่าง','เช่ารายเดือน'),
    ('A207','A',2,'Standard',400,None,'ว่าง',''),
    ('A208','A',2,'Standard',400,3500,'ไม่ว่าง','เช่ารายเดือน'),
    ('A209','A',2,'Standard',400,None,'ว่าง',''),
    ('A210','A',2,'Standard',400,None,'ว่าง',''),
    ('A211','A',2,'Standard',400,3500,'ไม่ว่าง','เช่ารายเดือน'),
    ('B101','B',1,'Standard',400,None,'ว่าง',''),
    ('B102','B',1,'Standard',400,None,'ว่าง',''),
    ('B103','B',1,'Standard',400,None,'ว่าง',''),
    ('B104','B',1,'Standard',400,None,'ว่าง',''),
    ('B105','B',1,'Standard',400,None,'ว่าง',''),
    ('B106','B',1,'Standard',400,None,'ว่าง',''),
    ('B107','B',1,'Standard',400,None,'ว่าง',''),
    ('B108','B',1,'Standard',400,None,'ว่าง',''),
    ('B109','B',1,'Standard',400,None,'ว่าง',''),
    ('B110','B',1,'Standard',400,None,'ว่าง',''),
    ('B111','B',1,'Standard Twin',500,None,'ว่าง',''),
    ('B201','B',2,'Standard',400,None,'ว่าง',''),
    ('B202','B',2,'Standard',400,None,'ว่าง',''),
    ('B203','B',2,'Standard',400,None,'ว่าง',''),
    ('B204','B',2,'Standard',400,None,'ว่าง',''),
    ('B205','B',2,'Standard',400,None,'ว่าง',''),
    ('B206','B',2,'Standard',400,None,'ว่าง',''),
    ('B207','B',2,'Standard',400,None,'ว่าง',''),
    ('B208','B',2,'Standard',400,None,'ว่าง',''),
    ('B209','B',2,'Standard',400,None,'ว่าง',''),
    ('B210','B',2,'Standard',400,None,'ว่าง',''),
    ('B211','B',2,'Standard',400,None,'ว่าง',''),
    ('N1','N',1,'Standard Twin',600,None,'ว่าง',''),
    ('N2','N',1,'Standard',500,None,'ว่าง',''),
    ('N3','N',1,'Standard',500,None,'ว่าง',''),
    ('N4','N',1,'Standard Twin',600,None,'ว่าง',''),
    ('N5','N',1,'Standard Twin',600,None,'ว่าง',''),
    ('N6','N',1,'Standard Twin',600,None,'ว่าง',''),
    ('N7','N',1,'Standard',500,None,'ว่าง',''),
]
c.executemany("""
    INSERT OR IGNORE INTO rooms VALUES (?,?,?,?,?,?,?,?)
""", rooms_data)

# =============================
# 2. ตารางลูกค้า (customers)
# =============================
c.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id     TEXT PRIMARY KEY,
    customer_name   TEXT NOT NULL,
    phone           TEXT DEFAULT '',
    address         TEXT DEFAULT '',
    nationality     TEXT DEFAULT 'ไทย',
    id_card         TEXT DEFAULT '',
    passport_id     TEXT DEFAULT '',
    created_at      TEXT DEFAULT (datetime('now'))
)
""")

# =============================
# 3. ตารางลูกค้า MASTER (master_customers)
# =============================
c.execute("""
CREATE TABLE IF NOT EXISTS master_customers (
    master_id       TEXT PRIMARY KEY,
    full_name       TEXT NOT NULL,
    address         TEXT DEFAULT '',
    id_card         TEXT DEFAULT '',
    source          TEXT DEFAULT '',
    created_at      TEXT DEFAULT (datetime('now'))
)
""")

# =============================
# 4. ตารางการจอง (bookings)
# =============================
c.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    booking_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number     TEXT NOT NULL,
    customer_id     TEXT,
    customer_name   TEXT DEFAULT '',
    check_in_date   TEXT NOT NULL,
    nights          INTEGER DEFAULT 1,
    channel         TEXT DEFAULT 'เงินสด',
    service_fee     INTEGER DEFAULT 0,
    deposit         INTEGER DEFAULT 0,
    note            TEXT DEFAULT '',
    created_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (room_number) REFERENCES rooms(room_number)
)
""")

# =============================
# 5. ตารางรายรับ-รายจ่าย (transactions)
# =============================
c.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,
    item_name       TEXT NOT NULL,
    phone           TEXT DEFAULT '',
    room            TEXT DEFAULT '',
    nights          INTEGER DEFAULT 0,
    expense         INTEGER DEFAULT 0,
    income          INTEGER DEFAULT 0,
    balance         INTEGER DEFAULT 0,
    deposit_cash    INTEGER DEFAULT 0,
    note            TEXT DEFAULT '',
    category        TEXT DEFAULT 'ทั่วไป',
    created_at      TEXT DEFAULT (datetime('now'))
)
""")

# บันทึกยอดยกมา
c.execute("""
    INSERT OR IGNORE INTO transactions (date, item_name, expense, income, balance, note, category)
    VALUES ('2568-12-01', 'ยอดยกมา', 0, 4037, 4037, 'ยอดยกมาต้นเดือน ธ.ค. 2568', 'ยกมา')
""")

# =============================
# 6. ตารางพนักงาน (employees)
# =============================
c.execute("""
CREATE TABLE IF NOT EXISTS employees (
    emp_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT NOT NULL,
    position        TEXT NOT NULL,
    pay_type        TEXT NOT NULL,
    salary          INTEGER NOT NULL,
    bank_name       TEXT DEFAULT '',
    bank_account    TEXT DEFAULT '',
    active          INTEGER DEFAULT 1
)
""")

employees_data = [
    ('ณัฐภัทร สุวรรณโส','บัญชี','รายเดือน',6000,'ธ.กสิกรไทย',''),
    ('สุพัตรา มาลัยเพิ่ม','แม่บ้าน','รายเดือน',7000,'ธ.กรุงเทพ',''),
    ('พิกุล สึกชัย','แม่บ้าน','รายวัน',320,'ธ.กรุงเทพ',''),
    ('พงษ์เพชร กนันารัตน์','คนสวน','รายวัน',400,'ธ.กรุงเทพ',''),
    ('สุพจน์ นาคเสน','รปภ.','รายวัน',400,'ธ.กรุงเทพ',''),
]
c.executemany("""
    INSERT OR IGNORE INTO employees (full_name, position, pay_type, salary, bank_name, bank_account)
    VALUES (?,?,?,?,?,?)
""", employees_data)

# =============================
# 7. ตารางสรุปรายเดือน (monthly_summary)
# =============================
c.execute("""
CREATE TABLE IF NOT EXISTS monthly_summary (
    summary_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    year            INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    total_income    INTEGER DEFAULT 0,
    total_expense   INTEGER DEFAULT 0,
    net_profit      INTEGER DEFAULT 0,
    total_bookings  INTEGER DEFAULT 0,
    note            TEXT DEFAULT '',
    UNIQUE(year, month)
)
""")

conn.commit()
conn.close()

print("✅ สร้างฐานข้อมูล hotel_account.db สำเร็จ!")
print(f"📁 ตำแหน่งไฟล์: {DB_PATH}")
print("📊 ตารางที่สร้าง: rooms, customers, master_customers, bookings, transactions, employees, monthly_summary")
