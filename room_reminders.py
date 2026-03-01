import sqlite3
from datetime import datetime, timedelta
import json
import os

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

def get_monthly_reminders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    reminders = []
    
    today = (datetime.now() + timedelta(days=-1)).day # Adjust to yesterday's day for processing
    
    # Get bookings that might need a monthly reminder
    # Assuming check_in_date is in 'YYYY-MM-DD' format
    cursor.execute("""
        SELECT b.room_no, g.name, b.check_in
        FROM bookings b
        JOIN guests g ON b.guest_id = g.guest_id
    """)
    
    for row in cursor.fetchall():
        room_number, customer_name, check_in_date_str = row
        
        try:
            check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d')
            
            # Calculate the reminder day. If check-in is e.g., 31st, for Feb use last day of Feb.
            day_of_month = check_in_date.day
            
            # Check if today is the reminder day for this month
            if today == day_of_month:
                 # Check if this booking is still active or relevant for this month.
                 # For simplicity, we assume all bookings are ongoing if their check_in_date has passed.
                 # A more robust system would check a 'check_out_date' or 'status'.
                 reminders.append(f"ห้อง {room_number} (คุณ{customer_name}): ครบรอบชำระเงินเดือนนี้ (เริ่มต้น {check_in_date_str})")
            elif day_of_month > today and today == (datetime.now().replace(day=1) + timedelta(days=32)).day -1 : # Check if today is the last day of the month and the reminder day is greater than today (e.g. 31st in February)
                 reminders.append(f"ห้อง {room_number} (คุณ{customer_name}): ครบรอบชำระเงินเดือนนี้ (เริ่มต้น {check_in_date_str})")

        except ValueError:
            # Handle invalid date format if necessary
            pass
            
    conn.close()
    return reminders

if __name__ == "__main__":
    reminders = get_monthly_reminders()
    if reminders:
        print(json.dumps({"status": "success", "reminders": reminders}))
    else:
        print(json.dumps({"status": "success", "reminders": ["ไม่มีกำหนดการแจ้งเตือนวันนี้"]}))