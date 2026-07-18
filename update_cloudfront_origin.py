import boto3
import os

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION = "us-east-1" # CloudFront API is always us-east-1

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)
cf = session.client('cloudfront')

DISTRIBUTION_ID = "ESQN1N11WMJMD"
NEW_S3_ORIGIN_ENDPOINT = "masterji-tailor-online-75e1fef7.s3-website.ap-south-1.amazonaws.com"

print(f"Updating CloudFront distribution {DISTRIBUTION_ID} to point to Mumbai S3 bucket...")

try:
    # 1. Get current config
    get_resp = cf.get_distribution_config(Id=DISTRIBUTION_ID)
    config = get_resp['DistributionConfig']
    etag = get_resp['ETag']
    
    # 2. Update Origin Domain Name
    for origin in config['Origins']['Items']:
        if origin['Id'] == 'S3-Website-Origin':
            print(f"Updating origin domain from {origin['DomainName']} to {NEW_S3_ORIGIN_ENDPOINT}")
            origin['DomainName'] = NEW_S3_ORIGIN_ENDPOINT
            
    # 3. Save config
    update_resp = cf.update_distribution(
        DistributionConfig=config,
        Id=DISTRIBUTION_ID,
        IfMatch=etag
    )
    print("\n=============================================")
    print("CLOUDFRONT DISTRIBUTION UPDATED SUCCESS!")
    print(f"Status: {update_resp['Distribution']['Status']}")
    print("=============================================")
except Exception as e:
    print(f"Error: {e}")
