import time
import json
import os
import random
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
env_sim = os.getenv('SIMULATION_MODE', 'True')
SIMULATION_MODE = env_sim.lower() == 'true'

# --- REPORTING DATA STORAGE ---
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
                    print(f"⚠️ Warning: Lock {lid} is an orphan (No User Found).")
                    report_data.append({
                        'Timestamp': datetime.now().isoformat(),
                        'Lock_ID': lid,
                        'User_ID': 'N/A',
                        'Status': 'FAILURE',
                        'User_Action': 'N/A',
                        'Outcome': 'FAILED',
                        'Reason': 'Orphan Lock - No User Mapping Found'
                    })
        return users_to_notify

# --- NOTIFICATION SERVICE ---
def send_notifications(user_list, campaign_id):
    sent_count = 0
    print(f"\nStarting Campaign: {campaign_id}")

    for user in user_list:
        if SIMULATION_MODE:
            print(f"   ➡ [FCM SENT] User: {user['user_id']} | Lock: {user['lock_id']}")
            sent_count += 1
            
            report_data.append({
                'Timestamp': datetime.now().isoformat(),
                'Lock_ID': user['lock_id'],
                'User_ID': user['user_id'],
                'Status': 'SUCCESS',
                'User_Action': 'NO_RESPONSE', 
                'Outcome': 'PENDING',
                'Reason': f'Notification Sent (Campgn: {campaign_id})'
            })
            
    return sent_count

# --- ANALYTICS SIMULATION (User Clicks) ---
def simulate_user_clicks(campaign_id, notified_users):
    clicks_data = []
    if SIMULATION_MODE:
        print(f"\n🎲 [Analytics] Simulating user clicks...")
        for user in notified_users:
            if random.random() < 0.6: # 60% Click Rate
                clicks_data.append({
                    'User_ID': user['user_id'],
                    'Action': 'CLICKED'
                })
        print(f"   ➡ Simulated {len(clicks_data)} clicks.")
    return clicks_data

# --- EFFECTIVENESS SIMULATION (Physical Action) ---
def simulate_conversions(campaign_id, notified_users):
    """
    Simulates users actually checking the battery (updating the lock timestamp).
    This creates the 'Conversion Rate'.
    """
    conversions_data = []
    if SIMULATION_MODE:
        print(f"\n🔋 [Analytics] Simulating battery checks (Effectiveness)...")
        for user in notified_users:
            # 30% of users actually do the job (Conversion)
            if random.random() < 0.3: 
                conversions_data.append(user['user_id'])
        print(f"   ➡ Simulated {len(conversions_data)} conversions (Battery Checked).")
    return conversions_data

# --- EXCEL REPORTING SERVICE ---
def generate_excel_report(campaign_id, sent_count, clicks_data, conversions_data):
    filename = f"battery_report_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    
    # 1. MERGE DATA INTO LOGS
    clicked_user_ids = {c['User_ID'] for c in clicks_data}
    converted_user_ids = set(conversions_data)
    
    for row in report_data:
        if row['Status'] == 'SUCCESS':
            # Update Click Status
            if row['User_ID'] in clicked_user_ids:
                row['User_Action'] = 'OPENED'
            
            # Update Effectiveness Outcome
            if row['User_ID'] in converted_user_ids:
                row['Outcome'] = 'EFFECTIVE' # User checked the battery
            else:
                row['Outcome'] = 'PENDING'

    # 2. Create DataFrames
    df_logs = pd.DataFrame(report_data)
    cols = ['Timestamp', 'Lock_ID', 'User_ID', 'Status', 'User_Action', 'Outcome', 'Reason']
    df_logs = df_logs[cols]

    # Metrics Calculation
    click_count = len(clicks_data)
    conversion_count = len(conversions_data)
    
    ctr = (click_count / sent_count * 100) if sent_count > 0 else 0
    effectiveness = (conversion_count / sent_count * 100) if sent_count > 0 else 0
    
    df_summary = pd.DataFrame([
        {'Metric': 'Campaign Date', 'Value': datetime.now().strftime('%Y-%m-%d')},
        {'Metric': 'Campaign ID', 'Value': campaign_id},
        {'Metric': 'Total Notifications Sent', 'Value': sent_count},
        {'Metric': 'User Clicks (CTR)', 'Value': f"{click_count} ({ctr:.1f}%)"},
        {'Metric': 'Effective Conversions', 'Value': f"{conversion_count} ({effectiveness:.1f}%)"},
        {'Metric': 'Analysis', 'Value': 'Effectiveness = Users who updated lock timestamp'}
    ])

    # 3. Write to Excel
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_logs.to_excel(writer, index=False, sheet_name='Detailed Logs')
        df_summary.to_excel(writer, index=False, sheet_name='Dashboard')
        
        worksheet = writer.sheets['Detailed Logs']
        from openpyxl.styles import PatternFill
        
        green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid') # Best (Opened)
        yellow_fill = PatternFill(start_color='FFFFCC', end_color='FFFFCC', fill_type='solid') # Okay (Sent)
        red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')   # Bad (Fail)

        for row_idx, row_data in enumerate(report_data, start=2):
            status = row_data['Status']
            action = row_data.get('User_Action', '')

            fill = None
            if status == 'FAILURE':
                fill = red_fill
            elif status == 'SUCCESS':
                if action == 'OPENED':
                    fill = green_fill  
                else:
                    fill = yellow_fill

            if fill:
                for col_idx in range(1, len(df_logs.columns) + 1):
                    worksheet.cell(row=row_idx, column=col_idx).fill = fill

    print(f"\n✅ Report generated: {filename}")
    print(f"   📊 Stats: Sent={sent_count} | CTR={ctr:.1f}% | Effective={effectiveness:.1f}%")

# --- MAIN ---
def main():
    mode_str = "SIMULATION" if SIMULATION_MODE else "PRODUCTION"
    print(f"--- Weekly Battery Check Job Started (Mode: {mode_str}) ---")
    
    db = DatabaseService()
    
    # 1. Get Stale Locks
    stale_locks = db.get_stale_locks(days_threshold=30)
    print(f" Found {len(stale_locks)} stale locks.")

    users = []
    sent_count = 0
    clicks_data = []
    conversions_data = []
    campaign_id = f"battery_check_{datetime.now().strftime('%Y_W%U')}"

    if stale_locks:
        # 2. Get Users
        users = db.get_user_details(stale_locks)
        
        # 3. Send Notifications
        sent_count = send_notifications(users, campaign_id)
        
        # 4. Analytics Simulation (Bonus Points)
        clicks_data = simulate_user_clicks(campaign_id, users)
        conversions_data = simulate_conversions(campaign_id, users)
        
    # 5. Generate Report
    generate_excel_report(campaign_id, sent_count, clicks_data, conversions_data)

if __name__ == "__main__":
    main()