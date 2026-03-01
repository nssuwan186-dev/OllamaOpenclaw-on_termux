#!/usr/bin/env python3
"""
Hotel Management Skill for OpenClaw v2.0
Integrated with Caelguard Security Tools
"""

import json
import subprocess
import sys
import os

# Paths
WORKSPACE = "/data/data/com.termux/files/home/.openclaw/workspace"
CAELGUARD = "/root/.opencode/caelguard-community/scripts"
DB_PATH = f"{WORKSPACE}/hotel_account.db"

def run_command(script, args=[]):
    """Run a Python script and return output"""
    result = subprocess.run(
        [sys.executable, script] + args,
        capture_output=True, text=True, cwd=WORKSPACE
    )
    return result.stdout or result.stderr

def cmd_rooms(query=""):
    """List available rooms"""
    if query:
        return run_command("query_rooms.py", ["details", query])
    return run_command("query_rooms.py", ["availability", "2026-03-01"])

def cmd_booking(room, date, nights):
    """Book a room"""
    return run_command("add_booking.py", [room, "Guest", date, str(nights)])

def cmd_search_guest(name):
    """Search for a guest"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, phone, country FROM guests WHERE name LIKE ?", (f"%{name}%",))
    results = cursor.fetchall()
    conn.close()
    if results:
        return "\n".join([f"• {r[0]} - {r[1]} ({r[2]})" for r in results])
    return "ไม่พบลูกค้า"

def cmd_report():
    """Generate daily report"""
    return run_command("report_generator.py", ["--type", "daily"])

def cmd_export():
    """Export data to CSV"""
    return run_command("export_csv.py", ["bookings"])

def cmd_backup():
    """Create backup"""
    return run_command("backup_manager.py", ["backup", "--type", "daily"])

def cmd_security_scan():
    """Run Caelguard security scan"""
    result = subprocess.run(
        [sys.executable, f"{CAELGUARD}/shellguard-scanner.py", WORKSPACE, "--json"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        score = data.get("overall_score", 0)
        rating = data.get("rating", "unknown")
        return f"🛡️ Security Scan Result\n\nScore: {score}/100 ({rating})\n\nFiles scanned: {data.get('files_scanned', 0)}"
    except:
        return result.stdout[:500]

def cmd_security_audit():
    """Run Caelguard audit lite"""
    result = subprocess.run(
        [sys.executable, f"{CAELGUARD}/caelguard-audit-lite.py", "--json"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        grade = data.get("overall_grade", "N/A")
        return f"🔒 Security Audit\n\nGrade: {grade}\n\nChecks passed: {data.get('checks_passed', 0)}/{data.get('total_checks', 0)}"
    except:
        return result.stdout[:500]

def cmd_token_audit():
    """Run token audit"""
    result = subprocess.run(
        [sys.executable, f"{CAELGUARD}/token-audit.py", WORKSPACE],
        capture_output=True, text=True
    )
    return result.stdout[:800]

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Usage: hotel.py <command> [args...]"}))
        return

    command = sys.argv[1].lower()
    
    commands = {
        "rooms": lambda: cmd_rooms(),
        "booking": lambda: cmd_booking(sys.argv[2], sys.argv[3], sys.argv[4]) if len(sys.argv) >= 5 else "Usage: booking <room> <date> <nights>",
        "search": lambda: cmd_search_guest(sys.argv[2]) if len(sys.argv) >= 3 else "Usage: search <name>",
        "report": lambda: cmd_report(),
        "export": lambda: cmd_export(),
        "backup": lambda: cmd_backup(),
        "scan": lambda: cmd_security_scan(),
        "audit": lambda: cmd_security_audit(),
        "token": lambda: cmd_token_audit(),
    }
    
    if command in commands:
        print(commands[command]())
    else:
        print(json.dumps({"status": "error", "message": f"Unknown command: {command}"}))

if __name__ == "__main__":
    main()
