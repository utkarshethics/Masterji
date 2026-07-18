import boto3
import os
import time

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION = "us-east-1" # CloudFront requires ACM certs to be in us-east-1

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)

acm = session.client('acm')

print("Requesting SSL Certificate for masterji.online and www.masterji.online...")
try:
    cert_response = acm.request_certificate(
        DomainName='masterji.online',
        ValidationMethod='DNS',
        SubjectAlternativeNames=['www.masterji.online']
    )
    cert_arn = cert_response['CertificateArn']
    print(f"Certificate requested successfully. ARN: {cert_arn}")
    
    # Wait a few seconds for DNS validation records to generate
    print("Waiting for DNS validation records to be generated...")
    time.sleep(10)
    
    cert_details = acm.describe_certificate(CertificateArn=cert_arn)
    options = cert_details['Certificate']['DomainValidationOptions']
    
    print("\n=============================================")
    print("ADD THESE CNAME RECORDS TO GODADDY TO VALIDATE SSL:")
    print("=============================================")
    for opt in options:
        record = opt.get('ResourceRecord')
        if record:
            print(f"Domain: {opt['DomainName']}")
            print(f"  Type: CNAME")
            print(f"  Name: {record['Name']}")
            print(f"  Value: {record['Value']}")
            print("---------------------------------------------")
        else:
            print(f"Validation record not ready for {opt['DomainName']}. Please re-run script in a minute.")
            
except Exception as e:
    print(f"Error: {e}")
