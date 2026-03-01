#!/usr/bin/env python3
"""
export_csv.py — Export ข้อมูลเป็น CSV สำหรับ Google Sheets
วิพัฒน์โฮเทล · OpenClaw System
"""

import sqlite3
import csv
import sys
import os
from datetime import datetime

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"
OUTPUT_DIR = "/data/data/com.termux/files/home/.openclaw/workspace/exports"

# สร้างโฟลเดอร์ export ถ้ายังไม่มี
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_connection():
    return sqlite3.connect(DB_PATH)

def export_rooms():
    """Export ข้อมูลห้องพักทั้งหมด"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT room_no, building, floor, type, price_per_night, status
        FROM rooms
        ORDER BY building, floor, room_no
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    filename = f"{OUTPUT_DIR}/rooms_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # Header สำหรับ Google Sheets
        writer.writerow(['หมายเลขห้อง', 'ตึก', 'ชั้น', 'ประเภท', 'ราคาต่อคืน', 'สถานะ'])
        writer.writerows(rows)
    
    return filename, len(rows)

def export_bookings(start_date=None, end_date=None):
    """Export ข้อมูลการจอง"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if start_date and end_date:
        cursor.execute("""
            SELECT b.booking_no, b.room_no, g.name as guest_name, g.phone,
                   b.check_in, b.check_out, b.nights, b.room_rate, 
                   b.total_amount, b.payment_channel, b.status
            FROM bookings b
            LEFT JOIN guests g ON b.guest_id = g.guest_id
            WHERE b.check_in >= ? AND b.check_in <= ?
            ORDER BY b.check_in DESC
        """, (start_date, end_date))
    else:
        cursor.execute("""
            SELECT b.booking_no, b.room_no, g.name as guest_name, g.phone,
                   b.check_in, b.check_out, b.nights, b.room_rate,
                   b.total_amount, b.payment_channel, b.status
            FROM bookings b
            LEFT JOIN guests g ON b.guest_id = g.guest_id
            ORDER BY b.check_in DESC
            LIMIT 500
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    filename = f"{OUTPUT_DIR}/bookings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            'เลขที่จอง', 'หมายเลขห้อง', 'ชื่อลูกค้า', 'เบอร์โทร',
            'วันเช็คอิน', 'วันเช็คเอาท์', 'จำนวนคืน', 'ราคาห้อง',
            'ยอดรวม', 'ช่องทางชำระ', 'สถานะ'
        ])
        writer.writerows(rows)
    
    return filename, len(rows)

def export_transactions(year_month=None):
    """Export ข้อมูลรายรับจาก clean_transactions"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if year_month:
        cursor.execute("""
            SELECT trans_id, date, room_no, guest_name, amount, payment_method, source_file
            FROM clean_transactions
            WHERE strftime('%Y-%m', date) = ?
            ORDER BY date DESC
        """, (year_month,))
    else:
        cursor.execute("""
            SELECT trans_id, date, room_no, guest_name, amount, payment_method, source_file
            FROM clean_transactions
            ORDER BY date DESC
            LIMIT 1000
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    filename = f"{OUTPUT_DIR}/transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['รหัสรายการ', 'วันที่', 'ห้อง', 'ชื่อลูกค้า', 'จำนวนเงิน', 'ช่องทางชำระ', 'ไฟล์ต้นทาง'])
        writer.writerows(rows)
    
    return filename, len(rows)

def export_guests():
    """Export ข้อมูลลูกค้า"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT guest_id, name, phone, address, country, id_card, passport
        FROM guests
        ORDER BY name
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    filename = f"{OUTPUT_DIR}/guests_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['รหัสลูกค้า', 'ชื่อ-นามสกุล', 'เบอร์โทร', 'ที่อยู่', 'สัญชาติ', 'เลขบัตรปชช', 'หนังสือเดินทาง'])
        writer.writerows(rows)
    
    return filename, len(rows)

def export_monthly_summary(year=None):
    """Export สรุปรายเดือน"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if year:
        cursor.execute("""
            SELECT month, year, total_income, total_expense, 
                   (total_income - total_expense) as net_profit
            FROM monthly_summary
            WHERE year = ?
            ORDER BY year DESC, month DESC
        """, (year,))
    else:
        cursor.execute("""
            SELECT month, year, total_income, total_expense,
                   (total_income - total_expense) as net_profit
            FROM monthly_summary
            ORDER BY year DESC, month DESC
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    filename = f"{OUTPUT_DIR}/monthly_summary_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['เดือน', 'ปี', 'รายรับ', 'รายจ่าย', 'กำไรสุทธิ'])
        writer.writerows(rows)
    
    return filename, len(rows)

def export_available_rooms():
    """Export ห้องว่าง"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT room_no, building, floor, type, price_per_night
        FROM rooms
        WHERE status = 'Available'
        ORDER BY building, floor, room_no
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    filename = f"{OUTPUT_DIR}/available_rooms_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['หมายเลขห้อง', 'ตึก', 'ชั้น', 'ประเภท', 'ราคาต่อคืน'])
        writer.writerows(rows)
    
    return filename, len(rows)

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Export ข้อมูลเป็น CSV สำหรับ Google Sheets')
    parser.add_argument('type', choices=['rooms', 'bookings', 'transactions', 'guests', 'monthly', 'available'],
                        help='ประเภทข้อมูลที่ต้องการ export')
    parser.add_argument('--date', help='วันที่ (YYYY-MM-DD) สำหรับ bookings')
    parser.add_argument('--month', help='เดือน (YYYY-MM) สำหรับ transactions')
    parser.add_argument('--year', help='ปี (YYYY) สำหรับ monthly summary')
    parser.add_argument('--start', help='วันเริ่ม (YYYY-MM-DD) สำหรับ bookings')
    parser.add_argument('--end', help='วันสิ้น (YYYY-MM-DD) สำหรับ bookings')
    
    args = parser.parse_args()
    
    print(f"📤 กำลัง export ข้อมูล: {args.type}")
    print("=" * 50)
    
    try:
        if args.type == 'rooms':
            filename, count = export_rooms()
        elif args.type == 'available':
            filename, count = export_available_rooms()
        elif args.type == 'bookings':
            filename, count = export_bookings(args.start, args.end)
        elif args.type == 'transactions':
            filename, count = export_transactions(args.month)
        elif args.type == 'guests':
            filename, count = export_guests()
        elif args.type == 'monthly':
            filename, count = export_monthly_summary(args.year)
        
        print(f"✅ สำเร็จ!")
        print(f"📁 ไฟล์: {filename}")
        print(f"📊 จำนวน: {count} รายการ")
        
    except Exception as e:
        print(f"❌ ผิดพลาด: {e}")
        sys.exit(1)
