import boto3
import mimetypes
import os
import sys

# Requirements: pip install boto3

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

if len(sys.argv) < 2:
    print("Usage: python deploy_preconfigured.py <YOUR_BUCKET_NAME>")
    sys.exit(1)

BUCKET_NAME = sys.argv[1]

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)
s3 = session.client('s3')

print(f"Deploying to preconfigured bucket: {BUCKET_NAME}...")

# Upload files
files_to_upload = ['index.html', 'styles.css', 'script.js', 'logo.png.jpeg']
for file_name in files_to_upload:
    try:
        content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        if file_name == 'logo.png.jpeg':
            content_type = 'image/jpeg'
        
        s3.upload_file(file_name, BUCKET_NAME, file_name, ExtraArgs={'ContentType': content_type})
        print(f"Uploaded {file_name}")
    except Exception as e:
        print(f"Error uploading {file_name}: {e}")
        sys.exit(1)

print("\nDeployment to S3 Complete!")
print("Make sure your CloudFront Distribution is pointing to this S3 bucket's website endpoint.")
