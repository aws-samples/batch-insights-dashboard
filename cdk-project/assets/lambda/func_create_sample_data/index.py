import os
import boto3
import time
import json
import uuid
import random


JOBS_LOG_GROUP = os.environ['JOBS_LOG_GROUP']
JOBS_LOG_STREAM = os.environ['JOBS_LOG_STREAM']

N_SAMPLES = 100
QUEUES = ['Stitching', 'Rendering']
STATUSES = ['SUCCEEDED', 'FAILED']
JOB_DEFS = ['StitchingDef:1', 'RenderingDef:1', 'RenderingDef:2']
AZS = ['eu-west-1a', 'eu-west-1b', 'eu-west-1c']
ARCHS = ['x86_64', 'arm64']
INSTANCES = ['c5.8xlarge', 'm4.large', 'c6g.4xlarge', 'c6g.2xlarge', 'm7g.16xlarge']


if __name__ == '__main__':
    job_events = []
    client = boto3.client('logs')

    for i in range(N_SAMPLES):
        job = {
            'JobName': f'Job-{i}',
            'JobId': str(uuid.uuid4()),
            'InstanceId': str(uuid.uuid4()),
            'JobQueue': random.choice(QUEUES),
            'Status': random.choice(STATUSES),
            'JobDefinition': random.choice(JOB_DEFS),
            'AvailabilityZone': random.choice(AZS),
            'Architecture': random.choice(ARCHS),
            'InstanceType': random.choice(INSTANCES)
        }

        job['TotalRunnableSeconds'] = random.randint(1, 3600 if job['Architecture'] == 'x86_64' else 2600)
        job['TotalStartingSeconds'] = random.randint(5, 100 if job['Architecture'] == 'x86_64' else 80)
        job['TotalRunningSeconds'] = random.randint(60, 7200 if job['Architecture'] == 'x86_64' else 5200)

        job_events.append({
            'timestamp': int(time.time()) * 1000,
            'message': json.dumps(job)
        })

    client.put_log_events(
        logGroupName=JOBS_LOG_GROUP,
        logStreamName=JOBS_LOG_STREAM,
        logEvents=job_events
    )
