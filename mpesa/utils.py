import requests
import json
from datetime import datetime
from base64 import b64encode
from decouple import config
import logging

logger = logging.getLogger(__name__)

class MpesaAPI:
    def __init__(self):
        self.environment = config('MPESA_ENVIRONMENT', default='sandbox')
        self.consumer_key = config('MPESA_CONSUMER_KEY')
        self.consumer_secret = config('MPESA_CONSUMER_SECRET')
        self.till_number = config('MPESA_TILL_NUMBER')  # Changed from paybill_number
        self.passkey = config('MPESA_PASSKEY')
        self.callback_url = config('MPESA_CALLBACK_URL')
        
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def get_access_token(self):
        """Generate access token"""
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        
        try:
            logger.info(f"Requesting access token from: {url}")
            
            response = requests.get(
                url,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=30
            )
            
            logger.info(f"Access token response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    access_token = data.get('access_token')
                    if access_token:
                        logger.info("✅ Access token obtained successfully")
                        return access_token
                    else:
                        raise Exception("No access_token in response")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON response: {response.text}")
                    raise Exception(f"Invalid JSON response from M-Pesa: {str(e)}")
            else:
                logger.error(f"❌ Failed to get access token. Status: {response.status_code}")
                raise Exception(f"Failed to get access token: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
    
    def generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = f"{self.till_number}{self.passkey}{timestamp}"
        encoded = b64encode(data_to_encode.encode())
        return encoded.decode('utf-8'), timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """
        Initiate STK push for Till Number (Buy Goods)
        
        Args:
            phone_number: Customer's M-Pesa phone number (format: 254XXXXXXXXX)
            amount: Amount to be paid
            account_reference: Optional reference (not shown to customer for Till)
            transaction_desc: Description of the transaction
        
        Note: For Till Number payments:
        - TransactionType is CustomerBuyGoodsOnline
        - Account reference is NOT shown to customer
        - Customer only sees Till number and amount
        """
        try:
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()
            
            # Format phone number
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]
            if phone_number.startswith('0') and len(phone_number) == 10:
                phone_number = '254' + phone_number[1:]
            if len(phone_number) == 9 and (phone_number.startswith('7') or phone_number.startswith('1')):
                phone_number = '254' + phone_number
            # Validate phone number
            if not phone_number.startswith('254') or len(phone_number) != 12:
                raise Exception(f"Invalid phone number format: {phone_number}")
            
            url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # TILL NUMBER PAYLOAD - Key differences from Paybill
            payload = {
                "BusinessShortCode": self.till_number,  # Till number
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerBuyGoodsOnline",  # ← Changed from PayBill
                "Amount": int(amount),
                "PartyA": phone_number,  # Customer's phone number
                "PartyB": self.till_number,  # Till number (receives payment)
                "PhoneNumber": phone_number,  # Phone to receive STK push
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,  # Optional, not shown to customer
                "TransactionDesc": transaction_desc  # Transaction description
            }
            
            logger.info(f"Sending Till Number STK push to: {url}")
            logger.info(f"Payload: {json.dumps({**payload, 'Password': '***'}, indent=2)}")
            
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            
            logger.info(f"STK push response status: {response.status_code}")
            logger.info(f"STK push response: {response.text}")
            
            if not response.text or response.text.strip() == '':
                raise Exception("Empty response from M-Pesa API")
            
            try:
                result = response.json()
                
                if 'errorCode' in result:
                    error_msg = result.get('errorMessage', 'Unknown error')
                    logger.error(f"❌ M-Pesa API error: {error_msg}")
                    return {
                        'ResponseCode': '1',
                        'ResponseDescription': error_msg,
                        'errorMessage': error_msg
                    }
                
                logger.info("✅ STK push sent successfully")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in response: {response.text}")
                raise Exception(f"Invalid response from M-Pesa: {response.text[:100]}")
            
        except Exception as e:
            logger.error(f"❌ Error in stk_push: {str(e)}")
            raise
    
    def query_stk_status(self, checkout_request_id):
        """Query the status of an STK push transaction"""
        try:
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()
            
            url = f'{self.base_url}/mpesa/stkpushquery/v1/query'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": self.till_number,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            logger.info(f"Querying STK status for: {checkout_request_id}")
            
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Query response: {response.text}")
            
            if response.text and response.text.strip():
                return response.json()
            else:
                raise Exception("Empty response from status query")
                
        except Exception as e:
            logger.error(f"❌ Error querying STK status: {str(e)}")
            raise