"""
@Author: Borja Pérez Guasch <bpguasch@amazon.es>
@Description: this script is meant to be automatically executed when there is a task state change.
It associates an AWS Batch job with its container instance.
"""

import boto3
import os

DDB_RESOURCE = boto3.resource('dynamodb')
CONTAINER_INSTANCE_TRACKING_TABLE = DDB_RESOURCE.Table(os.environ['CONTAINER_INSTANCE_TRACKING_TABLE'])
JOBS_TRACKING_TABLE = DDB_RESOURCE.Table(os.environ['JOBS_TRACKING_TABLE'])


def extract_job_id(event):
    for override in event['detail']['overrides']['containerOverrides'][0]['environment']:
        if override['name'] == 'AWS_BATCH_JOB_ID':
            return override['value']

    return None


def retrieve_container_instance(arn):
    return CONTAINER_INSTANCE_TRACKING_TABLE.get_item(Key={'ContainerInstanceArn': arn})['Item']


def hydrate_job_with_container_instance(job_id, container_instance):
    update_expressions = []
    attr_names = {}
    attr_values = {}

    for i, element in enumerate(container_instance.items()):
        update_expressions.append(f'#n{i} = :v{i}')
        attr_names[f'#n{i}'] = element[0]
        attr_values[f':v{i}'] = element[1]

    JOBS_TRACKING_TABLE.update_item(
        Key={'JobId': job_id},
        UpdateExpression=f'SET {",".join(update_expressions)}',
        ExpressionAttributeValues=attr_values,
        ExpressionAttributeNames=attr_names
    )


def handler(event, context):
    container_instance_arn = event['detail']['containerInstanceArn']
    job_id = extract_job_id(event)

    if job_id is not None:
        container_instance = retrieve_container_instance(container_instance_arn)
        hydrate_job_with_container_instance(job_id, container_instance)
