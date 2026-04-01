import requests
import json
from datetime import datetime
from base64 import b64encode
from decouple import config

class MpesaAPI:
    def __init__(self):
        self.environment = config('MPESA_ENVIRONMENT', default='sandbox')
        self.consumer_key = config('MPESA_CONSUMER_KEY')
        self.consumer_secret = config('MPESA_CONSUMER_SECRET')
        self.TILL_NUMBER = config('TILL_NUMBER')  # ✅ BUY GOODS TILL
        self.passkey = config('MPESA_PASSKEY')
        self.callback_url = config('MPESA_CALLBACK_URL')

        # ✅ Base URL
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'

    # ✅ 1. ACCESS TOKEN
    def get_access_token(self):
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'

        response = requests.get(
            url,
            auth=(self.consumer_key, self.consumer_secret)
        )

        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise Exception(f"Access token error: {response.text}")

    # ✅ 2. PASSWORD GENERATION
    def generate_password(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = f"{self.TILL_NUMBER}{self.passkey}{timestamp}"

        encoded = b64encode(data_to_encode.encode())
        return encoded.decode('utf-8'), timestamp

    # ✅ 3. FORMAT PHONE NUMBER
    def format_phone(self, phone_number):
        phone_number = phone_number.replace(" ", "")

        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        if not phone_number.startswith('254'):
            phone_number = '254' + phone_number

        return phone_number

    # ✅ 4. STK PUSH (BUY GOODS)
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        access_token = self.get_access_token()
        password, timestamp = self.generate_password()

        phone_number = self.format_phone(phone_number)

        url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "BusinessShortCode": self.TILL_NUMBER,  # ✅ TILL NUMBER
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",  # ✅ BUY GOODS
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.TILL_NUMBER,  # ✅ SAME TILL
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference[:12],  # Not critical in Buy Goods
            "TransactionDesc": transaction_desc,
        }

        response = requests.post(url, json=payload, headers=headers)

        try:
            return response.json()
        except Exception:
            return {
                "error": "Invalid response",
                "raw": response.text
            }

    # ✅ 5. QUERY STK STATUS
    def query_stk_status(self, checkout_request_id):
        access_token = self.get_access_token()
        password, timestamp = self.generate_password()

        url = f'{self.base_url}/mpesa/stkpushquery/v1/query'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "BusinessShortCode": self.TILL_NUMBER,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        response = requests.post(url, json=payload, headers=headers)

        try:
            return response.json()
        except Exception:
            return {
                "error": "Invalid response",
                "raw": response.text
            }