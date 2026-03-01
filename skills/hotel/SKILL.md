# Hotel Management Skill (v2.0)

Integrated with Caelguard Security for safe AI operations.

## Commands

### Room Management
- `ห้องว่าง` - Show available rooms
- `ห้อง [เลขห้อง]` - Room details
- `จองห้อง [เลขห้อง] วันที่ [YYYY-MM-DD] [จำนวนคืน]` - Book room

### Guest Management  
- `ค้นหาลูก [ชื่อ]` - Search guest
- `ข้อมูลลูกค้า [ชื่อ]` - Guest info

### Reports
- `รายงาน` - Daily report
- `รายงานเต็ม` - Full report
- `export csv` - Export to CSV

### System
- `backup` - Create backup
- `restore [ไฟล์]` - Restore from backup

### Security (Caelguard)
- `scan security` - Run security scan
- `audit` - Run security audit
- `token usage` - Check AI token usage

## Database
- Location: /data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db

## Requirements
- Python 3.8+
- sqlite3
