#!/bin/bash
# auto_backup.sh — รันอัตโนมัติผ่าน Cron

BACKUP_SCRIPT="/data/data/com.termux/files/home/.openclaw/workspace/backup_manager.py"
LOG_FILE="/data/data/com.termux/files/home/.openclaw/workspace/backups/logs/auto_backup.log"

echo "========== $(date) ==========" >> $LOG_FILE

# Daily backup (ทุกวัน เที่ยง)
python3 $BACKUP_SCRIPT backup --type daily >> $LOG_FILE 2>&1

# Weekly backup (ทุกวันจันทร์)
if [ $(date +%u) -eq 1 ]; then
    python3 $BACKUP_SCRIPT backup --type weekly >> $LOG_FILE 2>&1
fi

# Monthly backup (วันที่ 1 ของเดือน)
if [ $(date +%d) -eq 01 ]; then
    python3 $BACKUP_SCRIPT backup --type monthly >> $LOG_FILE 2>&1
fi

# Clean old backups
python3 $BACKUP_SCRIPT clean --type daily --keep 7 >> $LOG_FILE 2>&1
python3 $BACKUP_SCRIPT clean --type weekly --keep 4 >> $LOG_FILE 2>&1
python3 $BACKUP_SCRIPT clean --type monthly --keep 12 >> $LOG_FILE 2>&1

echo "✅ Backup เสร็จสิ้น: $(date)" >> $LOG_FILE
