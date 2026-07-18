import boto3
import os
import sys

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION = "us-east-1"

if len(sys.argv) < 3:
    print("Usage: python create_cloudfront.py <S3_WEBSITE_ENDPOINT> <CERTIFICATE_ARN>")
    sys.exit(1)

origin_domain = sys.argv[1] # e.g. masterji-tailor-online-c766fcd8.s3-website-us-east-1.amazonaws.com
cert_arn = sys.argv[2]      # e.g. arn:aws:acm:us-east-1:320797584910:certificate/...

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)
cf = session.client('cloudfront')

# Generate a unique CallerReference using timestamp
import time
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
                        'DomainName': origin_domain,
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
                'ACMCertificateArn': cert_arn,
                'SSLSupportMethod': 'sni-only',
                'MinimumProtocolVersion': 'TLSv1.2_2021',
                'CertificateSource': 'acm'
            }
        }
    )
    
    dist = cf_response['Distribution']
    print("\n=============================================")
    print("CLOUDFRONT DISTRIBUTION CREATED!")
    print(f"Status: {dist['Status']}")
    print(f"Domain Name: {dist['DomainName']}")
    print("=============================================")
    print("\nWait for the distribution status to be 'Deployed'.")
    print("Then configure GoDaddy as instructed.")
except Exception as e:
    print(f"Error creating CloudFront distribution: {e}")
