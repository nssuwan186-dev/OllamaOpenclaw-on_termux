# Hotel Management Skill for OpenClaw

## Overview
This skill provides hotel management capabilities integrated with Caelguard security.

## Setup
```bash
# Copy to OpenClaw skills
cp -r /data/data/com.termux/files/home/.openclaw/workspace/skills/hotel ~/.openclaw/workspace/skills/
```

## Usage via OpenClaw

### Natural Language Commands
Just message your OpenClaw with:
- "จองห้อง A101 วันที่ 2026-03-05 2 คืน"
- "มีห้องว่างไหม"
- "ค้นหาลูกชื่อ สมชาย"
- "รายงานวันนี้"
- "สำรองข้อมูล"

### Direct Commands
```bash
python3 ~/.openclaw/workspace/skills/hotel/hotel.py <command>
```

## Commands
- `rooms` - Show available rooms
- `book <room> <date> <nights>` - Book a room  
- `search <name>` - Search guest
- `report` - Daily report
- `backup` - Backup data
- `scan` - Security scan (Caelguard)
