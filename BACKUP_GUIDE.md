# 💾 คู่มือระบบ Backup - วิพัฒน์โฮเทล

## 📁 โครงสร้าง Backup

```
backups/
├── daily/          # Backup รายวัน (เก็บ 7 วัน)
├── weekly/         # Backup รายสัปดาห์ (เก็บ 4 สัปดาห์)
├── monthly/        # Backup รายเดือน (เก็บ 12 เดือน)
└── logs/           # บันทึกการ backup
```

---

## 🚀 การใช้งาน

### 1. สร้าง Backup ทันที

```bash
# Daily backup
python3 backup_manager.py backup --type daily

# Weekly backup  
python3 backup_manager.py backup --type weekly

# Monthly backup
python3 backup_manager.py backup --type monthly
```

### 2. ดูรายการ Backup

```bash
# ดูทั้งหมด
python3 backup_manager.py list

# ดูเฉพาะรายเดือน
python3 backup_manager.py list --type monthly
```

### 3. กู้คืนข้อมูล

```bash
# กู้คืนจาก backup
python3 backup_manager.py restore --file backup_daily_2026-03-01.db.gz
```

### 4. ลบ backup เก่า

```bash
# ลบ daily เก่า (เก็บแค่ 7 ไฟล์)
python3 backup_manager.py clean --type daily --keep 7
```

### 5. สรุป Backup

```bash
python3 backup_manager.py summary
```

---

## 🔍 ค้นหาข้อมูลจาก Backup

### ดูรายการ Backup

```bash
python3 query_backup.py --list
python3 query_backup.py --list --type monthly
```

### ค้นหาจากวันที่

```bash
# หา backup ที่ใกล้ที่สุดกับ 2026-01-15
python3 query_backup.py --date 2026-01-15
```

### Query ข้อมูล

```bash
# ดูห้องทั้งหมด
python3 query_backup.py --sql "SELECT * FROM rooms"

# ดูห้องว่าง
python3 query_backup.py --sql "SELECT * FROM rooms WHERE status = 'Available'"

# ดูการจองเดือนที่แล้ว
python3 query_backup.py --sql "SELECT * FROM bookings WHERE check_in LIKE '2026-01%'"

# ดูลูกค้า
python3 query_backup.py --sql "SELECT * FROM guests LIMIT 20"

# ดูรายรับ
python3 query_backup.py --sql "SELECT * FROM clean_transactions LIMIT 10"
```

---

## ⏰ ตั้ง Cron (Auto Backup)

### ติดตั้ง Cron Job

```bash
# เปิด crontab
crontab -e

# เพิ่มบรรทัดนี้ (รันทุกวัน เที่ยง)
0 12 * * * /data/data/com.termux/files/home/.openclaw/workspace/auto_backup.sh
```

### ตรวจสอบ Cron

```bash
# ดู cron ที่มี
crontab -l

# ดู log
cat /data/data/com.termux/files/home/.openclaw/workspace/backups/logs/auto_backup.log
```

---

## 📊 สรุปการตั้งค่า

| ประเภท | ความถี่ | เก็บไว้ |
|--------|---------|----------|
| Daily | ทุกวัน เที่ยง | 7 วัน |
| Weekly | ทุกวันจันทร์ | 4 สัปดาห์ |
| Monthly | ทุกเดือน | 12 เดือน |

---

## 🛠️ ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | หน้าที่ |
|--------|---------|
| `backup_manager.py` | จัดการ backup |
| `query_backup.py` | ค้นหาข้อมูลจาก backup |
| `auto_backup.sh` | รัน auto backup |

---

*💾 วิพัฒน์โฮเทล | OpenClaw System*
