import sqlite3
from datetime import datetime, timedelta
import json
import sys

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def get_room_availability(query_date_str, room_type=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query_date = datetime.strptime(query_date_str, '%Y-%m-%d').date()
    
    available_rooms = []
    
    # Get all rooms that are not explicitly 'Under Maintenance' or 'Monthly' by status
    # We will refine availability by checking bookings
    sql_base = "SELECT room_no, type, status, building FROM rooms WHERE status != 'Under Maintenance' AND status != 'Monthly'"
    params = []
    if room_type:
        sql_base += " AND type LIKE ?"
        params.append(f'%{room_type}%') # Use LIKE for partial matches
    
    cursor.execute(sql_base, params)
    potential_available_rooms = {row[0]: {'type': row[1], 'status': row[2], 'building': row[3]} for row in cursor.fetchall()}

    # Find rooms that are booked on the query_date
    booked_rooms_on_date = set()
    cursor.execute("""
        SELECT room_no
        FROM bookings
        WHERE check_in <= ? AND check_out > ?
    """, (query_date_str, query_date_str))
    
    for row in cursor.fetchall():
        booked_rooms_on_date.add(row[0])

    for room_num, details in potential_available_rooms.items():
        if room_num not in booked_rooms_on_date:
            available_rooms.append(f"ห้อง {room_num} ({details['type']} โซน {details['building']})")
            
    conn.close()
    return available_rooms

def get_room_specific_details(room_identifier):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    details = {}
    cursor.execute("SELECT room_no, building, floor, type, status, price_per_night FROM rooms WHERE room_no = ?", (room_identifier,))
    room_info = cursor.fetchone()

    if room_info:
        details['room_number'] = room_info[0]
        details['building'] = room_info[1]
        details['floor'] = room_info[2]
        details['room_type'] = room_info[3]
        details['status'] = room_info[4]
        details['price_per_night'] = room_info[5]

        # Check for current/upcoming bookings
        current_context_date = datetime.now().date() + timedelta(days=-1) # Use yesterday's context
        cursor.execute("""
            SELECT g.name, b.check_in, b.nights, b.check_out
            FROM bookings b
            JOIN guests g ON b.guest_id = g.guest_id
            WHERE b.room_no = ? AND b.check_in <= ? AND b.check_out > ?
            ORDER BY b.check_in DESC
            LIMIT 1
        """, (room_identifier, current_context_date.strftime('%Y-%m-%d'), current_context_date.strftime('%Y-%m-%d')))
        
        booking_info = cursor.fetchone()
        if booking_info:
            customer_name, check_in_date_str, nights, check_out_date_str = booking_info
            details['current_booking'] = {
                'customer_name': customer_name,
                'check_in': check_in_date_str,
                'check_out': check_out_date_str,
                'nights': nights
            }
        
        # Check for future bookings
        cursor.execute("""
            SELECT g.name, b.check_in, b.nights, b.check_out
            FROM bookings b
            JOIN guests g ON b.guest_id = g.guest_id
            WHERE b.room_no = ? AND b.check_in > ?
            ORDER BY b.check_in ASC
            LIMIT 1
        """, (room_identifier, current_context_date.strftime('%Y-%m-%d')))
        future_booking_info = cursor.fetchone()
        if future_booking_info:
            customer_name, check_in_date_str, nights, check_out_date_str = future_booking_info
            details['next_booking'] = {
                'customer_name': customer_name,
                'check_in': check_in_date_str,
                'check_out': check_out_date_str,
                'nights': nights
            }

    conn.close()
    return details

def get_monthly_rental_info():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    monthly_rooms_info = []
    # Fetch rooms marked 'Monthly'
    cursor.execute("""
        SELECT room_no, type, building
        FROM rooms
        WHERE status = 'Monthly'
    """)
    monthly_rooms_data = cursor.fetchall()

    for room_number, room_type, building in monthly_rooms_data:
        # For each monthly room, find the latest booking details
        cursor.execute("""
            SELECT guest_id, check_in, contract_signing_date, meter_reading_check_in
            FROM bookings
            WHERE room_no = ?
            ORDER BY check_in DESC
            LIMIT 1
        """, (room_number,))
        booking_info = cursor.fetchone()

        # Get guest name from guests table
        customer_name = "ไม่ทราบ"
        if booking_info and booking_info[0]:
            cursor.execute("SELECT name FROM guests WHERE guest_id = ?", (booking_info[0],))
            guest_row = cursor.fetchone()
            if guest_row:
                customer_name = guest_row[0]
        
        check_in_date = booking_info[1] if booking_info else "ไม่ทราบ"
        contract_signing_date = booking_info[2] if booking_info and booking_info[2] else "ไม่พบ"
        meter_reading = booking_info[3] if booking_info and booking_info[3] is not None else "ไม่พบ"
        
        monthly_rooms_info.append({
            'room_number': room_number,
            'room_type': room_type,
            'building': building,
            'customer_name': customer_name,
            'check_in_date': check_in_date,
            'contract_signing_date': contract_signing_date,
            'meter_reading_check_in': meter_reading
        })

    conn.close()
    return monthly_rooms_info

def get_tomorrow_room_info():
    tomorrow_dt = datetime.now().date() + timedelta(days=1) # Actual tomorrow
    tomorrow_str = tomorrow_dt.strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    check_ins = []
    check_outs = []
    
    # Check-ins tomorrow
    cursor.execute("""
        SELECT b.room_no, g.name
        FROM bookings b
        JOIN guests g ON b.guest_id = g.guest_id
        WHERE b.check_in = ?
    """, (tomorrow_str,))
    for room_num, cust_name in cursor.fetchall():
        check_ins.append(f"ห้อง {room_num} (คุณ {cust_name})")

    # Check-outs tomorrow
    cursor.execute("""
        SELECT b.room_no, g.name, b.check_in, b.nights
        FROM bookings b
        JOIN guests g ON b.guest_id = g.guest_id
        WHERE b.check_out = ?
    """, (tomorrow_str,))
    for room_num, cust_name, check_in_date_str, nights in cursor.fetchall():
        check_outs.append(f"ห้อง {room_num} (คุณ {cust_name}) (เข้าพัก {check_in_date_str} {nights} คืน)")
    
    conn.close()
    return {"check_ins_tomorrow": check_ins, "check_outs_tomorrow": check_outs}


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else None
    
    if action == "availability":
        date_str = sys.argv[2]
        room_type = sys.argv[3] if len(sys.argv) > 3 else None
        result = get_room_availability(date_str, room_type)
        print(json.dumps({"status": "success", "data": result}, ensure_ascii=False))
    elif action == "details":
        room_identifier = sys.argv[2]
        result = get_room_specific_details(room_identifier)
        print(json.dumps({"status": "success", "data": result}, ensure_ascii=False))
    elif action == "monthly_rentals":
        result = get_monthly_rental_info()
        print(json.dumps({"status": "success", "data": result}, ensure_ascii=False))
    elif action == "tomorrow_info":
        result = get_tomorrow_room_info()
        print(json.dumps({"status": "success", "data": result}, ensure_ascii=False))
    else:
        print(json.dumps({"status": "error", "message": "Invalid action. Use availability, details, monthly_rentals, or tomorrow_info."}, ensure_ascii=False))