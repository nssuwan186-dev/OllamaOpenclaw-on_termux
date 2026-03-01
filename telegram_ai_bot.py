#!/usr/bin/env python3
"""
telegram_ai_bot.py — Telegram Bot ที่มี AI สมอง
วิพัฒน์โฮเทล · OpenClaw System
"""

import os
import json
from datetime import datetime

# Import from same directory
from hotel_ai_agent import process_message
from vision_analyzer import analyze_and_save
from report_generator import generate_daily_report

# Config
BOT_TOKEN = "7736033828:AAH1PzHinXxjrWoAI0EQGC2_3Fes_zIKeXE"
ALLOWED_USERS = [7736033828, 8144545476]

# ============================================
# 📱 TELEGRAM FUNCTIONS
# ============================================

def send_message(chat_id, text):
    """ส่งข้อความกลับไป Telegram"""
    import requests
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    try:
        requests.post(url, json=data, timeout=10)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def send_photo(chat_id, photo_path, caption=None):
    """ส่งรูปภาพกลับไป Telegram"""
    import requests
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': caption or ''}
            requests.post(url, files=files, data=data, timeout=30)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def handle_message(chat_id, text):
    """จัดการข้อความ"""
    
    # Commands
    if text.startswith('/'):
        if text == '/start':
            response = """🏨 <b>ยินดีต้อนรับสู่วิพัฒน์โฮเทล!</b>

ผมคือ <b>Umi</b> ผู้ช่วย AI

💬 พิมพ์สิ่งที่ต้องการ:
• "ห้องว่าง"
• "รายงาน"
• "ช่วย"

📷 ส่งรูปภาพมาได้เลย!"""
            send_message(chat_id, response)
            return
        
        elif text == '/help':
            response = """🤖 <b>คำสั่ง</b>

/start - เริ่มต้น
/dashboard - สถานะ
/rooms - ห้องว่าง
/report - รายงาน
/help - ช่วย"""
            send_message(chat_id, response)
            return
        
        elif text == '/dashboard':
            result = process_message("รายงาน")
            send_message(chat_id, result['response'])
            return
        
        elif text == '/rooms':
            result = process_message("ห้องว่าง")
            send_message(chat_id, result['response'])
            return
        
        elif text == '/report':
            try:
                filename, stats = generate_daily_report()
                caption = f"""📊 <b>รายงาน</b>
ห้องว่าง: {stats['available_rooms']}/{stats['total_rooms']}
รายได้เดือนนี้: ฿{stats['month_revenue']:,.0f}"""
                send_photo(chat_id, filename, caption)
            except Exception as e:
                send_message(chat_id, f"Error: {e}")
            return
    
    # ส่งให้ AI
    result = process_message(text)
    send_message(chat_id, result['response'])

def handle_photo(chat_id, file_id):
    """จัดการรูปภาพ"""
    
    # Download
    import requests
    
    # Get file
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    response = requests.get(url)
    
    if not response.ok:
        send_message(chat_id, "❌ ไม่สามารถดาวน์โหลดรูปได้")
        return
    
    file_path = response.json()['result']['file_path']
    
    # Download image
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    image_path = f"/tmp/slip_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    
    response = requests.get(url)
    with open(image_path, 'wb') as f:
        f.write(response.content)
    
    print(f"📷 Image: {image_path}")
    
    # Analyze
    send_message(chat_id, "🔍 กำลังวิเคราะห์...")
    
    result = analyze_and_save(image_path)
    
    if 'error' in result.get('analyzed', {}):
        send_message(chat_id, f"❌ Error: {result['analyzed']['error']}")
    else:
        a = result['analyzed']
        s = result.get('saved', {})
        
        response = f"""📊 <b>ผลวิเคราะห์</b>

📅 วันที่: {a.get('date', '-')}
💰 เงิน: ฿{a.get('amount', 0):,.0f}
🏠 ห้อง: {a.get('room_no', '-')}
📝 หมายเหตุ: {a.get('note', '-')}

{'✅ บันทึกแล้ว' if s.get('status') == 'success' else '❌ ไม่บันทึก'}"""
        
        send_message(chat_id, response)

# ============================================
# 🏃 MAIN (Manual Mode for Testing)
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("🏨 Hotel AI Bot - Test Mode")
    print("=" * 50)
    
    # Interactive test
    while True:
        try:
            text = input("\n👤 คุณ: ")
            if text.lower in ['exit', 'quit', 'ออก']:
                break
            
            result = process_message(text)
            print(f"\n🤖 Umi:")
            print(result['response'])
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
