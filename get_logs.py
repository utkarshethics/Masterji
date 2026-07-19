import boto3
import time

client = boto3.client('logs', region_name='us-east-1')
log_group = '/aws/lambda/razorpay-backend'

try:
    streams = client.describe_log_streams(
        logGroupName=log_group,
        orderBy='LastEventTime',
        descending=True,
        limit=1
    )
    
    if streams['logStreams']:
        stream_name = streams['logStreams'][0]['logStreamName']
        events = client.get_log_events(
            logGroupName=log_group,
            logStreamName=stream_name,
            limit=50
        )
        for event in events['events']:
            print(event['message'])
    else:
        print("No log streams found.")
except Exception as e:
    print("Error:", e)
