"""
backend/sms.py
--------------
SMS sending logic using Fast2SMS.
All SMS messages are logged for transparency.
"""
import os
import requests
from dotenv import load_dotenv
from backend.db import get_db_connection

# Load environment variables
load_dotenv()

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")
FAST2SMS_URL = "https://www.fast2sms.com/dev/bulkV2"

# -------------------------------------
# CORE SMS FUNCTION
# -------------------
def send_sms(shg_id, member_id, mobile, message):
    """
    Send SMS using Fast2SMS and log result.
    """

    payload = {
        "route": "q",
        "message": message,
        "numbers": mobile
    }

    headers = {
        "authorization": FAST2SMS_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            FAST2SMS_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        status = "sent" if response.status_code == 200 else "failed"
    except Exception:
        status = "failed"

    # Log SMS
    log_sms(shg_id, member_id, mobile, message, status)

    return status == "sent"


# -------------------------------------------------
# SMS LOGGING
# -------------------------------------------------
def log_sms(shg_id, member_id, mobile, message, status):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO sms_logs (
            shg_id, member_id, mobile, message, status
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (shg_id, member_id, mobile, message, status))

    conn.commit()
    cur.close()
    conn.close()


# -------------------------------------------------
# MESSAGE TEMPLATES (FIXED)
# -------------------------------------------------
def deposit_sms(member_name, amount, balance):
    return f"""
महिला बचत गट

{member_name} यांची
₹{amount} जमा झाली आहे.

एकूण शिल्लक: ₹{balance}
""".strip()


def loan_given_sms(member_name, loan_amount, interest_rate, monthly_total):
    return f"""
महिला बचत गट

{member_name} यांना
₹{loan_amount} कर्ज दिले.

मासिक व्याज: {interest_rate}%
दरमहा भरायचे: ₹{monthly_total}
""".strip()


def loan_closed_sms(member_name, loan_amount):
    return f"""
महिला बचत गट

{member_name} यांचे
₹{loan_amount} कर्ज पूर्ण फेडले आहे.

कर्ज स्थिती: बंद
""".strip()
