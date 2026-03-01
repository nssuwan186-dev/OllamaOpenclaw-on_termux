# AGENTS.md — TABLE MAPPING (อัปเดต 2026-03-01)

## ⚠️ ตารางที่มีข้อมูล (ใช้ได้)
| ตาราง | rows | ใช้สำหรับ |
|---|---|---|
| `rooms` | 51 | ห้องว่าง/สถานะห้อง |
| `bookings` | 205 | การจอง |
| `dim_guests` | 1,139 | ข้อมูลลูกค้า |
| `clean_transactions` | 981 | รายรับปัจจุบัน |
| `fact_transactions` | 27,922 | ประวัติการเงินทั้งหมด |
| `utility_meters` | 3 | มิเตอร์น้ำ-ไฟ |

## ❌ ตารางว่างเปล่า (ห้ามใช้ query!)
- `transactions` → 0 rows
- `income_table` → 0 rows
- `expense_table` → 0 rows

## คอลัมน์จริงแต่ละตาราง
- **rooms:** room_no, building, floor, type, price_per_night, status
- **bookings:** booking_no, room_no, guest_id, check_in, check_out, nights, room_rate, total_amount, status, payment_channel
- **dim_guests:** Guest_ID, Guest_Name, Phone, Nationality
- **clean_transactions:** trans_id, date, room_no, guest_name, amount, payment_method
- **fact_transactions:** Guest_ID, Date, Room_No, Room_Type, Grand_Total, Payment_Method

## Relations
- dim_guests.Guest_ID ↔ bookings.guest_id
- rooms.room_no ↔ bookings.room_no
- rooms.room_no ↔ clean_transactions.room_no

## DB PATH
/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db
