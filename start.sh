#!/bin/bash
# Hotel Management System - Quick Start

cd /data/data/com.termux/files/home/.openclaw/workspace

echo "🏨 วิพัฒน์โฮเทล - กำลังเริ่มระบบ..."
echo "================================"

# Show menu
echo ""
echo "เลือกโหมด:"
echo "1. AI Agent (พิมพ์คำสั่งเอง)"
echo "2. Telegram Bot"
echo "3. ดูห้องว่าง"
echo "4. รายงาน"
echo "5. Backup"
echo "6. Security Scan"
echo ""

read -p "เลือก (1-6): " choice

case $choice in
  1) python3 hotel_ai_agent.py ;;
  2) python3 telegram_ai_bot.py ;;
  3) python3 query_rooms.py availability 2026-03-01 ;;
  4) python3 report_generator.py --type daily ;;
  5) python3 backup_manager.py backup --type daily ;;
  6) python3 /root/.opencode/caelguard-community/scripts/shellguard-scanner.py /data/data/com.termux/files/home/.openclaw/workspace --json ;;
  *) echo "ไม่ถูกต้อง" ;;
esac
