#!/usr/bin/env python3
"""
vision_analyzer.py — ระบบวิเคราะห์รูปภาพด้วย AI
วิพัฒน์โฮเทล · OpenClaw System

รองรับ:
1. Ollama Vision (kimi-k2.5, llava)
2. Google Gemini Vision
3. OpenAI GPT-4 Vision
"""

import sqlite3
import json
import os
import re
from datetime import datetime

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

# ============================================
# 🎯 ANALYZER FUNCTIONS
# ============================================

def analyze_slip_ollama(image_path):
    """
    วิเคราะห์สลิปด้วย Ollama (Vision)
    """
    import base64
    
    # อ่านรูปภาพ
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Prompt สำหรับวิเคราะห์สลิป
    prompt = """วิเคราะห์สลิปโอนเงินนี้และส่งข้อมูลในรูปแบบ JSON:
{
  "date": "วันที่ในสลิป (YYYY-MM-DD)",
  "amount": "จำนวนเงิน (ตัวเลข)",
  "from_account": "ชื่อบัญชีต้นทาง",
  "to_account": "ชื่อบัญชีปลายทาง", 
  "reference": "เลขที่อ้างอิง",
  "room_no": "หมายเลขห้อง (ถ้ามี)",
  "note": "หมายเหตุอื่นๆ"
}

ถ้าไม่พบข้อมูลให้ใส่ null"""

    # เรียก Ollama API
    import requests
    
    try:
        response = requests.post(
            'http://127.0.0.1:11434/api/generate',
            json={
                'model': 'llava:7b',
                'prompt': prompt,
                'images': [image_data],
                'stream': False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return parse_ai_response(result.get('response', ''))
        else:
            return {'error': f'Ollama error: {response.status_code}'}
    
    except Exception as e:
        return {'error': str(e)}

def analyze_slip_gemini(image_path, api_key=None):
    """
    วิเคราะห์สลิปด้วย Google Gemini Vision
    """
    import requests
    
    # อ่านรูปภาพ
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    prompt = """วิเคราะห์สลิปโอนเงินนี้และส่งข้อมูลในรูปแบบ JSON ที่สมบูรณ์:
{
  "date": "วันที่ในสลิป (YYYY-MM-DD)",
  "amount": "จำนวนเงิน (ตัวเลข)",
  "from_account": "ชื่อบัญชีต้นทาง",
  "to_account": "ชื่อบัญชีปลายทาง", 
  "reference": "เลขที่อ้างอิง",
  "room_no": "หมายเลขห้อง (ถ้ามี)",
  "note": "หมายเหตุอื่นๆ"
}

ถ้าไม่พบข้อมูลให้ใส่ null"""

    try:
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}',
            json={
                'contents': [{
                    'parts': [
                        {'text': prompt},
                        {'inline_data': {
                            'mime_type': 'image/jpeg',
                            'data': image_data
                        }}
                    ]
                }]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            return parse_ai_response(text)
        else:
            return {'error': f'Gemini error: {response.status_code}'}
    
    except Exception as e:
        return {'error': str(e)}

def parse_ai_response(text):
    """
    แปลงข้อความที่ AI ส่งมาเป็น JSON
    """
    # หา JSON ในข้อความ
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    
    if json_match:
        try:
            data = json.loads(json_match.group())
            
            # ทำความสะอาดข้อมูล
            result = {}
            
            # วันที่
            date_str = data.get('date', '')
            if date_str:
                result['date'] = parse_date(date_str)
            else:
                result['date'] = None
            
            # จำนวนเงิน
            amount = data.get('amount', 0)
            if isinstance(amount, str):
                # ลบเครื่องหมายจุลภาคและคำ
                amount = re.sub(r'[^\d.]', '', str(amount))
            result['amount'] = float(amount) if amount else 0
            
            # ข้อมูลอื่นๆ
            result['from_account'] = data.get('from_account', '')
            result['to_account'] = data.get('to_account', '')
            result['reference'] = data.get('reference', '')
            result['room_no'] = extract_room_number(data.get('room_no', '') or data.get('note', ''))
            result['note'] = data.get('note', '')
            
            return result
            
        except json.JSONDecodeError:
            return {'error': 'Cannot parse JSON', 'raw': text}
    
    return {'error': 'No JSON found', 'raw': text}

def parse_date(date_str):
    """
    แปลงวันที่หลายรูปแบบเป็น YYYY-MM-DD
    """
    date_str = date_str.strip()
    
    # รูปแบบที่รองรับ
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%m/%d/%Y',
        '%Y/%m/%d',
        '%d %B %Y',
        '%d %b %Y',
    ]
    
    # ลองทุกรูปแบบ
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except:
            continue
    
    # ถ้าไม่ได้ลองหาจาก regex
    # รูปแบบ 31/01/2026
    match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})', date_str)
    if match:
        day, month, year = match.groups()
        if len(year) == 2:
            year = '20' + year if int(year) < 50 else '19' + year
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    return date_str

