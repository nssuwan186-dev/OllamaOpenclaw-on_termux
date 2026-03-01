#!/usr/bin/env python3
"""
backup_manager.py — ระบบ Backup ข้อมูลอัตโนมัติ
วิพัฒน์โฮเทล · OpenClaw System

จัดเก็บ: /data/data/com.termux/files/home/.openclaw/workspace/backups/
"""

import sqlite3
import shutil
import os
import json
from datetime import datetime, timedelta
import gzip

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"
BACKUP_DIR = "/data/data/com.termux/files/home/.openclaw/workspace/backups"

# สร้างโฟลเดอร์ backup
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(f"{BACKUP_DIR}/daily", exist_ok=True)
os.makedirs(f"{BACKUP_DIR}/weekly", exist_ok=True)
os.makedirs(f"{BACKUP_DIR}/monthly", exist_ok=True)
os.makedirs(f"{BACKUP_DIR}/logs", exist_ok=True)

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_table_count(table_name):
    """นับจำนวนข้อมูลในตาราง"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = c.fetchone()[0]
    except:
        count = 0
    conn.close()
    return count

def get_database_stats():
    """ดึงสถิติฐานข้อมูล"""
    tables = ['rooms', 'bookings', 'guests', 'clean_transactions', 'fact_transactions']
    stats = {}
    
    for table in tables:
        stats[table] = get_table_count(table)
    
    return stats

def create_backup(backup_type='daily'):
    """
    สร้าง backup
    backup_type: 'daily', 'weekly', 'monthly'
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # ชื่อไฟล์ backup
    if backup_type == 'daily':
        filename = f"backup_daily_{date_str}.db"
    elif backup_type == 'weekly':
        week_num = datetime.now().isocalendar()[1]
        filename = f"backup_weekly_W{week_num}_{date_str}.db"
    else:  # monthly
        month_str = datetime.now().strftime('%Y-%m')
        filename = f"backup_monthly_{month_str}.db"
    
    backup_path = f"{BACKUP_DIR}/{backup_type}/{filename}"
    
    # คัดลอกไฟล์ database
    shutil.copy2(DB_PATH, backup_path)
    
    # บีบอัดด้วย gzip
    gzip_path = f"{backup_path}.gz"
    with open(backup_path, 'rb') as f_in:
        with gzip.open(gzip_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(backup_path)  # ลบไฟล์ไม่บีบอัด
    
    # สร้างไฟล์ manifest
    stats = get_database_stats()
    manifest = {
        'filename': f"{filename}.gz",
        'backup_type': backup_type,
        'created_at': datetime.now().isoformat(),
        'db_path': DB_PATH,
        'table_counts': stats
    }
    
    manifest_path = f"{BACKUP_DIR}/{backup_type}/{filename}.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # บันทึก log
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': backup_type,
        'file': f"{filename}.gz",
        'stats': stats
    }
    log_file = f"{BACKUP_DIR}/logs/backup_log.json"
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log_entry)
    
    # เก็บ log 30 รายการล่าสุด
    logs = logs[-30:]
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    
    return filename, stats

def list_backups(backup_type=None):
    """แสดงรายการ backup"""
    backups = []
    
    types = [backup_type] if backup_type else ['daily', 'weekly', 'monthly']
    
    for bt in types:
        backup_path = f"{BACKUP_DIR}/{bt}"
        if os.path.exists(backup_path):
            for f in sorted(os.listdir(backup_path)):
                if f.endswith('.json'):
                    with open(f"{backup_path}/{f}", 'r', encoding='utf-8') as file:
                        manifest = json.load(file)
                        backups.append({
                            'type': bt,
                            'file': manifest['filename'],
                            'created': manifest['created_at'],
                            'stats': manifest['table_counts']
                        })
    
    return backups

