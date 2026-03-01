#!/usr/bin/env python3
"""
telegram_handler.py — ระบบ Telegram Bot สำหรับวิพัฒน์โฮเทล
รองรับ: Commands, Inline Buttons, Rich Messages, Data Management
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# ============================================
# 📊 DATA QUERIES
# ============================================

def get_dashboard_stats():
    """ดึงสถิติ Dashboard"""
    conn = get_connection()
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Rooms
    c.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Available'")
    available = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM rooms")
    total = c.fetchone()[0]
    
    # Today's bookings
    c.execute("SELECT COUNT(*) FROM bookings WHERE check_in = ?", (today,))
    check_ins = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM bookings WHERE check_out = ?", (today,))
    check_outs = c.fetchone()[0]
    
    # Revenue
    c.execute("""
        SELECT SUM(total_amount) FROM bookings 
        WHERE strftime('%Y-%m', check_in) = strftime('%Y-%m', 'now')
    """)
    month_revenue = c.fetchone()[0] or 0
    
    # Recent transactions
    c.execute("""
        SELECT room_no, guest_name, amount, payment_method, date
        FROM clean_transactions
        ORDER BY date DESC LIMIT 5
    """)
    recent = c.fetchall()
    
    conn.close()
    
    return {
        'available': available,
        'total': total,
        'check_ins': check_ins,
        'check_outs': check_outs,
        'month_revenue': month_revenue,
        'recent': recent
    }

def get_available_rooms():
    """ดึงห้องว่าง"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT room_no, building, type, price_per_night
        FROM rooms WHERE status = 'Available'
        ORDER BY building, room_no
    """)
    rooms = c.fetchall()
    conn.close()
    return rooms

def get_all_rooms():
    """ดึงห้องทั้งหมด"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT room_no, building, floor, type, price_per_night, status FROM rooms ORDER BY building, room_no")
    rooms = c.fetchall()
    conn.close()
    return rooms

def search_guest(query):
    """ค้นหาลูกค้า"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT guest_id, name, phone, country
        FROM guests
        WHERE name LIKE ? OR phone LIKE ?
        LIMIT 10
    """, (f'%{query}%', f'%{query}%'))
    guests = c.fetchall()
    conn.close()
    return guests

def get_booking_details(booking_no):
    """ดึงรายละเอียดการจอง"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT b.booking_no, b.room_no, g.name, g.phone, b.check_in, b.check_out, 
               b.nights, b.total_amount, b.payment_channel, b.status
        FROM bookings b
        LEFT JOIN guests g ON b.guest_id = g.guest_id
        WHERE b.booking_no = ?
    """, (booking_no,))
    booking = c.fetchone()
    conn.close()
    return booking

def get_room_bookings(room_no):
    """ดึงประวัติการจองห้อง"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT b.check_in, b.check_out, g.name, b.total_amount
        FROM bookings b
        LEFT JOIN guests g ON b.guest_id = g.guest_id
        WHERE b.room_no = ?
        ORDER BY b.check_in DESC LIMIT 10
    """, (room_no,))
    bookings = c.fetchall()
    conn.close()
    return bookings

# ============================================
# 📱 MESSAGE BUILDERS
# ============================================

def build_dashboard_message():
    """สร้างข้อความ Dashboard"""
    stats = get_dashboard_stats()
    
    text = f"""🏨 <b>วิพัฒน์โฮเทล - Dashboard</b>

📅 {datetime.now().strftime('%d/%m/%Y')}

📊 <b>สถานะห้อง:</b>
• ว่าง: <b>{stats['available']}/{stats['total']}</b> ห้อง
• Check-in วันนี้: {stats['check_ins']}
• Check-out วันนี้: {stats['check_outs']}

💰 <b>รายได้เดือนนี้:</b>
• <b>฿{stats['month_revenue']:,.0f}</b>

<i>เลือกเมนูด้านล่างเพื่อดูข้อมูลเพิ่มเติม</i>"""
    
    return text

