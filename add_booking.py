import uuid
import sqlite3
from datetime import datetime, timedelta
import json
import sys

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

def get_or_create_guest(conn, customer_name, phone="", address="", nationality="ไทย", id_card="", passport=""):
    cursor = conn.cursor()
    cursor.execute("SELECT guest_id FROM guests WHERE name = ?", (customer_name,))
    guest_id_row = cursor.fetchone()

    if guest_id_row:
        return guest_id_row[0]
    else:
        # Create a new guest if not found
        new_guest_id = "GUEST-" + str(uuid.uuid4())[:8] # Shorter UUID for guest_id
        cursor.execute("""
            INSERT INTO guests (guest_id, name, phone, address, country, id_card, passport)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (new_guest_id, customer_name, phone, address, nationality, id_card, passport))
        conn.commit() # Commit guest creation immediately
        return new_guest_id


def add_new_booking(room_number, customer_name, check_in_date_str, nights, 
                    contract_signing_date_str=None, meter_reading_check_in=None, 
                    channel="Telegram"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()
        nights_int = int(nights)
        booking_no = "BKG-" + str(uuid.uuid4()) # Generate unique booking number

        # Basic validation
        if nights_int <= 0:
            return {"status": "error", "message": "จำนวนคืนที่เข้าพักต้องมากกว่า 0"}
        
        # Use yesterday's date as current for context, matching user's input cycle
        current_context_date = datetime.now().date() + timedelta(days=-1)
        if check_in_date < current_context_date:
             return {"status": "error", "message": "วันที่ Check-in ต้องไม่เป็นอดีต (เมื่อเทียบกับวันที่ประมวลผล)"}

        # Check if room exists and get its details
        cursor.execute("SELECT room_no, type, price_per_night, status FROM rooms WHERE room_no = ?", (room_number,))
        room_info = cursor.fetchone()
        if not room_info:
            return {"status": "error", "message": f"ไม่พบห้องพักหมายเลข {room_number}"}
        
        # Get room_rate
        room_rate = room_info[2] # price_per_night

        # Default values for booking
        booking_status = "Active"
        booking_payment_channel = channel  # Use the channel parameter
        booking_booking_channel = channel

        # Get or create guest
        guest_id = get_or_create_guest(conn, customer_name)

        # Validate contract_signing_date if provided
        contract_signing_date_val = None
        if contract_signing_date_str:
            try:
                datetime.strptime(contract_signing_date_str, '%Y-%m-%d').date()
                contract_signing_date_val = contract_signing_date_str
            except ValueError:
                return {"status": "error", "message": "รูปแบบวันที่ทำสัญญาไม่ถูกต้อง (YYYY-MM-DD)"}
        
        # Validate meter_reading_check_in if provided
        meter_reading_val = None
        if meter_reading_check_in is not None:
            try:
                meter_reading_val = float(meter_reading_check_in)
            except ValueError:
                return {"status": "error", "message": "รูปแบบเลขมิเตอร์ไม่ถูกต้อง (ต้องเป็นตัวเลข)"}
        
        # Calculate check_out date
        check_out_date = check_in_date + timedelta(days=nights_int)

        # Calculate total_amount
        total_amount = nights_int * room_rate

        
        # Check for booking conflicts for the specific room/dates
        # A conflict exists if a new booking's period (check_in to check_out) overlaps with an existing booking's period.
        # Existing booking period: [existing_check_in, existing_check_in + existing_nights)
        # New booking period: [check_in_date, check_in_date + nights_int)
        # Overlap if: (Start1 < End2) and (End1 > Start2)
        new_check_out_date = check_in_date + timedelta(days=nights_int)

        cursor.execute("""
            SELECT b.check_in, b.nights, g.name
            FROM bookings b
            JOIN guests g ON b.guest_id = g.guest_id
            WHERE b.room_no = ? AND
                  (
                      (b.check_in < ? AND date(b.check_in, '+' || b.nights || ' days') > ?) OR
                      (? < date(b.check_in, '+' || b.nights || ' days') AND ? > b.check_in)
                  )
        """, (room_number, check_out_date.strftime('%Y-%m-%d'), check_in_date_str, check_out_date.strftime('%Y-%m-%d'), check_in_date_str))

        conflicting_bookings = cursor.fetchall()
        if conflicting_bookings:
            conflict_details = []
            for ci, n, cn in conflicting_bookings:
                conflict_details.append(f"มีการจองอยู่แล้วสำหรับคุณ {cn} ตั้งแต่ {ci} เป็นเวลา {n} คืน")
            return {"status": "error", "message": f"ห้องพัก {room_number} มีการจองซ้อนทับในช่วงเวลาที่ระบุแล้ว: " + ", ".join(conflict_details)}

        # Insert new booking
        cursor.execute("""
            INSERT INTO bookings (booking_no, room_no, guest_id, check_in, check_out, nights, 
                                  room_rate, service_fee, total_amount, status, payment_channel, 
                                  booking_channel, contract_signing_date, meter_reading_check_in)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (booking_no, room_number, guest_id, check_in_date_str, check_out_date.strftime('%Y-%m-%d'), nights_int, 
              room_rate, 0, total_amount, booking_status, booking_payment_channel, 
              booking_booking_channel, contract_signing_date_val, meter_reading_val))
        
        # Update room status to 'ไม่ว่าง' if the booking is current or upcoming
        # A more robust system would update status based on ongoing booking logic in the daily checklist script.
        # For a simple add, we just check if it impacts today or future.
        # If the booking starts today (relative to context_date) or is ongoing relative to context_date.
        if room_info[3] == 'ว่าง' or room_info[3] == 'ไม่ว่าง': # Allow re-booking 'ไม่ว่าง' status if conflict check passed
            if check_in_date <= current_context_date + timedelta(days=nights_int) and new_check_out_date > current_context_date:
                cursor.execute("UPDATE rooms SET status = 'ไม่ว่าง' WHERE room_no = ?", (room_number,))
        
        conn.commit()
        return {"status": "success", "message": f"จองห้องพัก {room_number} สำหรับคุณ {customer_name} วันที่ {check_in_date_str} จำนวน {nights_int} คืน เรียบร้อยแล้ว"}

    except ValueError:
        return {"status": "error", "message": "รูปแบบวันที่ไม่ถูกต้อง (YYYY-MM-DD) หรือจำนวนคืนไม่เป็นตัวเลข"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(json.dumps({"status": "error", "message": "Usage: add_booking.py <room_number> <customer_name> <check_in_date_YYYY-MM-DD> <nights> [contract_signing_date_YYYY-MM-DD] [meter_reading_check_in]"}))
    else:
        contract_date = sys.argv[5] if len(sys.argv) > 5 else None
        meter_read = sys.argv[6] if len(sys.argv) > 6 else None
        result = add_new_booking(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], contract_date, meter_read)
        print(json.dumps(result, ensure_ascii=False))
