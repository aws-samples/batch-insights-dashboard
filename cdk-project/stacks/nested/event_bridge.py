from aws_cdk import (
    NestedStack,
    RemovalPolicy,
    aws_sqs as sqs,
    Duration,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct


class EventBridgeStack(NestedStack):
    def __create_batch_events_rule(self, target_func):
        dead_letter_queue = sqs.Queue(
            self, 'BatchEventsDeadLetterQueue',
            queue_name='BatchEventsDeadLetterQueue',
            removal_policy=RemovalPolicy.DESTROY
        )

        rule = events.Rule(
            self, 'BatchEventsRule',
            rule_name='BatchEventsRule',
            event_pattern=events.EventPattern(
                source=["aws.batch"],
                detail_type=['Batch Job State Change']
            )
        )

        rule.add_target(
            targets.LambdaFunction(
                target_func,
                dead_letter_queue=dead_letter_queue,
                max_event_age=Duration.hours(24),
                retry_attempts=2
            )
        )

        return rule

    def __create_container_instance_events_rule(self, target_func):
        dead_letter_queue = sqs.Queue(
            self, 'ContainerInstanceEventsDeadLetterQueue',
            queue_name='ContainerInstanceEventsDeadLetterQueue',
            removal_policy=RemovalPolicy.DESTROY
        )

        rule = events.Rule(
            self, 'ContainerInstanceEventsRule',
            rule_name='ContainerInstanceEventsRule',
            event_pattern=events.EventPattern(
                source=["aws.ecs"],
                detail_type=['ECS Container Instance State Change']
            )
        )

        rule.add_target(
            targets.LambdaFunction(
                target_func,
                dead_letter_queue=dead_letter_queue,
                max_event_age=Duration.hours(24),
                retry_attempts=2
            )
        )

        return rule

    def __create_task_state_events_rule(self, target_func):
        dead_letter_queue = sqs.Queue(
            self, 'TaskStateEventsDeadLetterQueue',
            queue_name='TaskStateEventsDeadLetterQueue',
            removal_policy=RemovalPolicy.DESTROY
        )

        rule = events.Rule(
            self, 'TaskStateEventsRule',
            rule_name='TaskStateEventsRule',
            event_pattern=events.EventPattern(
                source=["aws.ecs"],
                detail_type=['ECS Task State Change'],
                detail={
                    'launchType': ['EC2'],
                    'lastStatus': ['PENDING']
                }
            )
        )

        rule.add_target(
            targets.LambdaFunction(
                target_func,
                dead_letter_queue=dead_letter_queue,
                max_event_age=Duration.hours(24),
                retry_attempts=2
            )
        )

        return rule

    def __init__(self, scope: Construct, construct_id: str, lambda_stack) -> None:
        super().__init__(scope, construct_id)

        self.__create_batch_events_rule(lambda_stack.batch_events_processing_func)
        self.__create_container_instance_events_rule(lambda_stack.container_instance_events_processing_func)
        self.__create_task_state_events_rule(lambda_stack.task_state_events_processing_func)
