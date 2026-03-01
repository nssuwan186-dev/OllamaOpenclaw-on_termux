# 🔍 คู่มือ Vision Analyzer - วิพัฒน์โฮเทล

## 📷 ระบบวิเคราะห์รูปภาพ

รองรับการวิเคราะห์:
- 📄 สลิปโอนเงิน
- 🧾 ใบเสร็จ
- 📋 เอกสารต่างๆ

---

## 🚀 การใช้งาน

### 1. วิเคราะห์รูปภาพ (ไม่บันทึก)

```bash
python3 vision_analyzer.py /path/to/image.jpg
```

### 2. วิเคราะห์และบันทึกลงฐานข้อมูล

```bash
python3 vision_analyzer.py /path/to/image.jpg --save
```

### 3. เลือกวิธีวิเคราะห์

```bash
# Auto (ลอง Ollama ก่อน)
python3 vision_analyzer.py image.jpg --method auto

# ใช้ Ollama (LLava)
python3 vision_analyzer.py image.jpg --method ollama

# ใช้ Google Gemini
python3 vision_analyzer.py image.jpg --method gemini
```

---

## 🔧 การตั้งค่า

### Ollama (แนะนำ)

```bash
# ติดตั้ง LLava (Vision Model)
ollama pull llava:7b

# ทดสอบ
ollama list
```

### Google Gemini

```bash
# ตั้งค่า API Key
export GEMINI_API_KEY="your-api-key-here"

# หรือเพิ่มใน ~/.bashrc
echo 'export GEMINI_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📊 ข้อมูลที่วิเคราะห์ได้

| ข้อมูล | คำอธิบาย |
|---------|-----------|
| `date` | วันที่ในสลิป (YYYY-MM-DD) |
| `amount` | จำนวนเงิน |
| `from_account` | บัญชีต้นทาง |
| `to_account` | บัญชีปลายทาง |
| `reference` | เลขอ้างอิง |
| `room_no` | หมายเลขห้อง |
| `note` | หมายเหตุ |

---

## 📱 การใช้งานกับ Telegram

เมื่อส่งรูปภาพไปที่ Bot:

1. Bot จะวิเคราะห์รูปภาพ
2. แยกข้อมูลออกมา
3. แสดงผลการวิเคราะห์
4. ถามยืนยันเพื่อบันทึก

---

## 💾 การบันทึกข้อมูล

เมื่อบันทึกจะทำ:
1. เพิ่มข้อมูลใน `clean_transactions`
2. อัปเดตสถานะห้องเป็น "ไม่ว่าง" (ถ้าระบุห้อง)

---

## 🛠️ ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | หน้าที่ |
|--------|---------|
| `vision_analyzer.py` | วิเคราะห์รูปภาพ |
| `telegram_handler.py` | จัดการ Telegram |

---

## ⚠️ ข้อควรระวัง

1. คุณภาพรูปภาพ - ภาพชัดวิเคราะห์ได้แม่นยำกว่า
2. API Key - ถ้าใช้ Gemini ต้องตั้งค่า API Key
3. Ollama - ต้องติดตั้ง vision model (`ollama pull llava:7b`)

---

*🔍 วิพัฒน์โฮเทล | OpenClaw System*
