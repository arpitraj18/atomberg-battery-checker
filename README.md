# Atomberg Battery Checker Backend

This is a backend service designed to identify smart locks with stale battery checks (>30 days) and notify users via FCM.

## 📂 Project Structure
* `main.py`: Core logic using a Service Class pattern. Includes a `SIMULATION_MODE` for testing without live AWS credentials.
* `.github/workflows/weekly_cron.yml`: CI/CD configuration to automate this script to run every Monday.
* `requirements.txt`: Python dependencies.

## 🚀 How to Run (Simulation Mode)
The script is currently configured to run in **Simulation Mode** by default. It uses mock data to demonstrate the logic (handling stale locks, orphan locks, and multi-lock users) without needing cloud credentials.

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
Run the script:

Bash

python main.py
⚙️ How to Run with Real Database (Production)
To connect this script to a live AWS DynamoDB and PostgreSQL instance:

Update main.py: Change the configuration flag at the top of the file:

Python

SIMULATION_MODE = False
Set Environment Variables: The script looks for standard environment variables for security. You must export these in your terminal or CI/CD secrets:

Bash

export AWS_ACCESS_KEY_ID="your_aws_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
export DB_HOST="your_rds_endpoint"
export DB_PASSWORD="your_db_password"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/firebase_service_account.json"
Run the script:

Bash

python main.py