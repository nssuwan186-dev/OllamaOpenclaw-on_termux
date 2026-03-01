#!/usr/bin/env python3
"""
hotel_ai_agent.py — AI Agent ฉลาดสำหรับโรงแรม
วิพัฒน์โฮเทล · OpenClaw System

มีความสามารถ:
1. รับคำสั่งภาษาธรรมชาติ
2. วิเคราะห์และทำงานอัตโนมัติ
3. เชื่อมต่อทุกระบบ
4. จำข้อมูลและเรียนรู้
"""

import sqlite3
import json
import os
import re
from datetime import datetime, timedelta

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

# ============================================
# 🧠 AI CORE FUNCTIONS
# ============================================

def get_connection():
    return sqlite3.connect(DB_PATH)

# ============================================
# 📊 DATABASE QUERIES
# ============================================

def query_database(sql, params=None):
    """Query ฐานข้อมูล"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        if params:
            c.execute(sql, params)
        else:
            c.execute(sql)
        
        columns = [description[0] for description in c.description] if c.description else []
        rows = c.fetchall()
        conn.close()
        
        return {'success': True, 'columns': columns, 'rows': rows}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def execute_action(action, params=None):
    """Execute การกระทำต่างๆ"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        if action == 'add_booking':
            # เพิ่มการจอง
            c.execute("""
                INSERT INTO bookings (booking_no, room_no, guest_id, check_in, check_out, nights, 
                                    room_rate, service_fee, total_amount, status, payment_channel, booking_channel)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, params)
            
            # อัปเดตสถานะห้อง
            c.execute("UPDATE rooms SET status = 'ไม่ว่าง' WHERE room_no = ?", (params[1],))
            
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'เพิ่มการจองสำเร็จ'}
        
        elif action == 'add_guest':
            # เพิ่มลูกค้า
            c.execute("""
                INSERT INTO guests (guest_id, name, phone, address, country)
                VALUES (?, ?, ?, ?, ?)
            """, params)
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'เพิ่มลูกค้าสำเร็จ'}
        
        elif action == 'update_room_status':
            # อัปเดตสถานะห้อง
            c.execute("UPDATE rooms SET status = ? WHERE room_no = ?", params)
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'อัปเดตสถานะห้องสำเร็จ'}
        
        elif action == 'add_income':
            # เพิ่มรายรับ
            c.execute("""
                INSERT INTO clean_transactions (trans_id, date, room_no, guest_name, amount, payment_method)
                VALUES (?, ?, ?, ?, ?, ?)
            """, params)
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'บันทึกรายรับสำเร็จ'}
        
        else:
            conn.close()
            return {'success': False, 'error': 'Unknown action'}
    
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

# ============================================
# 🎯 INTENT DETECTION
# ============================================

def detect_intent(message):
    """ตรวจจับความต้องการจากข้อความ"""
    message = message.lower()
    
    intents = {
        # ค้นหาข้อมูล
        'search_room': ['ห้องว่าง', 'ห้องว่าง', 'ห้องไหนว่าง', 'มีห้องไหนว่าง', 'available'],
        'search_guest': ['ค้นหาลูก', 'หาลูก', 'ลูกค้าชื่อ', 'ลูกค้า', 'guest', 'search'],
        'room_info': ['ข้อมูลห้อง', 'ห้อง', 'room', 'details'],
        'booking_info': ['การจอง', 'จอง', 'booking'],
        'revenue': ['รายได้', 'รายรับ', 'income', 'revenue', 'ยอด'],
        
        # การกระทำ
        'add_booking': ['จอง', 'เพิ่มจอง', 'new booking', 'book'],
        'add_guest': ['เพิ่มลูก', 'ลูกค้าใหม่', 'new guest'],
        'update_status': ['อัปเดตสถานะ', 'เปลี่ยนสถานะ', 'update status'],
        'add_income': ['บันทึกรายรับ', 'เพิ่มรายรับ', 'add income'],
        
        # รายงาน
        'report': ['รายงาน', 'report', 'สรุป', 'summary', 'dashboard'],
        'help': ['ช่วย', 'help', 'ช่วยเหลือ', 'ทำอะไรได้'],
    }
    
    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in message:
                return intent
    
    return 'general'

# ============================================
# 💬 RESPONSE GENERATOR
# ============================================

def generate_response(intent, params=None):
    """สร้างคำตอบตาม intent"""
    
    if intent == 'search_room':
        result = query_database("""
            SELECT room_no, building, type, price_per_night 
            FROM rooms WHERE status = 'Available'
            ORDER BY building, room_no
        """)
        
        if result['success'] and result['rows']:
            response = "✅ <b>ห้องว่าง</b>\n\n"
            
            buildings = {}
            for row in result['rows']:
                b = row[1]
                if b not in buildings:
                    buildings[b] = []
                buildings[b].append(row)
            
            for b, rooms in buildings.items():
                response += f"🏢 <b>ตึก {b}</b>\n"
                for r in rooms:
                    response += f"• {r[0]} - {r[2]} (฿{r[3]:,.0f}/คืน)\n"
                response += "\n"
            
            return response
        return "✅ ไม่มีห้องว่างในขณะนี้"
    
    elif intent == 'search_guest':
        if params:
            query = params.get('query', '')
            result = query_database("""
                SELECT guest_id, name, phone, country
                FROM guests 
                WHERE name LIKE ? OR phone LIKE ?
                LIMIT 10
            """, (f'%{query}%', f'%{query}%'))
            
            if result['success'] and result['rows']:
                response = f"👥 <b>ผลการค้นหา: {query}</b>\n\n"
                for row in result['rows']:
                    response += f"• <b>{row[1]}</b>\n"
                    response += f"  📱 {row[2]}\n"
                    response += f"  🌍 {row[3]}\n\n"
                return response
            return f"❌ ไม่พบลูกค้าที่ค้นหา: {query}"
        return "🔍 พิมชื่อลูกค้าที่ต้องการค้นหา"
    
    elif intent == 'room_info':
        if params:
            room_no = params.get('room', '')
            result = query_database("""
                SELECT room_no, building, floor, type, price_per_night, status
                FROM rooms WHERE room_no = ?
            """, (room_no,))
            
            if result['success'] and result['rows']:
                r = result['rows'][0]
                response = f"""📋 <b>ข้อมูลห้อง {r[0]}</b>

🏢 ตึก: {r[1]}
📐 ชั้น: {r[2]}
🛏️ ประเภท: {r[3]}
💰 ราคา: ฿{r[4]:,.0f}/คืน
📊 สถานะ: {r[5]}"""
                return response
            return f"❌ ไม่พบห้อง {room_no}"
        return "🔍 ระบุหมายเลขห้อง"
    
    elif intent == 'revenue':
        result = query_database("""
            SELECT 
                strftime('%Y-%m', check_in) as month,
                COUNT(*) as bookings,
                SUM(total_amount) as revenue
            FROM bookings
            WHERE check_in >= date('now', '-6 months')
            GROUP BY month
            ORDER BY month DESC
        """)
        
        if result['success'] and result['rows']:
            response = "📈 <b>สรุปรายได้ 6 เดือนล่าสุด</b>\n\n"
            for row in result['rows']:
                response += f"📅 {row[0]}: {row[1]} จอง, ฿{row[2]:,.0f}\n"
            return response
        return "❌ ไม่พบข้อมูล"
    
    elif intent == 'report':
        # Get stats
        stats_result = query_database("""
            SELECT 
                (SELECT COUNT(*) FROM rooms WHERE status = 'Available') as available,
                (SELECT COUNT(*) FROM rooms) as total,
                (SELECT SUM(total_amount) FROM bookings WHERE strftime('%Y-%m', check_in) = strftime('%Y-%m', 'now')) as month_revenue,
                (SELECT COUNT(*) FROM guests) as guests
        """)
        
        if stats_result['success']:
            r = stats_result['rows'][0]
            response = f"""📊 <b>รายงานวิพัฒน์โฮเทล</b>

📅 {datetime.now().strftime('%d/%m/%Y')}

🛏️ <b>ห้อง:</b> {r[0]}/{r[1]} ว่าง
💰 <b>รายได้เดือนนี้:</b> ฿{r[2]:,.0f}
👥 <b>ลูกค้าทั้งหมด:</b> {r[3]} คน"""
            return response
        return "❌ ไม่สามารถดึงข้อมูลได้"
    
    elif intent == 'help':
        return """🤖 <b>คำสั่งที่รองรับ</b>

📋 <b>ค้นหา:</b>
• "ห้องว่าง" - ดูห้องว่าง
• "ค้นหาลูก [ชื่อ]" - ค้นหาลูกค้า
• "ข้อมูลห้อง [เลขห้อง]" - ดูข้อมูลห้อง

📝 <b>การจอง:</b>
• "จองห้อง [เลขห้อง] วันที่ [YYYY-MM-DD] [จำนวนคืน]" 

💰 <b>รายได้:</b>
• "รายได้" - ดูรายได้
• "รายงาน" - ดูรายงาน

❓ <b>อื่นๆ:</b>
• "ช่วย" - แสดงคำสั่งทั้งหมด"""
    
    elif intent == 'add_booking':
        if params:
            result = execute_action('add_booking', params)
            if result['success']:
                return f"✅ {result['message']}\n\n📋 รายละเอียด:\n• ห้อง: {params[1]}\n• Check-in: {params[3]}\n• คืน: {params[5]}"
            return f"❌ {result.get('error', 'เกิดข้อผิดพลาด')}"
        return "📝 ระบุ: ห้อง, วันที่, จำนวนคืน"
    
    else:
        return """👋 สวัสดีครับ!

ผมคือ <b>Umi</b> ผู้ช่วยอัจฉริยะของวิพัฒน์โฮเทล

💬 สั่งงานได้เลย:
• "ห้องว่าง" - ดูห้องว่าง
• "จองห้อง A101 วันที่ 2026-03-05 2 คืน"
• "รายงาน" - ดูรายงาน
• "ช่วย" - ดูคำสั่งทั้งหมด"""

# ============================================
# 🎬 MAIN HANDLER
# ============================================

def process_message(message, user_context=None):
    """
    ประมวลผลข้อความและตอบกลับ
    """
    # 1. ตรวจจับ intent
    intent = detect_intent(message)
    
    # 2. ดึง parameters
    params = extract_params(message, intent)
    
    # 3. Generate response
    response = generate_response(intent, params)
    
    return {
        'intent': intent,
        'params': params,
        'response': response,
        'timestamp': datetime.now().isoformat()
    }

def extract_params(message, intent):
    """ดึง parameters จากข้อความ"""
    params = {}
    
    # ห้อง
    room_match = re.search(r'([ABabNn]\d{1,3})', message)
    if room_match:
        params['room'] = room_match.group(1).upper()
    
    # วันที่
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
    if date_match:
        params['date'] = date_match.group(1)
    
    # จำนวนคืน
    night_match = re.search(r'(\d+)\s*คืน', message)
    if night_match:
        params['nights'] = int(night_match.group(1))
    
    # Query สำหรับค้นหา
    if intent == 'search_guest':
        # ดึงชื่อที่ต้องการค้นหา
        query_match = re.search(r'(?:ค้นหา|หา|search)\s*(?:ลูก\s*)?(.+)', message)
        if query_match:
            params['query'] = query_match.group(1).strip()
    
    return params

# ============================================
# 🧪 TEST
# ============================================

if __name__ == "__main__":
    print("🧠 Hotel AI Agent Test")
    print("=" * 50)
    
    # Test messages
    test_messages = [
        "ห้องว่าง",
        "ค้นหาลูก สมชาย",
        "ข้อมูลห้อง A101",
        "รายงาน",
        "ช่วย",
    ]
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        result = process_message(msg)
        print(f"🤖 Intent: {result['intent']}")
        print(f"💬 Response:\n{result['response'][:200]}...")
