import boto3
import os
import mimetypes

BUCKET_NAME = "masterji-tailor-online-75e1fef7"
s3 = boto3.client('s3')

def upload_dir(local_dir, s3_prefix=""):
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            if file.endswith('.py') or file == '.gitignore' or file == 'task.md' or file == 'walkthrough.md' or file == 'implementation_plan.md' or file.startswith('.'):
                continue
                
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dir)
            
            # Replace windows slashes with forward slashes for S3
            s3_key = relative_path.replace("\\", "/")
            if s3_prefix:
                s3_key = f"{s3_prefix}/{s3_key}"
                
            content_type, _ = mimetypes.guess_type(local_path)
            if content_type is None:
                if file.endswith('.css'):
                    content_type = 'text/css'
                elif file.endswith('.js'):
                    content_type = 'application/javascript'
                else:
                    content_type = 'binary/octet-stream'
            
            print(f"Uploading {local_path} to s3://{BUCKET_NAME}/{s3_key} as {content_type}")
            with open(local_path, "rb") as f:
                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=s3_key,
                    Body=f,
                    ContentType=content_type
                )

print("Starting S3 sync...")
upload_dir(".")
print("Sync complete.")
