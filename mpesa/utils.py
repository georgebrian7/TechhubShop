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
        self.paybill_number = config('MPESA_PAYBILL_NUMBER')  # Your Paybill number
        self.passkey = config('MPESA_PASSKEY')
        self.callback_url = config('MPESA_CALLBACK_URL')
        
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def get_access_token(self):
        """Generate access token"""
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        
        response = requests.get(
            url,
            auth=(self.consumer_key, self.consumer_secret)
        )
        
        return response.json().get('access_token')
    
    def generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = f"{self.paybill_number}{self.passkey}{timestamp}"
        encoded = b64encode(data_to_encode.encode())
        return encoded.decode('utf-8'), timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """
        Initiate STK push for Paybill
        
        Args:
            phone_number: Customer's M-Pesa phone number (format: 254XXXXXXXXX)
            amount: Amount to be paid
            account_reference: Account number to be displayed on customer's phone (max 12 chars)
            transaction_desc: Description of the transaction
        
        Note: For Paybill payments:
        - AccountReference is the account number shown to the customer (e.g., invoice number, customer ID)
        - This appears on the customer's phone as "Account No: [AccountReference]"
        - Maximum 12 characters for AccountReference
        """
        access_token = self.get_access_token()
        password, timestamp = self.generate_password()
        
        # Format phone number (remove + and ensure it starts with 254)
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        
        url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "BusinessShortCode": self.paybill_number,  # Your Paybill number
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",  # PayBill transaction type
            "Amount": int(amount),
            "PartyA": phone_number,  # Customer's phone number
            "PartyB": self.paybill_number,  # Your Paybill number (receives the payment)
            "PhoneNumber": phone_number,  # Phone number to receive the STK push
            "CallBackURL": self.callback_url,  # Your callback URL
            "AccountReference": account_reference[:12],  # Max 12 characters - Account number shown to customer
            "TransactionDesc": transaction_desc  # Transaction description
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def query_stk_status(self, checkout_request_id):
        """
        Query the status of an STK push transaction
        
        Args:
            checkout_request_id: The CheckoutRequestID from the initial STK push
        
        Returns:
            JSON response with transaction status
        """
        access_token = self.get_access_token()
        password, timestamp = self.generate_password()
        
        url = f'{self.base_url}/mpesa/stkpushquery/v1/query'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "BusinessShortCode": self.paybill_number,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()