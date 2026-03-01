import sqlite3
from datetime import datetime, timedelta
import json
import os

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

def get_advance_notifications():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tomorrow_dt = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
    notifications = {
        "upcoming_check_in": [],
        "upcoming_check_out": []
    }

    # Upcoming Check-ins (tomorrow)
    cursor.execute("""
        SELECT b.room_no, g.name, b.check_in
        FROM bookings b
        JOIN guests g ON b.guest_id = g.guest_id
        WHERE b.check_in = ?
    """, (tomorrow_dt,))
    for row in cursor.fetchall():
        room_number, customer_name, check_in_date_str = row
        notifications["upcoming_check_in"].append(f"ห้อง {room_number} (คุณ{customer_name}): Check-in พรุ่งนี้ {check_in_date_str}")

    # Upcoming Check-outs (tomorrow)
    cursor.execute("""
        SELECT b.room_no, g.name, b.check_in, b.nights
        FROM bookings b
        JOIN guests g ON b.guest_id = g.guest_id
        WHERE b.check_out = ?
    """, (tomorrow_dt,))
    for row in cursor.fetchall():
        room_number, customer_name, check_in_date_str, nights = row
        notifications["upcoming_check_out"].append(f"ห้อง {room_number} (คุณ{customer_name}): Check-out พรุ่งนี้ (เข้าพัก {check_in_date_str} {nights} คืน)")

    conn.close()
    return {"status": "success", "notifications": notifications}

if __name__ == "__main__":
    result = get_advance_notifications()
    print(json.dumps(result, indent=2, ensure_ascii=False))
