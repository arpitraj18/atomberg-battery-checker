import time
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# LOGIC:
# 1. Look for an Environment Variable named 'SIMULATION_MODE'
# 2. If found, convert string 'true'/'false' to boolean.
# 3. Default to True (Simulation) if the variable is missing (Safety).
env_sim = os.getenv('SIMULATION_MODE', 'True')
SIMULATION_MODE = env_sim.lower() == 'true'

# --- REPORTING DATA STORAGE ---
# We will append dictionaries here to track what happened
report_data = []

# --- HELPER FOR DATES ---
now = datetime.now()
def days_ago(n):
    return int((now - timedelta(days=n)).timestamp())

# --- MOCK DATA ---
mock_dynamo_table = [
    {'lock_id': 'L100', 'last_checked': days_ago(0)},
    {'lock_id': 'L103', 'last_checked': days_ago(29)},
    {'lock_id': 'L101', 'last_checked': days_ago(60)},
    {'lock_id': 'L102', 'last_checked': days_ago(35)},
    {'lock_id': 'L104', 'last_checked': days_ago(31)},
    {'lock_id': 'L105', 'last_checked': days_ago(365)},
    {'lock_id': 'L106', 'last_checked': days_ago(100)} # Orphan
]

mock_postgres_table = {
    'L100': {'user_id': 'U_A', 'fcm': 'token_A_123'},
    'L101': {'user_id': 'U_B', 'fcm': 'token_B_456'},
    'L102': {'user_id': 'U_C', 'fcm': 'token_C_789'},
    'L103': {'user_id': 'U_D', 'fcm': 'token_D_101'},
    'L104': {'user_id': 'U_E', 'fcm': 'token_E_202'},
    'L105': {'user_id': 'U_A', 'fcm': 'token_A_123'},
}

# --- DATABASE SERVICE ---
class DatabaseService:
    def get_stale_locks(self, days_threshold=30):
        cutoff = int((datetime.now() - timedelta(days=days_threshold)).timestamp())
        stale = []
        if SIMULATION_MODE:
            print(f"[DynamoDB] Scanning for locks older than {days_threshold} days...")
            for item in mock_dynamo_table:
                if item['last_checked'] < cutoff:
                    stale.append(item['lock_id'])
        return stale

    def get_user_details(self, lock_ids):
        users_to_notify = []
        if SIMULATION_MODE:
            print(f"[Postgres] Fetching owners for locks: {lock_ids}")
            for lid in lock_ids:
                if lid in mock_postgres_table:
                    data = mock_postgres_table[lid]
                    users_to_notify.append({
                        'lock_id': lid,
                        'user_id': data['user_id'],
                        'fcm_token': data['fcm']
                    })
                else:
                    # LOG FAILURE: ORPHAN LOCK
                    print(f"⚠️ Warning: Lock {lid} is an orphan (No User Found).")
                    report_data.append({
                        'Timestamp': datetime.now().isoformat(),
                        'Lock_ID': lid,
                        'User_ID': 'N/A',
                        'Status': 'FAILURE',
                        'Reason': 'Orphan Lock - No User Mapping Found'
                    })
        return users_to_notify

# --- NOTIFICATION SERVICE ---
def send_notifications(user_list):
    campaign_id = f"battery_check_{datetime.now().strftime('%Y_W%U')}"
    sent_count = 0
    print(f"\nStarting Campaign: {campaign_id}")

    for user in user_list:
        # LOG SUCCESS: NOTIFICATION SENT
        if SIMULATION_MODE:
            print(f"   ➡ [FCM SENT] User: {user['user_id']} | Lock: {user['lock_id']}")
            sent_count += 1
            
            report_data.append({
                'Timestamp': datetime.now().isoformat(),
                'Lock_ID': user['lock_id'],
                'User_ID': user['user_id'],
                'Status': 'SUCCESS',
                'Reason': f'Notification Sent (Campgn: {campaign_id})'
            })
            
    return sent_count

# --- EXCEL REPORTING SERVICE ---
def generate_excel_report():
    if not report_data:
        print("No data to report.")
        return

    filename = f"battery_report_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    df = pd.DataFrame(report_data)

    # Use ExcelWriter to apply styles
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
        worksheet = writer.sheets['Report']
        
        # Iterating through rows to apply conditional formatting
        # Row 1 is header, data starts at Row 2
        for row_idx, row_data in enumerate(report_data, start=2):
            status = row_data['Status']
            
            # Define Colors
            fill_color = None
            if status == 'SUCCESS':
                fill_color = 'C6EFCE' # Light Green
            elif status == 'FAILURE':
                fill_color = 'FFC7CE' # Light Red
                
            # Apply Color to the whole row
            if fill_color:
                from openpyxl.styles import PatternFill
                fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type='solid')
                for col_idx in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    cell.fill = fill

    print(f"\n✅ Report generated: {filename}")

# --- MAIN ---
def main():
    mode_str = "SIMULATION" if SIMULATION_MODE else "PRODUCTION"
    print(f"--- Weekly Battery Check Job Started (Mode: {mode_str}) ---")
    db = DatabaseService()
    
    # 1. Get Stale Locks
    stale_locks = db.get_stale_locks(days_threshold=30)
    print(f" Found {len(stale_locks)} stale locks.")

    if stale_locks:
        # 2. Get Users (Failures for orphans logged here)
        users = db.get_user_details(stale_locks)
        
        # 3. Send Notifications (Successes logged here)
        count = send_notifications(users)
        print(f"\n Job Finished. Total Notifications Sent: {count}")
        
    # 4. Generate the Excel Report
    generate_excel_report()

if __name__ == "__main__":
    main()