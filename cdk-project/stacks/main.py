from aws_cdk import (
    Stack
)
from constructs import Construct
from .nested import *


class MainStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ddb_stack = DynamoDBStack(self, 'DynamoDBStack')
        cloudwatch_stack = CloudWatchStack(self, 'CloudWatchStack')
        lambda_stack = LambdaStack(self, 'LambdaStack', cloudwatch_stack, ddb_stack)
        EventBridgeStack(self, 'EventBridgeStack', lambda_stack)
