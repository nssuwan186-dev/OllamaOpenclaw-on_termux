#!/usr/bin/env python3
"""
report_generator.py — สร้างรายงาน HTML สวยงามสำหรับโรงแรม
วิพัฒน์โฮเทล · OpenClaw System
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"
OUTPUT_DIR = "/data/data/com.termux/files/home/.openclaw/workspace/reports"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_stats():
    """ดึงสถิติหลัก"""
    conn = get_connection()
    c = conn.cursor()
    
    # Rooms
    c.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Available'")
    available_rooms = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Monthly'")
    monthly_rooms = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Under Maintenance'")
    maintenance_rooms = c.fetchone()[0]
    
    # Today's bookings
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    c.execute("""
        SELECT COUNT(*) FROM bookings 
        WHERE check_in <= ? AND check_out > ?
    """, (today, today))
    occupied_today = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM bookings WHERE check_in = ?", (today,))
    check_ins_today = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM bookings WHERE check_out = ?", (today,))
    check_outs_today = c.fetchone()[0]
    
    # Revenue
    c.execute("""
        SELECT SUM(total_amount) FROM bookings 
        WHERE check_in >= ? AND check_in <= ?
    """, (yesterday, today))
    today_revenue = c.fetchone()[0] or 0
    
    c.execute("""
        SELECT SUM(total_amount) FROM bookings 
        WHERE strftime('%Y-%m', check_in) = strftime('%Y-%m', 'now')
    """)
    month_revenue = c.fetchone()[0] or 0
    
    # Guests
    c.execute("SELECT COUNT(*) FROM guests")
    total_guests = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'monthly_rooms': monthly_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupied_today': occupied_today,
        'check_ins_today': check_ins_today,
        'check_outs_today': check_outs_today,
        'today_revenue': today_revenue,
        'month_revenue': month_revenue,
        'total_guests': total_guests,
        'today': today
    }

def get_recent_bookings(limit=10):
    """ดึงการจองล่าสุด"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT b.room_no, g.name, b.check_in, b.check_out, b.nights, b.total_amount, b.status
        FROM bookings b
        LEFT JOIN guests g ON b.guest_id = g.guest_id
        ORDER BY b.check_in DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_available_rooms_list():
    """ดึงห้องว่าง"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT room_no, building, floor, type, price_per_night
        FROM rooms
        WHERE status = 'Available'
        ORDER BY building, floor, room_no
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def get_rooms_by_building():
    """ดึงห้องตามตึก"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT building, 
               COUNT(*) as total,
               SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) as available,
               SUM(CASE WHEN status = 'Monthly' THEN 1 ELSE 0 END) as monthly,
               SUM(CASE WHEN status = 'Under Maintenance' THEN 1 ELSE 0 END) as maintenance
        FROM rooms
        GROUP BY building
        ORDER BY building
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def generate_html_report():
    """สร้างรายงาน HTML"""
    stats = get_stats()
    recent = get_recent_bookings(10)
    available = get_available_rooms_list()
    buildings = get_rooms_by_building()
    
    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>รายงานวิพัฒน์โฮเทล - {stats['today']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: white; text-align: center; margin-bottom: 10px; }}
        .date {{ color: #ddd; text-align: center; margin-bottom: 30px; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-icon {{ font-size: 40px; margin-bottom: 10px; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #333; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        
        .section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .section h2 {{ 
            color: #333; 
            margin-bottom: 20px; 
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #667eea; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        
        .revenue {{ color: #27ae60; font-weight: bold; }}
        .available {{ color: #27ae60; }}
        .occupied {{ color: #e67e22; }}
        .maintenance {{ color: #e74c3c; }}
        
        .building-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        .building-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        .building-name {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        
        .room-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 10px;
        }}
        .room-item {{
            background: #e8f5e9;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-weight: 500;
        }}
        
        .footer {{
            text-align: center;
            color: #ddd;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏨 รายงานวิพัฒน์โฮเทล</h1>
        <p class="date">📅 ข้อมูล ณ วันที่ {stats['today']}</p>
        
        <!-- Stats Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🛏️</div>
                <div class="stat-value">{stats['available_rooms']}/{stats['total_rooms']}</div>
                <div class="stat-label">ห้องว่าง</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📥</div>
                <div class="stat-value">{stats['check_ins_today']}</div>
                <div class="stat-label">Check-in วันนี้</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📤</div>
                <div class="stat-value">{stats['check_outs_today']}</div>
                <div class="stat-label">Check-out วันนี้</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💰</div>
                <div class="stat-value revenue">฿{stats['today_revenue']:,.0f}</div>
                <div class="stat-label">รายได้วันนี้</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-value revenue">฿{stats['month_revenue']:,.0f}</div>
                <div class="stat-label">รายได้เดือนนี้</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-value">{stats['total_guests']}</div>
                <div class="stat-label">ลูกค้าทั้งหมด</div>
            </div>
        </div>
        
        <!-- Rooms by Building -->
        <div class="section">
            <h2>📊 สถานะห้องตามตึก</h2>
            <div class="building-grid">
"""
    
    for b in buildings:
        html += f"""
                <div class="building-card">
                    <div class="building-name">ตึก {b[0]}</div>
                    <p>📦 ทั้งหมด: <strong>{b[1]}</strong></p>
                    <p class="available">✅ ว่าง: {b[2]}</p>
                    <p>🗓️ รายเดือน: {b[3]}</p>
                    <p class="maintenance">🔧 ปิดปรับปรุง: {b[4]}</p>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <!-- Available Rooms -->
        <div class="section">
            <h2>✅ ห้องว่าง ("""
    html += f"{len(available)}"
    html += """ ห้อง)</h2>
            <div class="room-list>
"""
    
    for room in available:
        html += f'<div class="room-item">{room[0]}<br><small>{room[3]}</small></div>'
    
    html += """
            </div>
        </div>
        
        <!-- Recent Bookings -->
        <div class="section">
            <h2>📋 การจองล่าสุด</h2>
            <table>
                <thead>
                    <tr>
                        <th>ห้อง</th>
                        <th>ลูกค้า</th>
                        <th>เช็คอิน</th>
                        <th>เช็คเอาท์</th>
                        <th>คืน</th>
                        <th>ยอด</th>
                        <th>สถานะ</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for b in recent:
        html += f"""
                    <tr>
                        <td><strong>{b[0]}</strong></td>
                        <td>{b[1]}</td>
                        <td>{b[2]}</td>
                        <td>{b[3]}</td>
                        <td>{b[4]}</td>
                        <td class="revenue">฿{b[5]:,.0f}</td>
                        <td>{b[6]}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>🤖 ระบบ AI ผู้ช่วยวิพัฒน์โฮเทล</p>
            <p>สร้างเมื่อ """
    html += datetime.now().strftime('%Y-%m-%d %H:%M')
    html += """</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def generate_daily_report():
    """สail รายงานประจำวัน"""
    stats = get_stats()
    available = get_available_rooms_list()
    
    filename = f"{OUTPUT_DIR}/daily_report_{stats['today']}.html"
    html = generate_html_report()
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename, stats

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='สร้างรายงาน HTML')
    parser.add_argument('--type', choices=['daily', 'full'], default='daily',
                        help='ประเภทรายงาน')
    
    args = parser.parse_args()
    
    print("📊 กำลังสร้างรายงาน...")
    print("=" * 50)
    
    if args.type == 'daily':
        filename, stats = generate_daily_report()
        print(f"✅ สำเร็จ!")
        print(f"📁 ไฟล์: {filename}")
        print(f"📈 ห้องว่าง: {stats['available_rooms']}/{stats['total_rooms']}")
        print(f"💰 รายได้วันนี้: ฿{stats['today_revenue']:,.0f}")
        print(f"💵 รายได้เดือนนี้: ฿{stats['month_revenue']:,.0f}")
