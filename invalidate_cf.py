import boto3
import os
import time

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION = "us-east-1"

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)
cf = session.client('cloudfront')

print("Locating CloudFront distribution for masterji.online...")
try:
    response = cf.list_distributions()
    dist_id = None
    if 'DistributionList' in response and 'Items' in response['DistributionList']:
        for dist in response['DistributionList']['Items']:
            aliases = dist.get('Aliases', {}).get('Items', [])
            if 'masterji.online' in aliases or 'www.masterji.online' in aliases:
                dist_id = dist['Id']
                print(f"Found distribution: {dist_id} ({dist['DomainName']})")
                break
                
    if not dist_id:
        print("Could not find CloudFront distribution for masterji.online.")
        exit(1)
        
    print(f"Creating cache invalidation for distribution {dist_id}...")
    inval_resp = cf.create_invalidation(
        DistributionId=dist_id,
        InvalidationBatch={
            'Paths': {
                'Quantity': 1,
                'Items': ['/*']
            },
            'CallerReference': str(time.time())
        }
    )
    print(f"Invalidation created successfully. ID: {inval_resp['Invalidation']['Id']}")
except Exception as e:
    print(f"Error: {e}")