def build_rooms_message():
    """สร้างข้อความห้องว่าง"""
    rooms = get_available_rooms()
    
    if not rooms:
        return "✅ ไม่มีห้องว่างในขณะนี้"
    
    # Group by building
    buildings = {}
    for r in rooms:
        b = r[1]
        if b not in buildings:
            buildings[b] = []
        buildings[b].append(r)
    
    text = "✅ <b>ห้องว่าง</b>\n\n"
    
    for b, room_list in buildings.items():
        text += f"🏢 <b>ตึก {b}</b>\n"
        for r in room_list:
            text += f"• {r[0]} - {r[2]} (฿{r[3]:,.0f}/คืน)\n"
        text += "\n"
    
    return text

def build_all_rooms_message():
    """สร้างข้อความห้องทั้งหมด"""
    rooms = get_all_rooms()
    
    text = "📋 <b>สถานะห้องทั้งหมด</b>\n\n"
    
    buildings = {}
    for r in rooms:
        b = r[1]
        if b not in buildings:
            buildings[b] = []
        buildings[b].append(r)
    
    for b, room_list in buildings.items():
        text += f"🏢 <b>ตึก {b}</b> ({len(room_list)} ห้อง)\n"
        for r in room_list:
            status_icon = "✅" if r[5] == "Available" else "❌" if r[5] == "Under Maintenance" else "🗓️"
            text += f"  {status_icon} {r[0]} - {r[3]} - {r[5]}\n"
        text += "\n"
    
    return text

def build_guest_search_message(query):
    """สร้างข้อความผลการค้นหาลูกค้า"""
    guests = search_guest(query)
    
    if not guests:
        return f"❌ ไม่พบลูกค้าที่ค้นหา: {query}"
    
    text = f"👥 <b>ผลการค้นหา: {query}</b>\n\n"
    
    for g in guests:
        text += f"• <b>{g[1]}</b>\n"
        text += f"  📱 {g[2]}\n"
        text += f"  🌍 {g[3]}\n"
        text += f"  ID: {g[0]}\n\n"
    
    return text

def build_help_message():
    """สร้างข้อความ help"""
    text = """🤖 <b>คำสั่งที่รองรับ</b>

/start - เริ่มต้นใช้งาจ
/dashboard - ดูสถานะห้อง
/rooms - ดูห้องว่าง
/allrooms - ดูห้องทั้งหมด
/search [ชื่อ] - ค้นห้า
/าลูกคroom [เลขห้อง] - ดูข้อมูลห้อง
/report - ดูรายงาน HTML
/help - แสดงคำสั่งทั้งหมด

<i>กดปุ่มด้านล่างเพื่อใช้งานง่ายๆ</i>"""
    return text

# ============================================
# 🎛️ INLINE KEYBOARD BUILDER
# ============================================

def build_main_keyboard():
    """สร้าง Main Keyboard"""
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📊 Dashboard", "callback_data": "dashboard"},
                {"text": "✅ ห้องว่าง", "callback_data": "rooms"}
            ],
            [
                {"text": "📋 ทุกห้อง", "callback_data": "all_rooms"},
                {"text": "🔍 ค้นหาลูกค้า", "callback_data": "search"}
            ],
            [
                {"text": "📈 รายงาน", "callback_data": "report"},
                {"text": "❓ ช่วยเหลือ", "callback_data": "help"}
            ]
        ]
    }
    return json.dumps(keyboard)

def build_rooms_keyboard():
    """สร้าง Rooms Keyboard"""
    rooms = get_available_rooms()
    
    keyboard = {"inline_keyboard": []}
    row = []
    
    for i, r in enumerate(rooms):
        row.append({"text": r[0], "callback_data": f"room:{r[0]}"})
        if len(row) == 3:
            keyboard["inline_keyboard"].append(row)
            row = []
    
    if row:
        keyboard["inline_keyboard"].append(row)
    
    # Back button
    keyboard["inline_keyboard"].append([
        {"text": "🔙 กลับ", "callback_data": "back"}
    ])
    
    return json.dumps(keyboard)

