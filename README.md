# Smart Lock Battery Monitor & Notification System

This project is a backend data engineering service designed to identify smart locks that haven't had their battery checked in over 30 days. It automatically identifies stale locks, retrieves the owner's details, and sends a push notification (FCM) to prompt a check.

The system includes built-in analytics to track **User Click-Through Rates (CTR)** and **Campaign Effectiveness (Conversion Rates)**.

---

## 📂 Project Structure

* **`main.py`**: The core Python script containing the business logic, database service classes, and analytics simulation.
* **`.github/workflows/weekly_cron.yml`**: CI/CD pipeline configuration that automates this script to run every Monday at 10:00 AM UTC.
* **`requirements.txt`**: List of Python dependencies (`boto3`, `pandas`, `openpyxl`, etc.).
* **`battery_report_YYYY-MM-DD.xlsx`**: The automatically generated Excel report containing success/failure logs and an analytics dashboard.

---

## 🧠 System Logic & Workflow

The script follows a modular **Service Class** pattern:

1.  **`DatabaseService`**:
    * Connects to **DynamoDB** (Mocked or Real) to scan for locks with `last_checked_timestamp < 30_days_ago`.
    * Connects to **PostgreSQL** (Mocked or Real) to fetch the `user_id` and `fcm_token` for those locks.
    * Handles edge cases, such as "Orphan Locks" (locks that exist but have no assigned user).

2.  **`NotificationService`**:
    * Generates a unique `campaign_id` (e.g., `battery_check_2025_W50`).
    * Sends an FCM notification to the user with this ID attached to the payload for tracking.

3.  **Analytics Engine (Bonus Implementation)**:
    * **Click Simulation**: Simulates users clicking the notification (randomized probability).
    * **Conversion Simulation**: Simulates users actually performing the physical action of checking the lock (randomized probability).
    * **Reporting**: Aggregates this data into an Excel Dashboard.

---

## 🚀 How to Run

### 1. Simulation Mode (Default)
The script is designed to run out-of-the-box without needing AWS credentials. It uses internal mock data to demonstrate the logic.

**Steps:**
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the script:
    ```bash
    python main.py
    ```
3.  **Output:**
    * Console logs showing the mock process.
    * A generated Excel file (`battery_report_....xlsx`) with color-coded logs.

### 2. Production Mode (Real Database)
To connect to live AWS DynamoDB and PostgreSQL instances:

1.  Set the environment variable `SIMULATION_MODE` to `False`.
2.  Export the required credentials in your environment (or CI/CD Secrets):
    ```bash
    export AWS_ACCESS_KEY_ID="your_key"
    export AWS_SECRET_ACCESS_KEY="your_secret"
    export DB_HOST="your_rds_host"
    export DB_PASSWORD="your_db_password"
    ```

---

## 📊 Analytics & Reporting (Bonus Points)

The script generates an Excel report with two sheets:

### Sheet 1: Detailed Logs
A color-coded breakdown of every notification attempt:
* 🟢 **Green (OPENED):** User received and clicked the notification.
* 🟡 **Yellow (NO_RESPONSE):** Notification sent successfully, but user hasn't clicked yet.
* 🔴 **Red (FAILURE):** Error occurred (e.g., Orphan lock with no user mapping).

### Sheet 2: Dashboard
A high-level summary for stakeholders:
* **Total Sent:** Number of stale locks identified.
* **Click Through Rate (CTR):** `%` of users who opened the app.
* **Effective Conversions:** `%` of users who actually checked their battery (Outcome = `EFFECTIVE`).

---

## 🤖 CI/CD Automation (GitHub Actions)

The project includes a GitHub Actions workflow (`weekly_cron.yml`) that:
1.  **Runs Automatically:** Scheduled via Cron (`0 10 * * 1`) to run every Monday.
2.  **Runs Manually:** Includes a `workflow_dispatch` trigger with a **Checkbox Input**, allowing the recruiter/admin to toggle between Simulation Mode and Production Mode directly from the GitHub UI.
3.  **Artifacts:** Automatically uploads the generated Excel report to the GitHub Run summary for download.