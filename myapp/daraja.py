import requests
from requests.auth import HTTPBasicAuth
import base64
from datetime import datetime

# -------------------------
# Daraja Sandbox Credentials
# -------------------------
CONSUMER_KEY = "Q2aTAjgS4wQuTugXE6b2Ld7HFehBQVnTUSXxLBbE654Bk8GD"
CONSUMER_SECRET = "J6xzvBIXASLb731G1jre2GqEED5lVA3GzvgPfByI1yOsBAIqjg2z3E6C4pfmAAlt"
BUSINESS_SHORTCODE = "174379"  # Sandbox shortcode
PASSKEY = "YourPasskey"        # Sandbox passkey

# Important: match this URL to your Django URL pattern exactly
# For local testing, you can use 127.0.0.1
CALLBACK_URL = "http://127.0.0.1:8000/mpesa-callback/"


# -------------------------
# 1️⃣ Get Access Token
# -------------------------
def get_access_token():
    """
    Fetch OAuth access token from Safaricom Daraja sandbox
    """
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    response.raise_for_status()  # raise error if failed
    data = response.json()
    return data['access_token']

# -------------------------
# 2️⃣ Generate STK Push Password & Timestamp
# -------------------------
def generate_password():
    """
    Generates Base64 encoded password for STK push
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = BUSINESS_SHORTCODE + PASSKEY + timestamp
    encoded = base64.b64encode(data_to_encode.encode('utf-8')).decode('utf-8')
    return encoded, timestamp

# -------------------------
# 3️⃣ Initiate STK Push
# -------------------------
def lipa_na_mpesa(phone_number, amount, account_reference="Order123", transaction_desc="Payment"):
    """
    Initiates a Daraja STK Push request
    """
    token = get_access_token()
    password, timestamp = generate_password()
    
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,                # Customer phone number
        "PartyB": BUSINESS_SHORTCODE,          # Your shortcode
        "PhoneNumber": phone_number,           # Customer phone number again
        "CallBackURL": CALLBACK_URL,           # Must match Django URL exactly
        "AccountReference": account_reference, # Usually order ID
        "TransactionDesc": transaction_desc
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # raise error if network or HTTP issue
    return response.json()
