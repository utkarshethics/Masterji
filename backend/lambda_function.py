import json
import os
import hmac
import hashlib
import razorpay
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')

# Initialize Razorpay Client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def handler(event, context):
    path = event.get('rawPath', event.get('path', ''))
    http_method = event.get('requestContext', {}).get('http', {}).get('method', event.get('httpMethod', ''))
    
    # CORS headers for API Gateway
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }
    
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    try:
        body = json.loads(event.get('body', '{}'))
    except:
        body = {}

    if path == '/create-order' and http_method == 'POST':
        return create_order(body, headers)
    elif path == '/verify-payment' and http_method == 'POST':
        return verify_payment(body, headers)
    else:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Not Found'})
        }

def create_order(body, headers):
    try:
        amount = body.get('amount')
        currency = body.get('currency', 'INR')
        receipt = body.get('receipt', 'receipt#1')

        if not amount or int(amount) < 100:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Amount must be at least 100 paise.'})
            }

        order_data = {
            'amount': int(amount),
            'currency': currency,
            'receipt': receipt
        }

        order = client.order.create(data=order_data)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency']
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def verify_payment(body, headers):
    try:
        razorpay_order_id = body.get('razorpay_order_id')
        razorpay_payment_id = body.get('razorpay_payment_id')
        razorpay_signature = body.get('razorpay_signature')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing payment verification fields.'})
            }

        # Verify signature using HMAC-SHA256
        msg = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode('utf-8'),
            msg.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if generated_signature == razorpay_signature:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'status': 'success', 'message': 'Payment verified successfully'})
            }
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Signature verification failed. Potential tampering.'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