def build_back_keyboard():
    """สร้าง Back Keyboard"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 กลับเมนูหลัก", "callback_data": "back"}]
        ]
    }
    return json.dumps(keyboard)

# ============================================
# 🚀 MAIN HANDLER
# ============================================

def handle_command(command, args=None):
    """จัดการคำสั่ง"""
    
    if command == "start":
        return {
            "text": "🏨 ยินดีต้อนรับสู่วิพัฒน์โฮเทล!\n\n" + build_dashboard_message(),
            "keyboard": build_main_keyboard()
        }
    
    elif command == "dashboard":
        return {
            "text": build_dashboard_message(),
            "keyboard": build_main_keyboard()
        }
    
    elif command == "rooms":
        return {
            "text": build_rooms_message(),
            "keyboard": build_main_keyboard()
        }
    
    elif command == "allrooms":
        return {
            "text": build_all_rooms_message(),
            "keyboard": build_main_keyboard()
        }
    
    elif command == "search" and args:
        return {
            "text": build_guest_search_message(args),
            "keyboard": build_main_keyboard()
        }
    
    elif command == "room" and args:
        room_no = args.upper()
        bookings = get_room_bookings(room_no)
        
        if not bookings:
            text = f"📋 ห้อง {room_no}\n\n❌ ไม่มีประวัติการจอง"
        else:
            text = f"📋 <b>ประวัติห้อง {room_no}</b>\n\n"
            for b in bookings:
                text += f"• {b[0]} → {b[1]}: {b[2]} (฿{b[3]:,.0f})\n"
        
        return {
            "text": text,
            "keyboard": build_back_keyboard()
        }
    
    elif command == "report":
        from report_generator import generate_daily_report
        filename, stats = generate_daily_report()
        
        text = f"""📈 <b>รายงานประจำวัน</b>

📊 ห้องว่าง: {stats['available_rooms']}/{stats['total_rooms']}
💰 รายได้วันนี้: ฿{stats['today_revenue']:,.0f}
💵 รายได้เดือนนี้: ฿{stats['month_revenue']:,.0f}

📄 ดาวน์โหลด: {filename}"""
        
        return {
            "text": text,
            "file": filename,
            "keyboard": build_main_keyboard()
        }
    
    elif command == "help":
        return {
            "text": build_help_message(),
            "keyboard": build_main_keyboard()
        }
    
    else:
        return {
            "text": "❌ ไม่เข้าใจคำสั่ง\n\n" + build_help_message(),
            "keyboard": build_main_keyboard()
        }

def handle_callback(callback_data):
    """จัดการ Callback Query"""
    
    if callback_data == "dashboard":
        return handle_command("dashboard")
    elif callback_data == "rooms":
        return handle_command("rooms")
    elif callback_data == "all_rooms":
        return handle_command("allrooms")
    elif callback_data == "search":
        return {"text": "🔍 พิมชื่อลูกค้าที่ต้องการค้นหา:", "keyboard": build_back_keyboard()}
    elif callback_data == "report":
        return handle_command("report")
    elif callback_data == "help":
        return handle_command("help")
    elif callback_data == "back":
        return handle_command("dashboard")
    elif callback_data.startswith("room:"):
        room_no = callback_data.split(":")[1]
        return handle_command("room", room_no)
    
    return {"text": "❌ ไม่เข้าใจการทำงาน"}

# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Telegram Handler Test")
    print("=" * 50)
    
    # Test Dashboard
    result = handle_command("dashboard")
    print("\n📊 Dashboard:")
    print(result["text"][:500])
    
    # Test Rooms
    result = handle_command("rooms")
    print("\n✅ Rooms:")
    print(result["text"][:300])
    
    # Test Search
    result = handle_command("search", "สม")
    print("\n🔍 Search:")
    print(result["text"][:300])
