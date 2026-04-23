# myapp/mpesa.py
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64

# Replace these with your real credentials
MPESA_CONSUMER_KEY = "Q2aTAjgS4wQuTugXE6b2Ld7HFehBQVnTUSXxLBbE654Bk8GD"
MPESA_CONSUMER_SECRET = "J6xzvBIXASLb731G1jre2GqEED5lVA3GzvgPfByI1yOsBAIqjg2z3E6C4pfmAAlt"
MPESA_SHORTCODE = "YOUR_SHORTCODE"
MPESA_PASSKEY = "YOUR_PASSKEY"
MPESA_ENVIRONMENT = "sandbox"  # or "production"

def get_access_token():
    if MPESA_ENVIRONMENT == "sandbox":
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    else:
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(url, auth=HTTPBasicAuth(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    data = response.json()
    return data['access_token']

def lipa_na_mpesa(phone_number, amount, account_reference, transaction_desc):
    token = get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = MPESA_SHORTCODE + MPESA_PASSKEY + timestamp
    password = base64.b64encode(password_str.encode()).decode()

    if MPESA_ENVIRONMENT == "sandbox":
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    else:
        url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/mpesa/callback/",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
