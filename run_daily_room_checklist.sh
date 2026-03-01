#!/bin/bash

# Define the path to the Python script
PYTHON_SCRIPT="/data/data/com.termux/files/home/.openclaw/workspace/daily_room_checklist.py"
USER_ID="8144545476" # Replace with actual Telegram User ID

# Run the Python script and capture its JSON output
CHECKLIST_OUTPUT=$(python3 "$PYTHON_SCRIPT")

# Parse the JSON output
STATUS=$(echo "$CHECKLIST_OUTPUT" | jq -r '.status')

if [ "$STATUS" == "success" ]; then
    # Extract checklist details
    CHECK_IN_TODAY=$(echo "$CHECKLIST_OUTPUT" | jq -r '.checklist.check_in_today[]' | sed 's/^/- /' | tr '
' '
')
    CHECK_OUT_TODAY=$(echo "$CHECKLIST_OUTPUT" | jq -r '.checklist.check_out_today[]' | sed 's/^/- /' | tr '
' '
')
    OCCUPIED_ONGOING=$(echo "$CHECKLIST_OUTPUT" | jq -r '.checklist.occupied_ongoing[]' | sed 's/^/- /' | tr '
' '
')
    AVAILABLE_TODAY=$(echo "$CHECKLIST_OUTPUT" | jq -r '.checklist.available_today[]' | sed 's/^/- /' | tr '
' '
')
    UNDER_MAINTENANCE=$(echo "$CHECKLIST_OUTPUT" | jq -r '.checklist.under_maintenance[]' | sed 's/^/- /' | tr '
' '
')
    MONTHLY_STAY=$(echo "$CHECKLIST_OUTPUT" | jq -r '.checklist.monthly_stay[]' | sed 's/^/- /' | tr '
' '
')

    MESSAGE="📋 **Daily Room Status Checklist ($(date +'%Y-%m-%d'))**
"
    MESSAGE+="-------------------------------------------------
"

    if [ -n "$CHECK_IN_TODAY" ]; then
        MESSAGE+="📥 **Check-ins Today:**
$CHECK_IN_TODAY
"
    fi
    if [ -n "$CHECK_OUT_TODAY" ]; then
        MESSAGE+="📤 **Check-outs Today:**
$CHECK_OUT_TODAY
"
    fi
    if [ -n "$OCCUPIED_ONGOING" ]; then
        MESSAGE+="🛌 **Occupied (Ongoing):**
$OCCUPIED_ONGOING
"
    fi
    if [ -n "$AVAILABLE_TODAY" ]; then
        MESSAGE+="✅ **Available Today:**
$AVAILABLE_TODAY
"
    fi
    if [ -n "$MONTHLY_STAY" ]; then
        MESSAGE+="🗓️ **Monthly Stays:**
$MONTHLY_STAY
"
    fi
    if [ -n "$UNDER_MAINTENANCE" ]; then
        MESSAGE+="🚧 **Under Maintenance:**
$UNDER_MAINTENANCE
"
    fi

    # If no specific activities, provide a general message
    if [ -z "$CHECK_IN_TODAY" ] && 
       [ -z "$CHECK_OUT_TODAY" ] && 
       [ -z "$OCCUPIED_ONGOING" ] && 
       [ -z "$AVAILABLE_TODAY" ] && 
       [ -z "$MONTHLY_STAY" ] && 
       [ -z "$UNDER_MAINTENANCE" ]; then
        MESSAGE="ℹ️ ไม่มีข้อมูลสถานะห้องพักพิเศษสำหรับวันนี้"
    fi
else
    ERROR_MESSAGE=$(echo "$CHECKLIST_OUTPUT" | jq -r '.message')
    MESSAGE="❌ เกิดข้อผิดพลาดในการสร้าง Daily Room Checklist: $ERROR_MESSAGE"
fi

# Send the message via OpenClaw
/data/data/com.termux/files/usr/bin/openclaw message send --target "$USER_ID" --message "$MESSAGE"