def restore_backup(backup_file, target_path=None):
    """กู้คืนข้อมูลจาก backup"""
    if not target_path:
        target_path = DB_PATH
    
    # หาข้อมูลไฟล์
    for bt in ['daily', 'weekly', 'monthly']:
        gz_path = f"{BACKUP_DIR}/{bt}/{backup_file}"
        if os.path.exists(gz_path):
            # unzip
            with gzip.open(gz_path, 'rb') as f_in:
                with open(target_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_in)
            
            return True, gz_path
    
    return False, "ไม่พบไฟล์ backup"

def clean_old_backups(backup_type='daily', keep=7):
    """ลบ backup เก่า"""
    backup_path = f"{BACKUP_DIR}/{backup_type}"
    
    if not os.path.exists(backup_path):
        return 0
    
    files = sorted(os.listdir(backup_path))
    files = [f for f in files if f.endswith('.json')]
    
    deleted = 0
    while len(files) > keep:
        f = files.pop(0)
        # ลบไฟล์ .json และ .gz
        base = f.replace('.json', '')
        for ext in ['.json', '.gz']:
            path = f"{backup_path}/{base}{ext}"
            if os.path.exists(path):
                os.remove(path)
                deleted += 1
    
    return deleted

def get_backup_summary():
    """สร้างสรุป backup"""
    daily = len([f for f in os.listdir(f"{BACKUP_DIR}/daily") if f.endswith('.json')])
    weekly = len([f for f in os.listdir(f"{BACKUP_DIR}/weekly") if f.endswith('.json')])
    monthly = len([f for f in os.listdir(f"{BACKUP_DIR}/monthly") if f.endswith('.json')])
    
    log_file = f"{BACKUP_DIR}/logs/backup_log.json"
    last_backup = "ไม่เคย"
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            if logs:
                last_backup = logs[-1]['timestamp']
    
    return {
        'daily_backups': daily,
        'weekly_backups': weekly,
        'monthly_backups': monthly,
        'last_backup': last_backup,
        'backup_dir': BACKUP_DIR
    }

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ระบบ Backup ข้อมูล')
    parser.add_argument('command', choices=['backup', 'list', 'restore', 'clean', 'summary'],
                        help='คำสั่ง')
    parser.add_argument('--type', choices=['daily', 'weekly', 'monthly'], default='daily',
                        help='ประเภท backup')
    parser.add_argument('--file', help='ไฟล์ที่ต้องการกู้คืน')
    parser.add_argument('--keep', type=int, default=7, help='จำนวน backup ที่เก็บ')
    
    args = parser.parse_args()
    
    print("💾 ระบบ Backup ข้อมูล - วิพัฒน์โฮเทล")
    print("=" * 50)
    
    if args.command == 'backup':
        filename, stats = create_backup(args.type)
        print(f"✅ Backup สำเร็จ: {filename}")
        print(f"📊 จำนวนข้อมูล:")
        for table, count in stats.items():
            print(f"   - {table}: {count}")
    
    elif args.command == 'list':
        backups = list_backups()
        print(f"📋 รายการ Backup ({len(backups)} ไฟล์)")
        for b in reversed(backups[-10:]):
            print(f"   [{b['type']}] {b['file']} - {b['created'][:10]}")
    
    elif args.command == 'restore':
        if not args.file:
            print("❌ กรุณาระบุชื่อไฟล์ที่ต้องการกู้คืน")
        else:
            success, msg = restore_backup(args.file)
            if success:
                print(f"✅ กู้คืนสำเร็จ: {msg}")
            else:
                print(f"❌ {msg}")
    
    elif args.command == 'clean':
        deleted = clean_old_backups(args.type, args.keep)
        print(f"✅ ลบ backup เก่า {deleted} ไฟล์")
    
    elif args.command == 'summary':
        summary = get_backup_summary()
        print(f"📊 สรุป Backup")
        print(f"   Daily: {summary['daily_backups']}")
        print(f"   Weekly: {summary['weekly_backups']}")
        print(f"   Monthly: {summary['monthly_backups']}")
        print(f"   Last: {summary['last_backup']}")
        print(f"   Path: {summary['backup_dir']}")
