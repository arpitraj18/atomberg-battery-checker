# Smart Lock Battery Monitor & Analytics System

This project is a backend data engineering service designed to identify smart locks that haven't had their battery checked in over 30 days. It automatically identifies stale locks, retrieves owner details, and sends push notifications (FCM) to prompt a check.

Beyond simple notifications, this system includes a **Simulation Engine** to generate realistic user behavior data and an **Analytics Module** to track Click-Through Rates (CTR) and Campaign Effectiveness.

---

## 🌟 Key Features

* **Automated Stale Lock Detection:** Scans DynamoDB for locks with `last_checked_timestamp < 30_days`.
* **Intelligent Routing:** Fetches owner details from PostgreSQL to map locks to users.
* **Dual-Mode Execution:**
    * **Simulation Mode (Default):** Runs locally or in CI/CD without credentials, using mock data to demonstrate logic.
    * **Production Mode:** Connects to real AWS and Firebase services when credentials are provided.
* **Advanced Analytics (Bonus Features):**
    * **Click Tracking:** Simulates and measures how many users open the notification.
    * **Conversion Tracking:** Measures "Effectiveness" by tracking if users actually checked their lock after the notification.
* **Automated Reporting:** Generates a color-coded Excel report with detailed logs and a summary dashboard.

---

## 📂 Project Structure

* `main.py`: The core script containing business logic, database services, and the simulation engine.
* `.github/workflows/weekly_cron.yml`: CI/CD pipeline for weekly automation. Includes a manual "Production Switch" for recruiters.
* `requirements.txt`: Python dependencies (`boto3`, `pandas`, `openpyxl`, `firebase-admin`).
* `battery_report_[DATE].xlsx`: The output report generated after every run.

---

## 🚀 How to Run

### 1. Run Locally (Simulation Mode)
This is the default mode. It requires no AWS keys and uses internal mock data.

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Script:**
    ```bash
    python main.py
    ```
3.  **View Output:** A new file `battery_report_YYYY-MM-DD.xlsx` will appear in your folder.

### 2. Run in Production (Real Database)
To switch to live data, you must provide environment variables.

1.  **Set Environment Variables:**
    ```bash
    export SIMULATION_MODE="False"
    export AWS_ACCESS_KEY_ID="your_key"
    export AWS_SECRET_ACCESS_KEY="your_secret"
    export DB_HOST="your_rds_host"
    export DB_PASSWORD="your_db_password"
    ```
2.  **Run the Script:**
    ```bash
    python main.py
    ```

### 3. Run via CI/CD (GitHub Actions)
The project includes a GitHub Actions workflow that runs automatically every Monday.
* **Manual Trigger:** You can manually trigger the workflow from the "Actions" tab.
* **Production Toggle:** When running manually, a checkbox **"Enable Simulation Mode?"** appears. Unchecking it allows you to run against production (if Secrets are configured).

---

## 📊 Understanding the Generated Report

The script generates an Excel file with two sheets. Here is how to interpret the data.

### Sheet 1: Detailed Logs
This sheet tracks every individual notification attempt.

| Column | Meaning |
| :--- | :--- |
| **Timestamp** | Exact time the notification was sent. |
| **Lock_ID** | The ID of the stale lock. |
| **User_ID** | The owner of the lock. |
| **Status** | **SUCCESS:** Message sent to FCM.<br>**FAILURE:** Error occurred (e.g., Orphan lock). |
| **User_Action** | **OPENED:** User clicked the notification.<br>**NO_RESPONSE:** User ignored it. |
| **Outcome** | **EFFECTIVE:** User physically checked the lock (Conversion).<br>**PENDING:** No action taken yet. |

**Color Coding Guide:**
* 🟢 **Green:** Success! The user received the message **AND** opened it.
* 🟡 **Yellow:** Pending. The message was sent successfully, but the user hasn't opened it yet.
* 🔴 **Red:** Failure. Technical error (e.g., Lock exists but has no owner).

### Sheet 2: Dashboard
A high-level summary for stakeholders to measure campaign performance.

| Metric | Definition |
| :--- | :--- |
| **Campaign ID** | Unique ID for the weekly run (e.g., `bat_check_2025_W50`). |
| **Sent** | Total number of stale locks identified and notified. |
| **Clicks (CTR)** | **Click-Through Rate:** Percentage of users who tapped the notification.<br>*(Formula: Clicks / Sent * 100)* |
| **Effectiveness** | **Conversion Rate:** Percentage of users who actually checked their lock battery.<br>*(Formula: Conversions / Sent * 100)* |

---

## 🛠 Tech Stack
* **Language:** Python 3.9
* **Data Processing:** Pandas
* **Reporting:** OpenPyXL (Excel generation)
* **Cloud (Mocked/Real):** AWS DynamoDB, PostgreSQL, Firebase FCM
* **Automation:** GitHub Actions