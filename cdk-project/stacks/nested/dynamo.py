from aws_cdk import (
    NestedStack,
    aws_dynamodb as ddb,
    RemovalPolicy
)
from constructs import Construct


class DynamoDBStack(NestedStack):
    def __create_job_tracking_table(self):
        return ddb.Table(
            self, 'BatchJobsTrackingTable',
            table_name='BatchJobsTracking',
            partition_key=ddb.Attribute(name='JobId', type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST
        )

    def __create_container_instance_tracking_table(self):
        return ddb.Table(
            self, 'ContainerInstanceTrackingTable',
            table_name='ContainerInstanceTracking',
            partition_key=ddb.Attribute(name='ContainerInstanceArn', type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST
        )

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.job_tracking_table = self.__create_job_tracking_table()
        self.container_instance_tracking_table = self.__create_container_instance_tracking_table()
