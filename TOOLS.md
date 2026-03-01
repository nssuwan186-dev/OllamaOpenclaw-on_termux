# TOOLS.md — คู่มือ SQL (อัปเดต 2026-03-01)

## DB PATH
DB = "/data/data/com.termux/files/home/.openclaw/workspace/hotel_account.db"

## ห้องว่าง
SELECT room_no, building, floor, type, price_per_night
FROM rooms WHERE status = 'Available'
ORDER BY building, room_no;

## การจองปัจจุบัน
SELECT b.room_no, g.Guest_Name, b.check_in, b.check_out, b.nights, b.payment_channel
FROM bookings b
LEFT JOIN dim_guests g ON b.guest_id = g.Guest_ID
WHERE b.status = 'Active'
ORDER BY b.check_in;

## รายรับย้อนหลัง (ใช้ clean_transactions เสมอ)
SELECT date, room_no, guest_name, amount, payment_method
FROM clean_transactions
ORDER BY date DESC LIMIT 20;

## สรุปรายรับรายเดือน
SELECT strftime('%Y-%m', date) AS เดือน,
       COUNT(*) AS จำนวน, SUM(amount) AS รายรับรวม
FROM clean_transactions
GROUP BY strftime('%Y-%m', date)
ORDER BY เดือน DESC;

## ค้นหาลูกค้า
SELECT Guest_ID, Guest_Name, Phone, Nationality
FROM dim_guests
WHERE Guest_Name LIKE '%ชื่อ%' OR Phone LIKE '%เบอร์%';

## บันทึกรายรับใหม่
INSERT INTO income_table (date, amount, source, note)
VALUES (DATE('now'), 400, 'ห้องพัก', 'B106');

## บันทึกรายจ่ายใหม่
INSERT INTO expense_table (date, amount, category, vendor)
VALUES (DATE('now'), 500, 'ค่าน้ำ', 'การประปา');

## ❌ ห้าม query ตารางเหล่านี้ (ว่างเปล่า)
-- transactions, income_table (อ่าน), expense_table (อ่าน), monthly_summary
