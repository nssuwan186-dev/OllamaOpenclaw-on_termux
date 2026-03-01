#!/usr/bin/env python3
"""
Hotel Manager Core - ระบบจัดการโรงแรมวิพัฒน์
"""

import sqlite3
import sys
import json
from datetime import datetime

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

class HotelCore:
    def __init__(self):
        self.db_path = DB_PATH
    
    def _query(self, sql, params=()):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.execute(sql, params)
            rows = cur.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_dashboard(self):
        rooms = self._query("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) as available FROM rooms")
        today = self._query("SELECT COALESCE(SUM(amount), 0) as total FROM clean_transactions WHERE date = DATE('now')")
        month = self._query("SELECT COALESCE(SUM(amount), 0) as total FROM clean_transactions WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')")
        return {
            "rooms": rooms[0] if rooms else {},
            "today_revenue": today[0] if today else {},
            "month_revenue": month[0] if month else {}
        }
    
    def get_available_rooms(self, building=None):
        sql = "SELECT room_no, building, floor, type, price_per_night FROM rooms WHERE status = 'Available'"
        if building:
            sql += f" AND building = '{building}'"
        sql += " ORDER BY building, room_no"
        rooms = self._query(sql)
        return {"count": len(rooms), "rooms": rooms}

def main():
    core = HotelCore()
    
    if len(sys.argv) < 2:
        print("คำสั่ง: dashboard | available [ตึก]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "dashboard":
        result = core.get_dashboard()
    elif cmd == "available":
        building = sys.argv[2] if len(sys.argv) > 2 else None
        result = core.get_available_rooms(building)
    else:
        result = {"error": "คำสั่งไม่รู้จัก"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
