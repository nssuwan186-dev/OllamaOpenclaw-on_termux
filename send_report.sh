#!/bin/bash
# send_report.sh — ส่งรายงาน HTML ผ่าน Telegram

REPORT_SCRIPT="/data/data/com.termux/files/home/.openclaw/workspace/report_generator.py"
REPORT_DIR="/data/data/com.termux/files/home/.openclaw/workspace/reports"
TODAY=$(date +%Y-%m-%d)
USER_ID="8144545476"  # เปลี่ยนเป็น ID ของคุณ

echo "📊 กำลังสร้างรายงานประจำวัน..."

# 1. สร้างรายงาน
python3 "$REPORT_SCRIPT" --type daily
REPORT_FILE="$REPORT_DIR/daily_report_$TODAY.html"

if [ ! -f "$REPORT_FILE" ]; then
    echo "❌ ไม่สามารถสร้างรายงานได้"
    exit 1
fi

# 2. อ่านข้อมูลสถิติสำหรับสร้างข้อความสรุป
STATS=$(python3 -c "
import sqlite3
from datetime import datetime

DB_PATH = '/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db'
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM rooms WHERE status = \"Available\"')
available = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM rooms')
total = c.fetchone()[0]

c.execute('''
    SELECT SUM(total_amount) FROM bookings 
    WHERE strftime(\"%Y-%m\", check_in) = strftime(\"%Y-%m\", \"now\")
''')
month_revenue = c.fetchone()[0] or 0

conn.close()

print(f'{available},{total},{month_revenue}')
")

AVAILABLE=$(echo $STATS | cut -d',' -f1)
TOTAL=$(echo $STATS | cut -d',' -f2)
REVENUE=$(echo $STATS | cut -d',' -f3)

# 3. สร้างข้อความสรุป
SUMMARY="🏨 <b>รายงานประจำวัน - $TODAY</b>

📊 <b>สถานะห้อง:</b>
• ห้องว่าง: $AVAILABLE / $TOTAL

💰 <b>รายได้เดือนนี้:</b>
• ฿$REVENUE

📄 <b>ดูรายงานฉบับเต็ม:</b>
<a href=\"file://$REPORT_FILE\">คลิกที่นี่</a>

🤖 วิพัฒน์โฮเทล"

# 4. ส่งข้อความ
echo "📤 กำลังส่งรายงานผ่าน Telegram..."

# ส่งเป็น HTML
/data/data/com.termux/files/usr/bin/openclaw message send \
    --target "$USER_ID" \
    --message "$SUMMARY"

# 5. ส่งไฟล์ HTML (ถ้าต้องการ)
/data/data/com.termux/files/usr/bin/openclaw message send \
    --target "$USER_ID" \
    --file "$REPORT_FILE"

echo "✅ ส่งรายงานสำเร็จ!"
echo "📁 ไฟล์: $REPORT_FILE"
