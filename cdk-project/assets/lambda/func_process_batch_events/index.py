"""
@Author: Borja Pérez Guasch <bpguasch@amazon.es>
@Description: this is script is meant to be automatically executed when there is a status change in an AWS Batch job.
It 1) tracks the job status change in a DynamoDB table and 2) logs all the job information to CloudWatch when the job
has completed its execution.
"""

import os
import boto3
import time
import json
import datetime


JOBS_LOG_GROUP = os.environ['JOBS_LOG_GROUP']
JOBS_LOG_STREAM = os.environ['JOBS_LOG_STREAM']

COMPLETION_STATUSES = {'SUCCEEDED', 'FAILED'}
TRANSITION_STATUSES = {'RUNNABLE', 'STARTING', 'RUNNING'}

DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

LOGS_CLIENT = boto3.client('logs')
JOBS_TRACKING_TABLE = boto3.resource('dynamodb').Table(os.environ['JOBS_TRACKING_TABLE'])


def track_job_status_transition(event, job):
    JOBS_TRACKING_TABLE.update_item(
        Key={'JobId': job['JobId']},
        UpdateExpression='SET #s = :v',
        ExpressionAttributeValues={':v': event['time']},
        ExpressionAttributeNames={'#s': job['Status']}
    )


def retrieve_job_tracking_data(job_id):
    return JOBS_TRACKING_TABLE.get_item(Key={'JobId': job_id})['Item']


def delete_job_tracking_data(job_id):
    JOBS_TRACKING_TABLE.delete_item(Key={'JobId': job_id})


def calculate_job_status_durations(event, tracking_data):
    # Calculate job duration
    if 'startedAt' in event['detail'] and 'stoppedAt' in event['detail']:
        dt1 = datetime.datetime.fromtimestamp(event['detail']['startedAt'] // 1000)
        dt2 = datetime.datetime.fromtimestamp(event['detail']['stoppedAt'] // 1000)
        total_running_seconds = (dt2 - dt1).seconds
    else:
        total_running_seconds = 0

    # Convert status timestamps to date objects
    dt_runnable = datetime.datetime.strptime(tracking_data['RUNNABLE'], DT_FORMAT)
    dt_starting = datetime.datetime.strptime(tracking_data['STARTING'], DT_FORMAT)
    dt_running = datetime.datetime.strptime(tracking_data['RUNNING'], DT_FORMAT)

    tracking_data.update({
        'TotalRunnableSeconds': (dt_starting - dt_runnable).seconds,
        'TotalStartingSeconds': (dt_running - dt_starting).seconds,
        'TotalRunningSeconds': total_running_seconds
    })

    del tracking_data['RUNNABLE']
    del tracking_data['STARTING']
    del tracking_data['RUNNING']


def log_job(job):
    LOGS_CLIENT.put_log_events(
        logGroupName=JOBS_LOG_GROUP,
        logStreamName=JOBS_LOG_STREAM,
        logEvents=[
            {
                'timestamp': int(time.time()) * 1000,
                'message': json.dumps(job)
            },
        ],
    )


def handler(event, context):
    job = {
        'JobName': event['detail']['jobName'],
        'JobId': event['detail']['jobId'],
        'JobQueue': event['detail']['jobQueue'].split('/')[-1],
        'Status': event['detail']['status'],
        'JobDefinition': event['detail']['jobDefinition'].split('/')[-1],
    }

    if job['Status'] in TRANSITION_STATUSES:
        track_job_status_transition(event, job)
    elif job['Status'] in COMPLETION_STATUSES:
        tracking_data = retrieve_job_tracking_data(job['JobId'])
        calculate_job_status_durations(event, tracking_data)
        job.update(tracking_data)
        log_job(job)
        delete_job_tracking_data(job['JobId'])
