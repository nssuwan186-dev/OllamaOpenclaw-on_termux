#!/usr/bin/env python3
"""
fix_database.py — แก้ไขปัญหาข้อมูลใน hotel_account.db
วิพัฒน์โฮเทล · OpenClaw System

ปัญหาที่แก้:
1. rooms.status ไม่ถูกต้อง
2. master_transactions column misalignment
3. เพิ่มข้อมูลเริ่มต้นใน income_table/expense_table
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

def connect():
    return sqlite3.connect(DB_PATH)

# ─────────────────────────────────────────────
# 1. แก้ไข rooms.status
# ─────────────────────────────────────────────
def fix_room_status():
    conn = connect()
    cur = conn.cursor()
    
    # ห้องปิดปรับปรุง
    cur.execute("UPDATE rooms SET status = 'Under Maintenance' WHERE room_no = 'A201'")
    
    # ห้องรายเดือน (ไม่ว่าง)
    monthly_rooms = ['A204', 'A205', 'A206', 'A208', 'A211']
    for room in monthly_rooms:
        cur.execute("UPDATE rooms SET status = 'Monthly' WHERE room_no = ?", (room,))
    
    conn.commit()
    print(f"✅ แก้ไข rooms.status สำเร็จ: A201=Under Maintenance, {monthly_rooms}=Monthly")
    conn.close()

# ─────────────────────────────────────────────
# 2. สร้าง clean_transactions จาก master_transactions
#    (แก้ column misalignment)
# ─────────────────────────────────────────────
def create_clean_transactions():
    conn = connect()
    
    # อ่านข้อมูลดิบ
    df = pd.read_sql("SELECT * FROM master_transactions", conn)
    
    # Column mapping จริง (ข้อมูลถูก shift):
    # Food_Bev = ยอดเงินจริง (Grand_Total)
    # Audit_Status = วิธีชำระ
    # Room_No, Room_Type = ถูกต้อง
    # Imported_At = ชื่อไฟล์ต้นทาง
    
    clean = pd.DataFrame({
        'trans_id':       df['Trans_ID'],
        'date':           df['Date'],
        'room_no':        df['Room_No'],
        'room_type':      df['Room_Type'],
        'guest_name':     df['Guest_Name'],
        'amount':         pd.to_numeric(df['Food_Bev'], errors='coerce').fillna(0),
        'payment_method': df['Audit_Status'],
        'source_file':    df['Imported_At'],
        'imported_at':    df['Imported_At'],
    })
    
    # กรองเฉพาะรายการที่มียอดเงิน
    clean = clean[clean['amount'] > 0].copy()
    
    # บันทึกลง table ใหม่
    clean.to_sql('clean_transactions', conn, if_exists='replace', index=False)
    
    print(f"✅ สร้าง clean_transactions สำเร็จ: {len(clean)} รายการ")
    print(f"   รายรับรวม: ฿{clean['amount'].sum():,.2f}")
    
    conn.close()

# ─────────────────────────────────────────────
# 3. สรุปยอดรายห้อง
# ─────────────────────────────────────────────
def room_revenue_summary():
    conn = connect()
    
    # ใช้ bookings (ข้อมูลสะอาดที่สุด)
    df = pd.read_sql("""
        SELECT room_no, 
               COUNT(*) as จำนวนครั้ง,
               SUM(total_amount) as รายรับรวม,
               AVG(total_amount) as เฉลี่ย
        FROM bookings
        WHERE total_amount > 0
        GROUP BY room_no
        ORDER BY รายรับรวม DESC
    """, conn)
    
    print("\n=== รายได้ตามห้อง (จาก bookings) ===")
    print(df.to_string(index=False))
    
    conn.close()
    return df

# ─────────────────────────────────────────────
# 4. ตรวจสอบข้อมูล
# ─────────────────────────────────────────────
def health_check():
    conn = connect()
    cur = conn.cursor()
    
    checks = {
        'rooms': "SELECT status, COUNT(*) FROM rooms GROUP BY status",
        'bookings': "SELECT COUNT(*), SUM(total_amount) FROM bookings WHERE total_amount > 0",
        'clean_transactions': "SELECT COUNT(*), SUM(amount) FROM clean_transactions",
    }
    
    print("\n=== Health Check ===")
    for table, query in checks.items():
        try:
            cur.execute(query)
            result = cur.fetchall()
            print(f"✅ {table}: {result}")
        except Exception as e:
            print(f"❌ {table}: {e}")
    
    conn.close()

# ─────────────────────────────────────────────
# 5. บันทึกรายรับใหม่ (ใช้งานประจำวัน)
# ─────────────────────────────────────────────
def add_income(date: str, source: str, amount: float, note: str = ""):
    """
    ตัวอย่าง: add_income('2026-02-27', 'ค่าห้องรายวัน', 400, 'B106 นายสมชาย')
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO income_table (date, source, amount, note) VALUES (?, ?, ?, ?)",
        (date, source, amount, note)
    )
    conn.commit()
    print(f"✅ บันทึกรายรับ: {date} | {source} | ฿{amount:,.0f} | {note}")
    conn.close()

# ─────────────────────────────────────────────
# 6. บันทึกรายจ่ายใหม่
# ─────────────────────────────────────────────
def add_expense(date: str, category: str, amount: float, vendor: str = ""):
    """
    ตัวอย่าง: add_expense('2026-02-27', 'ค่าแรง / เงินเดือน', 400, 'พิกุล')
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expense_table (date, category, amount, vendor) VALUES (?, ?, ?, ?)",
        (date, category, amount, vendor)
    )
    conn.commit()
    print(f"✅ บันทึกรายจ่าย: {date} | {category} | ฿{amount:,.0f} | {vendor}")
    conn.close()

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🏨 วิพัฒน์โฮเทล — Database Fix Script")
    print("=" * 50)
    
    fix_room_status()
    create_clean_transactions()
    room_revenue_summary()
    health_check()
    
    print("\n✅ เสร็จสิ้น! ฐานข้อมูลพร้อมใช้งาน")
    print("\nใช้งาน daily:")
    print("  add_income('2026-02-27', 'ค่าห้องรายวัน', 400, 'B106 ชื่อลูกค้า')")
    print("  add_expense('2026-02-27', 'ค่าแรง / เงินเดือน', 400, 'พิกุล')")
