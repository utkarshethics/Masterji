import boto3
import os

BUCKET_NAME = "masterji-tailor-online-75e1fef7"
FILES = ["index.html", "terms.html", "privacy.html"]

s3 = boto3.client('s3')

for file in FILES:
    content_type = "text/html"
    print(f"Uploading {file} to {BUCKET_NAME}...")
    with open(file, "rb") as f:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file,
            Body=f,
            ContentType=content_type
        )
print("Files uploaded successfully.")
