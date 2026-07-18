import boto3
import os
import time
import sys

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION = "us-east-1"

CERT_ARN = "arn:aws:acm:us-east-1:320797584910:certificate/0617a2d8-9386-4158-8ab1-80443008524a"
S3_ENDPOINT = "masterji-tailor-online-0b5a143a.s3-website-us-east-1.amazonaws.com"

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)
acm = session.client('acm')

print("Checking ACM Certificate status...")

# Poll ACM certificate status up to 10 times (5 minutes)
for i in range(15):
    try:
        cert_details = acm.describe_certificate(CertificateArn=CERT_ARN)
        status = cert_details['Certificate']['Status']
        print(f"Attempt {i+1}/15: Certificate status is: {status}")
        
        if status == 'ISSUED':
            print("Certificate is ISSUED! Proceeding to CloudFront creation...")
            break
        elif status == 'FAILED':
            print("Certificate validation FAILED. Please check GoDaddy records.")
            sys.exit(1)
            
        print("Waiting 20 seconds for DNS validation...")
        time.sleep(20)
    except Exception as e:
        print(f"Error checking status: {e}")
        sys.exit(1)
else:
    print("Certificate is still pending validation. Please ensure CNAME records are correct in GoDaddy.")
    sys.exit(1)

# Certificate is ISSUED. Now run the CloudFront creation logic.
cf = session.client('cloudfront')
caller_ref = str(time.time())

print("Creating CloudFront Distribution...")
try:
    cf_response = cf.create_distribution(
        DistributionConfig={
            'CallerReference': caller_ref,
            'Aliases': {
                'Quantity': 2,
                'Items': ['masterji.online', 'www.masterji.online']
            },
            'DefaultRootObject': 'index.html',
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'Id': 'S3-Website-Origin',
                        'DomainName': S3_ENDPOINT,
                        'CustomOriginConfig': {
                            'HTTPPort': 80,
                            'HTTPSPort': 443,
                            'OriginProtocolPolicy': 'http-only',
                            'OriginSslProtocols': {
                                'Quantity': 3,
                                'Items': ['TLSv1', 'TLSv1.1', 'TLSv1.2']
                            },
                            'OriginReadTimeout': 30,
                            'OriginKeepaliveTimeout': 5
                        }
                    }
                ]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': 'S3-Website-Origin',
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                },
                'ViewerProtocolPolicy': 'redirect-to-https',
                'MinTTL': 0,
                'AllowedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD'],
                    'CachedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD']
                    }
                },
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {
                        'Forward': 'none'
                    },
                    'Headers': {
                        'Quantity': 0
                    },
                    'QueryStringCacheKeys': {
                        'Quantity': 0
                    }
                },
                'DefaultTTL': 86400,
                'MaxTTL': 31536000,
                'Compress': True
            },
            'Comment': 'CloudFront Distribution for Masterji.online',
            'Enabled': True,
            'ViewerCertificate': {
                'ACMCertificateArn': CERT_ARN,
                'SSLSupportMethod': 'sni-only',
                'MinimumProtocolVersion': 'TLSv1.2_2021',
                'CertificateSource': 'acm'
            }
        }
    )
    
    dist = cf_response['Distribution']
    print("\n=============================================")
    print("CLOUDFRONT DISTRIBUTION CREATED SUCCESS!")
    print(f"Status: {dist['Status']}")
    print(f"Domain Name: {dist['DomainName']}")
    print("=============================================")
except Exception as e:
    print(f"Error creating CloudFront distribution: {e}")
