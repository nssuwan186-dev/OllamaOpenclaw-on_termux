#!/bin/bash

# Define the path to the Python script
PYTHON_SCRIPT="/data/data/com.termux/files/home/.openclaw/workspace/advance_notifications.py"
USER_ID="8144545476" # Replace with actual Telegram User ID

# Run the Python script and capture its JSON output
NOTIFICATION_OUTPUT=$(python3 "$PYTHON_SCRIPT")

# Parse the JSON output
STATUS=$(echo "$NOTIFICATION_OUTPUT" | jq -r '.status')

if [ "$STATUS" == "success" ]; then
    UPCOMING_CHECK_IN=$(echo "$NOTIFICATION_OUTPUT" | jq -r '.notifications.upcoming_check_in[]' | sed 's/^/- /' | tr '
' '
')
    UPCOMING_CHECK_OUT=$(echo "$NOTIFICATION_OUTPUT" | jq -r '.notifications.upcoming_check_out[]' | sed 's/^/- /' | tr '
' '
')

    MESSAGE="🔔 **แจ้งเตือนล่วงหน้า (พรุ่งนี้):**
"
    MESSAGE+="-------------------------------------------------
"

    HAS_NOTIFICATIONS=false
    if [ -n "$UPCOMING_CHECK_IN" ]; then
        MESSAGE+="➡️ **Check-in พรุ่งนี้:**
$UPCOMING_CHECK_IN
"
        HAS_NOTIFICATIONS=true
    fi
    if [ -n "$UPCOMING_CHECK_OUT" ]; then
        MESSAGE+="⬅️ **Check-out พรุ่งนี้:**
$UPCOMING_CHECK_OUT
"
        HAS_NOTIFICATIONS=true
    fi

    if [ "$HAS_NOTIFICATIONS" == "false" ]; then
        MESSAGE="✅ ไม่มีรายการ Check-in/Check-out ล่วงหน้าสำหรับพรุ่งนี้"
    fi
else
    ERROR_MESSAGE=$(echo "$NOTIFICATION_OUTPUT" | jq -r '.message')
    MESSAGE="❌ เกิดข้อผิดพลาดในการตรวจสอบแจ้งเตือนล่วงหน้า: $ERROR_MESSAGE"
fi

# Send the message via OpenClaw
/data/data/com.termux/files/usr/bin/openclaw message send --target "$USER_ID" --message "$MESSAGE"
