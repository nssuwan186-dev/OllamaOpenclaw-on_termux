# tools.md — คู่มือการใช้เครื่องมือ (The Manual)

> เมื่อ AI ต้องการดำเนินการกับข้อมูล ให้ใช้คู่มือนี้เป็นแนวทาง

---

## 1. ฐานข้อมูลหลัก
**ไฟล์**: `/data/data/com.termux/files/home/.openclaw/workspace/Database/hotel_account.db`
**ประเภท**: SQLite
**Library**: `sqlite3` หรือ `SQLAlchemy + pandas`

```python
import sqlite3
import pandas as pd
DB_PATH = "/data/data/com.termux/files/home/.openclaw/workspace/Database/hotel_account.db"
conn = sqlite3.connect(DB_PATH)
```

---

## 2. CRUD Operations — รายรับ-รายจ่าย
### บันทึกรายการใหม่
```sql
INSERT INTO transactions (date, item_name, phone, room, nights, expense, income, balance, deposit_cash, note) 
VALUES ('2568-12-01', 'ชื่อลูกค้า', '08X-XXXXXXX', 'B106', 1, 0, 400, 3112, 0, 'พักต่อ');
```

### ดึงรายการวันนี้
```sql
SELECT * FROM transactions WHERE date = DATE('now') ORDER BY id DESC;
```

### สรุปยอดรายสัปดาห์
```sql
SELECT SUM(income) AS รายรับรวม, SUM(expense) AS รายจ่ายรวม, SUM(income) - SUM(expense) AS กำไรสุทธิ 
FROM transactions 
WHERE date >= DATE('now', '-7 days');
```

### สรุปยอดรายเดือน
```sql
SELECT strftime('%Y-%m', date) AS เดือน, SUM(income) AS รายรับรวม, SUM(expense) AS รายจ่ายรวม, SUM(income) - SUM(expense) AS กำไรสุทธิ, 
COUNT(CASE WHEN income > 0 AND room != '' THEN 1 END) AS จำนวนการจอง 
FROM transactions 
GROUP BY strftime('%Y-%m', date) 
ORDER BY เดือน DESC;
```

---

## 3. CRUD Operations — ห้องพัก
### ตรวจสอบห้องว่าง
```sql
SELECT room_no, building, floor, room_type, price FROM rooms WHERE status = 'Available' ORDER BY building, room_no;
```

### อัปเดตสถานะห้อง
```sql
UPDATE rooms SET status = 'Occupied' WHERE room_no = 'B106';
UPDATE rooms SET status = 'Available' WHERE room_no = 'B106';
```

---

## 4. CRUD Operations — การจอง
### บันทึกการจองใหม่
```sql
INSERT INTO bookings (room_no, guest_id, check_in_date, nights, channel, service_fee, note) 
VALUES ('B106', 'CM01957', '2568-12-01', 1, 'เงินสด', 0, '');
```

### ดูการจองปัจจุบัน
```sql
SELECT b.room_no, g.name, b.check_in_date, b.nights, b.channel 
FROM bookings b 
LEFT JOIN guests g ON b.guest_id = g.guest_id 
WHERE b.check_in_date >= DATE('now') 
ORDER BY b.check_in_date, b.room_no;
```

---

## 5. การนำเข้าข้อมูลจาก Excel → SQL
```python
import pandas as pd
import sqlite3

def import_transactions_from_excel(excel_path, db_path):
    df = pd.read_excel(excel_path)
    # ปรับชื่อคอลัมน์ให้ตรงกับ DB
    df.columns = ['date', 'item_name', 'phone', 'room', 'nights', 'expense', 'income', 'balance', 'deposit_cash', 'note']
    conn = sqlite3.connect(db_path)
    df.to_sql('transactions', conn, if_exists='append', index=False)
    conn.close()
    return f"นำเข้าสำเร็จ {len(df)} รายการ"
```

---

## 6. การสร้างรายงาน Excel
```python
import pandas as pd
import sqlite3
from datetime import datetime

def generate_monthly_report(db_path, month, year):
    conn = sqlite3.connect(db_path)
    query = f""" 
    SELECT date, item_name, room, nights, expense, income, balance, note 
    FROM transactions 
    WHERE strftime('%m', date) = '{month:02d}' AND strftime('%Y', date) = '{year}' 
    ORDER BY date 
    """
    df = pd.read_sql(query, conn)
    conn.close()
    output_path = f"/data/data/com.termux/files/home/.openclaw/workspace/Reports/Monthly/รายงาน_{year}_{month:02d}.xlsx"
    df.to_excel(output_path, index=False)
    return output_path
```

---

## 7. การวิเคราะห์สลิป (Vision AI)
เมื่อได้รับภาพสลิปผ่าน Telegram:
1. ส่งภาพให้ Gemini Vision วิเคราะห์: ยอดเงิน, วันที่, เลขอ้างอิง
2. บันทึกข้อมูลลง `transactions` table
3. ย้ายไฟล์ภาพไปที่ `/data/data/com.termux/files/home/.openclaw/workspace/Media/Slips/YYYY-MM/`
4. บันทึกลง ChromaDB พร้อม metadata

```python
# Prompt สำหรับวิเคราะห์สลิป
SLIP_PROMPT = """
วิเคราะห์สลิปนี้และส่งข้อมูลในรูปแบบ JSON:
{
  "amount": <ยอดเงิน>,
  "date": "<วัน-เดือน-ปี>",
  "reference": "<เลขอ้างอิง>",
  "from_account": "<บัญชีต้นทาง>",
  "to_account": "<บัญชีปลายทาง>",
  "note": "<หมายเหตุ>"
}
"""
```

---

## 8. คำสั่ง Telegram ที่รองรับ
| คำสั่ง | ผลลัพธ์ |
|---|---|
| `สรุปวันนี้` | ตารางรายรับ-รายจ่ายวันนี้ |
| `สรุปสัปดาห์นี้` | ตารางสรุป 7 วัน เทียบสัปดาห์ที่แล้ว |
| `สรุปเดือนนี้` | รายงานรายเดือนพร้อมกราฟ |
| `ห้องว่าง` | รายการห้องที่ว่างอยู่ตอนนี้ |
| `ลูกค้า [ชื่อ/รหัส]` | ดูข้อมูลลูกค้า |
| `บันทึก [รายการ]` | บันทึกรายรับ-รายจ่ายใหม่ |
| ส่งรูปสลิป | วิเคราะห์และบันทึกอัตโนมัติ |
| `/new` หรือ `/reset` | เริ่ม Session ใหม่ |

---

## 9. Restart Protocol
ต้อง Restart Gateway ทุกครั้งที่แก้ไขไฟล์เหล่านี้:
- `soul.md`, `agent.md`, `tools.md`, `.env`

```bash
pkill -f 'openclaw' && sleep 2 && openclaw gateway run
```

---
*tools.md | OpenClaw Hotel System | อัปเดตล่าสุดจากการนำเข้าไฟล์ใหม่*
