#!/usr/bin/env python3
"""
วิพัฒน์โฮเทล - AI Assistant
รันแล้วพิมพ์คุยได้เลย
"""

import sqlite3
import os

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def show_rooms():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT room_no, type, status, building FROM rooms WHERE status = 'Available' ORDER BY room_no")
    rooms = c.fetchall()
    conn.close()
    
    print("\n🏨 ห้องว่าง:")
    print("-" * 40)
    for r in rooms:
        print(f"  {r[0]:6} | {r[1]:15} | โซน {r[3]}")
    print(f"\n📊 รวม: {len(rooms)} ห้อง")

def search_guest(name):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name, phone, country FROM guests WHERE name LIKE ?", (f"%{name}%",))
    guests = c.fetchall()
    conn.close()
    
    print(f"\n👥 ผลค้นหา: {name}")
    print("-" * 40)
    for g in guests:
        print(f"  {g[0]} | {g[1]} | {g[2]}")

def book_room(room, date, nights, name):
    conn = get_db()
    c = conn.cursor()
    
    # Check room
    c.execute("SELECT price_per_night FROM rooms WHERE room_no = ?", (room,))
    result = c.fetchone()
    if not result:
        print(f"❌ ไม่มีห้อง {room}")
        return
    
    price = result[0]
    total = price * int(nights)
    
    # Get or create guest
    c.execute("SELECT guest_id FROM guests WHERE name = ?", (name,))
    g = c.fetchone()
    if g:
        guest_id = g[0]
    else:
        import uuid
        guest_id = "GUEST-" + str(uuid.uuid4())[:8]
        c.execute("INSERT INTO guests (guest_id, name, country) VALUES (?, ?, 'ไทย')", (guest_id, name))
    
    # Create booking
    import uuid
    booking_no = "BKG-" + str(uuid.uuid4())[:8]
    
    from datetime import datetime, timedelta
    check_out = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=int(nights))).strftime('%Y-%m-%d')
    
    c.execute("""INSERT INTO bookings 
        (booking_no, room_no, guest_id, check_in, check_out, nights, room_rate, total_amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active')""",
        (booking_no, room, guest_id, date, check_out, int(nights), price, total))
    
    # Update room status
    c.execute("UPDATE rooms SET status = 'ไม่ว่าง' WHERE room_no = ?", (room,))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ จองสำเร็จ!")
    print(f"   ห้อง: {room}")
    print(f"   ชื่อ: {name}")
    print(f"   วันที่: {date} - {check_out}")
    print(f"   คืน: {nights}")
    print(f"   ราคา: ฿{total}")

def show_report():
    conn = get_db()
    c = conn.cursor()
    
    # Room stats
    c.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Available'")
    available = c.fetchone()[0]
    
    # This month revenue
    from datetime import datetime
    month = datetime.now().strftime('%Y-%m')
    c.execute("""SELECT SUM(total_amount) FROM bookings 
                WHERE check_in LIKE ? AND status = 'Active'""", (f"{month}%",))
    revenue = c.fetchone()[0] or 0
    
    conn.close()
    
    print(f"\n📊 รายงานวิพัฒน์โฮเทล")
    print("=" * 40)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    print(f"🛏️ ห้องว่าง: {available}/{total_rooms}")
    print(f"💰 รายได้เดือนนี้: ฿{revenue:,}")

def main():
    print("=" * 50)
    print("🏨 วิพัฒน์โฮเทล AI Assistant")
    print("=" * 50)
    print("\nพิมพ์คำสั่งได้เลย:")
    print("  1 - ดูห้องว่าง")
    print("  2 - ค้นหาลูกค้า")
    print("  3 - จองห้อง")
    print("  4 - ดูรายงาน")
    print("  5 - ออก")
    print()
    
    while True:
        cmd = input("> ").strip()
        
        if cmd == "1":
            show_rooms()
        elif cmd == "2":
            name = input("ชื่อลูกค้า: ")
            search_guest(name)
        elif cmd == "3":
            room = input("เลขห้อง: ")
            date = input("วันที่ (YYYY-MM-DD): ")
            nights = input("จำนวนคืน: ")
            name = input("ชื่อลูกค้า: ")
            book_room(room, date, nights, name)
        elif cmd == "4":
            show_report()
        elif cmd == "5":
            print("👋")
            break
        else:
            print("ไม่เข้าใจ ลองใหม่")

if __name__ == "__main__":
    main()
