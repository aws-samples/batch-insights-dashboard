"""
@Author: Borja Pérez Guasch <bpguasch@amazon.es>
@Description: this script is meant to be automatically executed when a container instance is registered / deregistered.
It either tracks in DynamoDB some container instance's attributes or deletes the tracked information.
"""

import boto3
import os


CONTAINER_INSTANCE_TRACKING_TABLE = boto3.resource('dynamodb').Table(os.environ['CONTAINER_INSTANCE_TRACKING_TABLE'])


def extract_container_instance_attributes(container_instance):
    attrs = {
        'ContainerInstanceArn': container_instance['containerInstanceArn'],
        'InstanceId': container_instance['ec2InstanceId']
    }

    for attr in container_instance['attributes']:
        if attr['name'] == 'ecs.availability-zone':
            attrs['AvailabilityZone'] = attr['value']
        elif attr['name'] == 'ecs.cpu-architecture':
            attrs['Architecture'] = attr['value']
        elif attr['name'] == 'ecs.instance-type':
            attrs['InstanceType'] = attr['value']

    return attrs


def track_container_instance(container_instance):
    CONTAINER_INSTANCE_TRACKING_TABLE.put_item(Item=container_instance)


def delete_container_instance(arn):
    CONTAINER_INSTANCE_TRACKING_TABLE.delete_item(Key={'ContainerInstanceArn': arn})


def handler(event, context):
    if event['detail']['status'] == 'ACTIVE':
        container_instance = extract_container_instance_attributes(event['detail'])
        track_container_instance(container_instance)
    else:
        container_instance_arn = event['detail']['containerInstanceArn']
        delete_container_instance(container_instance_arn)
