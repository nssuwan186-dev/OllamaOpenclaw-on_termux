# 📚 สารบัญข้อมูลวิพัฒน์โฮเทล (Data Schema)

Umi ใช้ข้อมูลเหล่านี้ในการเขียน Python Script เพื่อรายงานผล:

## 1. ข้อมูลลูกค้า (Guests)
- **ตารางหลัก:** `dim_guests` (สะอาด ไม่มีซ้ำ)
  - คอลัมน์: Guest_Name, Phone, Nationality, Guest_ID
- **ตารางเดิม:** `guests`
  - คอลัมน์: name, phone, id_card, passport

## 2. ข้อมูลการเงิน (Finance)
- **ประวัติศาสตร์:** `fact_transactions` (ดึงจาก Excel 2.7 หมื่นรายการ)
  - คอลัมน์: Date, Room_No, Grand_Total, Payment_Method
- **รายรับปัจจุบัน:** `income_table`
  - คอลัมน์: date, amount, source, note
- **รายจ่ายปัจจุบัน:** `expense_table`
  - คอลัมน์: date, amount, category, vendor

## 3. ห้องพักและมิเตอร์ (Rooms & Utilities)
- **ตารางห้อง:** `rooms` (room_no, building, type, status)
- **ตารางมิเตอร์:** `utility_meters` (room_no, month, electric_reading, water_reading)