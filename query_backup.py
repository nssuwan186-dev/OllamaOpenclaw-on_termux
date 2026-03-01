#!/usr/bin/env python3
"""
query_backup.py — ค้นหาข้อมูลจาก Backup
วิพัฒน์โฮเทล · OpenClaw System

ใช้ค้นหาข้อมูลเก่าได้ง่าย
"""

import sqlite3
import os
import gzip
from datetime import datetime

BACKUP_DIR = "/data/data/com.termux/files/home/.openclaw/workspace/backups"

def find_backup(backup_type=None, date=None):
    """หาไฟล์ backup ที่ต้องการ"""
    import glob
    
    patterns = []
    if backup_type:
        patterns.append(f"{BACKUP_DIR}/{backup_type}/*.gz")
    else:
        patterns.extend([
            f"{BACKUP_DIR}/daily/*.gz",
            f"{BACKUP_DIR}/weekly/*.gz",
            f"{BACKUP_DIR}/monthly/*.gz"
        ])
    
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    
    # เรียงลำดับตามวันที่
    files.sort(reverse=True)
    
    if date:
        # หา backup ที่ใกล้ที่สุดกับวันที่ที่ต้องการ
        target = datetime.strptime(date, '%Y-%m-%d')
        closest = None
        closest_diff = float('inf')
        
        for f in files:
            # ดึงวันที่จากชื่อไฟล์
            basename = os.path.basename(f)
            try:
                if 'daily' in basename:
                    file_date = datetime.strptime(basename.replace('backup_daily_', '').replace('.db.gz', ''), '%Y-%m-%d')
                elif 'weekly' in basename:
                    file_date = datetime.strptime(basename.replace('backup_weekly_W', '').split('_')[1], '%Y-%m-%d')
                elif 'monthly' in basename:
                    file_date = datetime.strptime(basename.replace('backup_monthly_', '').replace('.db.gz', ''), '%Y-%m')
                    file_date = file_date.replace(day=1)
                
                diff = abs((file_date - target).days)
                if diff < closest_diff:
                    closest_diff = diff
                    closest = f
            except:
                pass
        
        return [closest] if closest else []
    
    return files

def query_backup(backup_file, sql, params=None):
    """Query ข้อมูลจาก backup"""
    # สร้างไฟล์ชั่วคราว
    temp_db = "/tmp/query_backup_temp.db"
    
    # unzip
    with gzip.open(backup_file, 'rb') as f_in:
        with open(temp_db, 'wb') as f_out:
            f_out.write(f_in.read())
    
    # Query
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    
    if params:
        c.execute(sql, params)
    else:
        c.execute(sql)
    
    results = c.fetchall()
    
    # Get column names
    column_names = [description[0] for description in c.description] if c.description else []
    
    conn.close()
    
    # ลบไฟล์ชั่วคราว
    os.remove(temp_db)
    
    return column_names, results

def format_results(columns, rows, limit=50):
    """จัดรูปแบบผลลัพธ์"""
    if not rows:
        return "ไม่พบข้อมูล"
    
    # Limit
    rows = rows[:limit]
    
    # หาความกว้างของแต่ละคอลัมน์
    widths = [len(str(c)) for c in columns]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))
    
    # สร้างตาราง
    lines = []
    
    # Header
    header = " | ".join(str(col).ljust(widths[i]) for i, col in enumerate(columns))
    lines.append(header)
    lines.append("-" * len(header))
    
    # Rows
    for row in rows:
        line = " | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row))
        lines.append(line)
    
    if len(rows) >= limit:
        lines.append(f"... (แสดง {limit} รายการแรก)")
    
    return "\n".join(lines)

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ค้นหาข้อมูลจาก Backup')
    parser.add_argument('--type', choices=['daily', 'weekly', 'monthly'],
                        help='ประเภท backup')
    parser.add_argument('--date', help='วันที่ (YYYY-MM-DD)')
    parser.add_argument('--sql', help='SQL query')
    parser.add_argument('--limit', type=int, default=50, help='จำนวนผลลัพธ์')
    parser.add_argument('--list', action='store_true', help='แสดงรายการ backup')
    
    args = parser.parse_args()
    
    print("🔍 ระบบค้นหาข้อมูลจาก Backup")
    print("=" * 50)
    
    if args.list:
        files = find_backup(args.type, args.date)
        print(f"📋 พบ {len(files)} ไฟล์:")
        for f in files[:10]:
            print(f"   - {os.path.basename(f)}")
    
    elif args.sql:
        files = find_backup(args.type, args.date)
        
        if not files:
            print("❌ ไม่พบไฟล์ backup")
        else:
            print(f"🔍 ค้นหาจาก: {os.path.basename(files[0])}")
            print("")
            
            columns, rows = query_backup(files[0], args.sql)
            print(format_results(columns, rows, args.limit))
    
    else:
        # แสดงตัวอย่าง
        print("📋 ตัวอย่างการใช้งาน:")
        print("")
        print("# 1. ดูรายการ backup")
        print("   python3 query_backup.py --list")
        print("")
        print("# 2. ดูรายการ backup ประจำเดือน")
        print("   python3 query_backup.py --list --type monthly")
        print("")
        print("# 3. ค้นหาจาก backup ที่ใกล้ที่สุดกับวันที่ 2026-01-15")
        print("   python3 query_backup.py --date 2026-01-15")
        print("")
        print("# 4. Query ข้อมูลจาก backup")
        print('   python3 query_backup.py --sql "SELECT * FROM rooms LIMIT 5"')
        print("")
        print("# 5. Query ห้องว่างจาก backup เดือนที่แล้ว")
        print("   python3 query_backup.py --type monthly --sql \"SELECT * FROM rooms WHERE status = 'Available' LIMIT 10\"")
