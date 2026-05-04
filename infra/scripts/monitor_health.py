import requests
import sys
import time

# Configuration
API_URL = "https://api.yourdomain.com/api/health"
WEBHOOK_URL = "https://hooks.slack.com/services/..." # Add your webhook here
APP_NAME = "MyAtelier Pro"

def check_health():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok" and data.get("database_ok"):
                return True, "Healthy"
            else:
                return False, f"Degraded: {data}"
        else:
            return False, f"HTTP Error: {response.status_code}"
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def send_alert(message):
    if not WEBHOOK_URL:
        print(f"ALERT: {message}")
        return
    
    payload = {
        "text": f"🚨 *{APP_NAME} Health Alert* 🚨\nStatus: {message}\nTime: {time.ctime()}"
    }
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Failed to send alert: {e}")

if __name__ == "__main__":
    is_healthy, status_msg = check_health()
    if not is_healthy:
        send_alert(status_msg)
        sys.exit(1)
    else:
        print(f"System is healthy: {status_msg}")
        sys.exit(0)
