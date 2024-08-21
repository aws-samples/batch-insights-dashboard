import aws_cdk as cdk

from aws_cdk import Tags
from stacks import *


app = cdk.App()
stack = MainStack(app, "AWSBatchInsightsDashboard")

Tags.of(cdk.Stack).add("application", 'BatchInsightsDashboard')

app.synth()
