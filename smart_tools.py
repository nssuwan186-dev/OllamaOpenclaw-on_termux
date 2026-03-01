#!/usr/bin/env python3
"""
Smart Hotel Management Tools
ระบบจัดการโรงแรมอัจฉริยะ - รองรับคำสั่งภาษาธรรมชาติ
"""

import sqlite3
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

class CommandType(Enum):
    QUERY = "query"
    REPORT = "report"
    ANALYZE = "analyze"
    PREDICT = "predict"
    COMPARE = "compare"
    ACTION = "action"

@dataclass
class QueryResult:
    success: bool
    data: Any
    message: str
    sql: str = ""

class HotelAI:
    """AI ผู้ช่วยจัดการโรงแรมวิพัฒน์"""
    
    def __init__(self):
        self.db = DB_PATH
        self.context = {}
        
    def _connect(self):
        return sqlite3.connect(self.db)
    
    def understand_command(self, text: str) -> Dict[str, Any]:
        """วิเคราะห์คำสั่งภาษาธรรมชาติ"""
        text = text.lower()
        
        # ตรวจจับเจตนา
        patterns = {
            'available_rooms': r'(ห้องว่าง|available|ว่าง|ห้องไหนวาง)',
            'room_status': r'(สถานะห้อง|status|ห้อง.*เช็ค|เช็ค.*ห้อง)',
            'revenue': r'(รายรับ|revenue|income|เงินเข้า|ยอดขาย)',
            'guest_info': r'(ลูกค้า|guest|ข้อมูลคน|ค้นหาชื่อ)',
            'booking': r'(จอง|booking|reservation|การจอง)',
            'compare': r'(เปรียบเทียบ|compare|เทียบ|vs|กับ)',
            'trend': r'(แนวโน้ม|trend|พัฒนาการ|growth)',
            'top': r'(สูงสุด|top|best|hero|มากที่สุด)',
            'summary': r'(สรุป|summary|overview|ภาพรวม)'
        }
        
        intent = None
        for key, pattern in patterns.items():
            if re.search(pattern, text):
                intent = key
                break
        
        # ตรวจจับช่วงเวลา
        time_patterns = {
            'today': r'(วันนี้|today|now)',
            'yesterday': r'(เมื่อวาน|yesterday)',
            'this_week': r'(สัปดาห์นี้|this week|อาทิตย์นี้)',
            'this_month': r'(เดือนนี้|this month)',
            'last_month': r'(เดือนที่แล้ว|last month)',
            'year': r'(ปีนี้|ปีที่แล้ว|year|\d{4})'
        }
        
        time_range = 'all'
        for key, pattern in time_patterns.items():
            if re.search(pattern, text):
                time_range = key
                break
        
        # ตรวจจับตึก/ชั้น/ห้อง
        building = None
        if re.search(r'ตึก\s*([abn])', text):
            building = re.search(r'ตึก\s*([abn])', text).group(1).upper()
        
        room_match = re.search(r'([abn]\d{3})', text, re.IGNORECASE)
        room = room_match.group(1).upper() if room_match else None
        
        return {
            'intent': intent or 'unknown',
            'time_range': time_range,
            'building': building,
            'room': room,
            'original': text
        }
    
    def execute(self, command: str) -> QueryResult:
        """ประมวลผลคำสั่งและส่งผลลัพธ์"""
        parsed = self.understand_command(command)
        intent = parsed['intent']
        
        handlers = {
            'available_rooms': self.get_available_rooms,
            'room_status': self.get_room_status,
            'revenue': self.get_revenue,
            'guest_info': self.search_guest,
            'booking': self.get_bookings,
            'compare': self.compare_data,
            'trend': self.analyze_trend,
            'top': self.get_top_performers,
            'summary': self.get_summary
        }
        
        handler = handlers.get(intent, self.unknown_command)
        return handler(parsed)
    
    def get_available_rooms(self, parsed: Dict) -> QueryResult:
        """ดึงข้อมูลห้องว่าง"""
        conn = self._connect()
        building_filter = f"AND building = '{parsed['building']}'" if parsed['building'] else ""
        
        sql = f"""
        SELECT room_no, building, floor, type, price_per_night
        FROM rooms 
        WHERE status = 'Available' {building_filter}
        ORDER BY building, CAST(SUBSTR(room_no, 2) AS INTEGER)
        """
        
        df = conn.execute(sql).fetchall()
        conn.close()
        
        if not df:
            return QueryResult(True, [], "ไม่มีห้องว่างในขณะนี้ค่ะ", sql)
        
        rooms = [{"ห้อง": r[0], "ตึก": r[1], "ชั้น": r[2], "ประเภท": r[3], "ราคา": f"{r[4]} บาท"} for r in df]
        return QueryResult(True, rooms, f"พบห้องว่าง {len(rooms)} ห้องค่ะ", sql)
    
    def get_revenue(self, parsed: Dict) -> QueryResult:
        """ดึงข้อมูลรายรับ"""
        conn = self._connect()
        
        time_filters = {
            'today': "date = DATE('now')",
            'yesterday': "date = DATE('now', '-1 day')",
            'this_month': "strftime('%Y-%m', date) = strftime('%Y-%m', 'now')",
            'last_month': "strftime('%Y-%m', date) = strftime('%Y-%m', 'now', '-1 month')",
            'this_week': "date >= DATE('now', '-7 days')",
            'year': f"strftime('%Y', date) = '{datetime.now().year}'"
        }
        
        where_clause = time_filters.get(parsed['time_range'], "1=1")
        
        sql = f"""
        SELECT 
            COUNT(*) as จำนวนรายการ,
            SUM(amount) as รายรับรวม,
            AVG(amount) as ค่าเฉลี่ย,
            MIN(amount) as ต่ำสุด,
            MAX(amount) as สูงสุด
        FROM clean_transactions
        WHERE {where_clause}
        """
        
        result = conn.execute(sql).fetchone()
        conn.close()
        
        if result[0] == 0:
            return QueryResult(True, None, "ไม่มีรายรับในช่วงเวลานี้ค่ะ", sql)
        
        data = {
            "จำนวนรายการ": result[0],
            "รายรับรวม": f"{result[1]:,.0f} บาท",
            "ค่าเฉลี่ย": f"{result[2]:.0f} บาท",
            "ต่ำสุด": f"{result[3]:.0f} บาท",
            "สูงสุด": f"{result[4]:.0f} บาท"
        }
        
        msg = f"สรุปรายรับ ({parsed['time_range']})\n" + "\n".join([f"{k}: {v}" for k, v in data.items()])
        return QueryResult(True, data, msg, sql)
    
    def get_summary(self, parsed: Dict) -> QueryResult:
        """สรุปภาพรวมโรงแรม"""
        conn = self._connect()
        
        stats = {}
        
        # ห้อง
        c = conn.execute("SELECT COUNT(*), SUM(CASE WHEN status='Available' THEN 1 ELSE 0 END) FROM rooms")
        total, available = c.fetchone()
        stats['ห้องทั้งหมด'] = total
        stats['ห้องว่าง'] = available
        stats['ห้องไม่ว่าง'] = total - available
        
        # การจองวันนี้
        c = conn.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Active' AND check_in <= DATE('now') AND check_out >= DATE('now')")
        stats['เข้าพักวันนี้'] = c.fetchone()[0]
        
        # รายรับวันนี้
        c = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM clean_transactions WHERE date = DATE('now')")
        stats['รายรับวันนี้'] = f"{c.fetchone()[0]:,.0f} บาท"
        
        # รายรับเดือนนี้
        c = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM clean_transactions WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')")
        stats['รายรับเดือนนี้'] = f"{c.fetchone()[0]:,.0f} บาท"
        
        conn.close()
        
        message = """🏨 ภาพรวมวิพัฒน์โฮเทล

📊 ห้องพัก:
• ทั้งหมด: {ห้องทั้งหมด} ห้อง
• ว่าง: {ห้องว่าง} ห้อง | ไม่ว่าง: {ห้องไม่ว่าง} ห้อง

👥 การเข้าพัก:
• วันนี้: {เข้าพักวันนี้} ห้อง

💰 รายได้:
• วันนี้: {รายรับวันนี้}
• เดือนนี้: {รายรับเดือนนี้}""".format(**stats)
        
        return QueryResult(True, stats, message, "")
    
    def unknown_command(self, parsed: Dict) -> QueryResult:
        return QueryResult(False, None, f"อุ้มมิไม่เข้าใจคำสั่ง '{parsed['original']}' ค่ะ ลองถามใหม่ได้ไหมคะ?", "")

# CLI Interface
if __name__ == "__main__":
    import sys
    
    ai = HotelAI()
    
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        result = ai.execute(command)
        print(json.dumps({
            "success": result.success,
            "message": result.message,
            "data": result.data
        }, ensure_ascii=False, indent=2))
    else:
        print("Usage: python smart_tools.py 'คำสั่งของคุณ'")
        print("Example: python smart_tools.py 'ห้องว่างตึก A วันนี้'")