def extract_room_number(text):
    """
    หาหมายเลขห้องจากข้อความ
    """
    # รูปแบบ: A101, B106, N1, etc.
    patterns = [
        r'([ABN]\d{1,3})',
        r'ห้อง\s*([ABN]\d{1,3})',
        r'ห\.?\s*([ABN]\d{1,3})',
        r'Room\s*([ABN]\d{1,3})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    
    return ''

# ============================================
# 💾 DATABASE FUNCTIONS
# ============================================

def get_connection():
    return sqlite3.connect(DB_PATH)

def save_transaction(data, source='vision'):
    """
    บันทึกข้อมูลลงฐานข้อมูล
    """
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # หาห้องจาก room_no
        room_no = data.get('room_no', '')
        
        # บันทึกลง clean_transactions
        c.execute("""
            INSERT INTO clean_transactions (trans_id, date, room_no, guest_name, amount, payment_method, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"TRANS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            data.get('date'),
            room_no,
            data.get('from_account', ''),
            data.get('amount', 0),
            data.get('to_account', ''),
            source
        ))
        
        conn.commit()
        
        # อัปเดตสถานะห้องถ้ามี
        if room_no:
            c.execute("UPDATE rooms SET status = 'ไม่ว่าง' WHERE room_no = ?", (room_no,))
            conn.commit()
        
        conn.close()
        
        return {
            'status': 'success',
            'message': f'บันทึกข้อมูลสำเร็จ: ฿{data.get("amount", 0):,.0f}',
            'data': data
        }
    
    except Exception as e:
        conn.close()
        return {'status': 'error', 'message': str(e)}

# ============================================
# 🎨 MAIN ANALYZER
# ============================================

def analyze_image(image_path, method='auto'):
    """
    วิเคราะห์รูปภาพ
    
    method: 'ollama', 'gemini', 'auto'
    """
    if not os.path.exists(image_path):
        return {'error': 'ไม่พบไฟล์ภาพ'}
    
    # ตรวจสอบประเภทไฟล์
    allowed_types = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(image_path)[1].lower()
    
    if ext not in allowed_types:
        return {'error': f'ไม่รองรับไฟล์ประเภท {ext}'}
    
    # วิเคราะห์ตามวิธีที่เลือก
    if method == 'auto':
        # ลอง Ollama ก่อน
        result = analyze_slip_ollama(image_path)
        if 'error' in result:
            # ถ้าไม่ได้ใช้ Gemini
            # ต้องใส่ API key
            result = {'error': 'กรุณาตั้งค่า Vision API'}
        return result
    
    elif method == 'ollama':
        return analyze_slip_ollama(image_path)
    
    elif method == 'gemini':
        # ต้องใส่ API key ใน config
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if not api_key:
            return {'error': 'กรุณาตั้งค่า GEMINI_API_KEY'}
        return analyze_slip_gemini(image_path, api_key)
    
    return {'error': 'Unknown method'}

def analyze_and_save(image_path, method='auto'):
    """
    วิเคราะห์และบันทึกในขั้นตอนเดียว
    """
    # วิเคราะห์
    result = analyze_image(image_path, method)
    
    if 'error' in result:
        return result
    
    # บันทึก
    save_result = save_transaction(result)
    
    return {
        'analyzed': result,
        'saved': save_result
    }

# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='วิเคราะห์รูปภาพสลิป')
    parser.add_argument('image', help='Path to image file')
    parser.add_argument('--method', choices=['auto', 'ollama', 'gemini'], default='auto',
                        help='วิธีวิเคราะห์')
    parser.add_argument('--save', action='store_true', help='บันทึกลงฐานข้อมูล')
    
    args = parser.parse_args()
    
    print("🔍 กำลังวิเคราะห์รูปภาพ...")
    print("=" * 50)
    
    if args.save:
        result = analyze_and_save(args.image, args.method)
    else:
        result = analyze_image(args.image, args.method)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
