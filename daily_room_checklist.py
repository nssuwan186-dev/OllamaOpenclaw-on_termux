import sqlite3
from datetime import datetime, timedelta
import json
import os

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

def get_daily_checklist():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today_dt = datetime.now().date() + timedelta(days=-1) # Adjust to yesterday's date for processing
    today_str = today_dt.strftime('%Y-%m-%d')

    checklist = {
        "check_in_today": [],
        "check_out_today": [],
        "occupied_ongoing": [],
        "available_today": [],
        "under_maintenance": [],
        "monthly_stay": []
    }

    # 1. Rooms Under Maintenance
    cursor.execute("SELECT room_no FROM rooms WHERE status = 'Under Maintenance'")
    for row in cursor.fetchall():
        checklist["under_maintenance"].append(row[0])

    # 2. Rooms with Monthly Stay
    cursor.execute("SELECT room_no FROM rooms WHERE status = 'Monthly'")
    for row in cursor.fetchall():
        checklist["monthly_stay"].append(row[0])

    # Get all rooms and their initial status
    all_rooms_status = {} # Map room_number to its status
    cursor.execute("SELECT room_no, status FROM rooms")
    for room_num, status in cursor.fetchall():
        all_rooms_status[room_num] = status

    # Get all relevant bookings
    # We need bookings that check in today, check out today, or are ongoing today.
    cursor.execute("""
        SELECT b.room_no, g.name, b.check_in, b.check_out, b.nights
        FROM bookings b
        JOIN guests g ON b.guest_id = g.guest_id
        WHERE b.check_in <= ?                                 -- Checkin is on or before today
          AND b.check_out > ?                                 -- Checkout is after today (means still occupied today)
    """, (today_str, today_str))
    
    # Store rooms occupied by bookings to distinguish from rooms with other statuses
    booked_rooms_today = set() 

    for room_number, customer_name, check_in_date_str, check_out_date_str, nights in cursor.fetchall():
        check_in_dt = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()
        check_out_dt = datetime.strptime(check_out_date_str, '%Y-%m-%d').date()
        
        if check_in_dt == today_dt:
            checklist["check_in_today"].append(f"{room_number} ({customer_name})")
            booked_rooms_today.add(room_number)
        
        # Check-out date is the day *after* the last night. So check if check_out_dt is today.
        if check_out_dt == today_dt:
            checklist["check_out_today"].append(f"{room_number} ({customer_name})")
            booked_rooms_today.add(room_number)

        # Room is occupied if check_in_date is in the past or today, and check_out_date is in the future.
        if check_in_dt <= today_dt < check_out_dt:
            if room_number not in [r.split(' ')[0] for r in checklist["occupied_ongoing"]]: # Avoid duplicates
                checklist["occupied_ongoing"].append(f"{room_number} ({customer_name})")
            booked_rooms_today.add(room_number)

    # Determine available rooms - these are rooms not under maintenance, not monthly, and not booked today.
    # Also, exclude rooms that are currently occupied due to an ongoing booking but might not be marked 'ไม่ว่าง' yet
    
    occupied_by_status = set(checklist["under_maintenance"] + checklist["monthly_stay"])
    all_occupied_rooms_derived = occupied_by_status.union(booked_rooms_today) # Union of status-based and booking-based occupied rooms

    for room_num in all_rooms_status:
        if room_num not in all_occupied_rooms_derived:
            # Check if room_num is already in check_in_today or occupied_ongoing.
            # This handles cases where a room is available but also checking in today.
            # A room is truly available if it's not marked as maintenance, monthly, or associated with any booking today.
            # The current logic for booked_rooms_today and all_occupied_rooms_derived should cover this.
            if all_rooms_status[room_num] == 'ว่าง': # Only consider rooms explicitly marked as 'ว่าง' in the table
                checklist["available_today"].append(room_num)


    conn.close()
    return {"status": "success", "checklist": checklist}

if __name__ == "__main__":
    result = get_daily_checklist()
    print(json.dumps(result, indent=2, ensure_ascii=False)) # ensure_ascii=False for Thai characters
