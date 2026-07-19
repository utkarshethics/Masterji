import boto3
import os
import zipfile

# Create a zip of the backend directory
zip_path = 'backend.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('backend'):
        for file in files:
            if '__pycache__' not in root:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'backend')
                zipf.write(file_path, arcname)

print("Created backend.zip")

lambda_client = boto3.client('lambda', region_name='us-east-1')

with open(zip_path, 'rb') as f:
    zipped_code = f.read()

print("Updating Lambda function code...")
lambda_client.update_function_code(
    FunctionName='razorpay-backend',
    ZipFile=zipped_code
)
print("Update successful.")
