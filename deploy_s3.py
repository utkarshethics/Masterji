import boto3
import json
import os
import mimetypes
import uuid

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION = "ap-south-1"
BUCKET_NAME = "masterji-tailor-online-" + str(uuid.uuid4())[:8]

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)
s3 = session.client('s3')

print(f"Creating S3 Bucket: {BUCKET_NAME}...")

# Create bucket
try:
    if REGION == 'us-east-1':
        s3.create_bucket(Bucket=BUCKET_NAME)
    else:
        s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': REGION})
    print(f"Created bucket {BUCKET_NAME}")
except Exception as e:
    print(f"Bucket creation error: {e}")
    exit(1)

# Disable Block Public Access
s3.delete_public_access_block(Bucket=BUCKET_NAME)

# Set bucket policy
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
    }]
}
s3.put_bucket_policy(Bucket=BUCKET_NAME, Policy=json.dumps(bucket_policy))
print("Applied public read bucket policy")

# Configure website
website_configuration = {
    'ErrorDocument': {'Key': 'index.html'},
    'IndexDocument': {'Suffix': 'index.html'},
}
s3.put_bucket_website(Bucket=BUCKET_NAME, WebsiteConfiguration=website_configuration)
print("Configured bucket for static website hosting")

# Upload files
files_to_upload = ['index.html', 'styles.css', 'script.js', 'logo.png.jpeg']
for file_name in files_to_upload:
    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
    if file_name == 'logo.png.jpeg':
        content_type = 'image/jpeg'
    s3.upload_file(file_name, BUCKET_NAME, file_name, ExtraArgs={'ContentType': content_type})
    print(f"Uploaded {file_name}")

website_url = f"http://{BUCKET_NAME}.s3-website.{REGION}.amazonaws.com"
print(f"\n============================================\nDeployment Complete!\nYour website is live at:\n{website_url}\n============================================")
