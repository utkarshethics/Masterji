import urllib.request
import json
import ssl
import os
import datetime

# Gemini API Key
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

def generate_marketing_campaign():
    print("MasterJi Brand Manager is waking up...")
    print("Analyzing today's trends and SEO keywords...")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    system_prompt = """You are the expert Brand Manager and Social Media Marketer for 'masterji.online'.
Your goal is to increase daily SEO ranking, drive traffic, and maximize Click-Through Rates (CTA).
masterji.online is India's premium doorstep tailoring service. Users can book a tailor to visit their home for measurements for just ₹50.

Generate a daily marketing campaign outputting EXACTLY in this Markdown format:

# 📅 Daily Marketing Campaign: [Today's Date/Theme]

## 📝 SEO Blog Post (To be posted on the website)
**Title:** [Catchy, SEO-optimized title]
**Focus Keywords:** [3-4 keywords]
**Content:** [Write a 300-word engaging blog post about a tailoring topic (e.g. saree blouse fits, suit lapels, wedding season). Include a strong Call To Action (CTA) at the end pushing the ₹50 doorstep service at masterji.online].

## 📱 Social Media Posts
### 🐦 Twitter (X)
[Write an engaging, short tweet. Include emojis. End with a strong CTA to book at masterji.online for ₹50. Include 3 trending hashtags.]

### 📸 Instagram
[Write a highly engaging Instagram caption. Ask a question to drive comments. End with a CTA directing to the link in bio (masterji.online). Include 5-7 aesthetic hashtags.]

### 📘 Facebook
[Write a slightly longer, community-focused post. Explain the value of doorstep tailoring. End with a CTA and a link.]
"""

    payload = {
        "contents": [
            {
                "parts": [{"text": "Please generate today's marketing campaign and blog post to boost our SEO and CTA!"}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        response = urllib.request.urlopen(req, context=ctx)
        response_data = json.loads(response.read().decode('utf-8'))
        content = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # Save to file
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        campaign_dir = "marketing/campaigns"
        if not os.path.exists(campaign_dir):
            os.makedirs(campaign_dir)
            
        file_path = f"{campaign_dir}/{today}-campaign.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Success! Today's marketing campaign has been generated and saved to {file_path}")
        
    except Exception as e:
        print("Error generating campaign:", e)
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))

if __name__ == "__main__":
    generate_marketing_campaign()
