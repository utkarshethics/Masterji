import json
import os
import hmac
import hashlib
import razorpay
import urllib.request
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

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

    print("RECEIVED EVENT:", json.dumps(event))

    body_content = event.get('body', '{}')
    if event.get('isBase64Encoded', False):
        import base64
        body_content = base64.b64decode(body_content).decode('utf-8')

    try:
        body = json.loads(body_content)
    except:
        body = {}

    if path == '/create-order' and http_method == 'POST':
        return create_order(body, headers)
    elif path == '/verify-payment' and http_method == 'POST':
        return verify_payment(body, headers)
    elif path == '/chat' and http_method == 'POST':
        return chat_with_gemini(body, headers)
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

        link_data = {
            'amount': int(amount),
            'currency': currency,
            'description': 'Doorstep Tailor Booking Fee',
            'notify': {
                'sms': False,
                'email': False
            },
            'reminder_enable': False
        }

        payment_link = client.payment_link.create(link_data)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'payment_link_id': payment_link['id'],
                'url': payment_link['short_url']
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

def chat_with_gemini(body, headers):
    try:
        user_message = body.get('message', '')
        if not user_message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Message is required'})
            }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        system_prompt = """You are MasterJi, a helpful and expert AI tailor assistant for masterji.online.
Your goal is to help customers with tailoring questions, suggest fits, and encourage them to book a tailor visit.
Key information:
- We offer doorstep tailoring and alterations.
- The booking fee for a doorstep tailor visit is just ₹50.
- We offer a 7-day free alteration guarantee.
- If the user is ready to book, tell them: 'Click the "Book Now for ₹50" button below the chat to schedule your visit!'
Keep your responses very concise, friendly, and under 3-4 sentences."""

        payload = {
            "contents": [
                {
                    "parts": [{"text": user_message}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            }
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        # Need to handle SSL context for Lambda if required, but default usually works on AWS Python 3.11
        response = urllib.request.urlopen(req)
        response_data = json.loads(response.read().decode('utf-8'))
        
        bot_reply = response_data['candidates'][0]['content']['parts'][0]['text']

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'reply': bot_reply})
        }
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        print("Gemini API Error:", error_msg)
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Failed to get response from AI'})
        }
    except Exception as e:
        print("Chat Error:", str(e))
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
