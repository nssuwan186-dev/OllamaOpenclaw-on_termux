#!/bin/bash

# Define the path to the Python script
PYTHON_SCRIPT="/data/data/com.termux/files/home/.openclaw/workspace/room_reminders.py"
USER_ID="8144545476" # Replace with actual Telegram User ID

# Run the Python script and capture its JSON output
REMINDER_OUTPUT=$(python3 "$PYTHON_SCRIPT")

# Parse the JSON output
STATUS=$(echo "$REMINDER_OUTPUT" | jq -r '.status')
# Check if "reminders" array is empty or contains "ไม่มีกำหนดการแจ้งเตือนวันนี้"
REMINDER_ARRAY=$(echo "$REMINDER_OUTPUT" | jq -c '.reminders')

if [ "$STATUS" == "success" ]; then
    if [ "$REMINDER_ARRAY" == '["ไม่มีกำหนดการแจ้งเตือนวันนี้"]' ]; then
        MESSAGE="✅ ไม่มีกำหนดการแจ้งเตือนห้องพักรายเดือนวันนี้"
    elif [ "$REMINDER_ARRAY" != '[]' ]; then
        # Format reminders, each on a new line
        REMINDERS=$(echo "$REMINDER_OUTPUT" | jq -r '.reminders[]' | sed 's/^/- /')
        MESSAGE="📢 **แจ้งเตือนห้องพักรายเดือน:**
$REMINDERS"
    else
        MESSAGE="✅ ไม่มีกำหนดการแจ้งเตือนห้องพักรายเดือนวันนี้"
    fi
else
    ERROR_MESSAGE=$(echo "$REMINDER_OUTPUT" | jq -r '.message')
    MESSAGE="❌ เกิดข้อผิดพลาดในการตรวจสอบแจ้งเตือนห้องพัก: $ERROR_MESSAGE"
fi

# Send the message via OpenClaw
/data/data/com.termux/files/usr/bin/openclaw message send --target "$USER_ID" --message "$MESSAGE"
