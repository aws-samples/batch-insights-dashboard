from aws_cdk import (
    Duration,
    NestedStack,
    aws_lambda as _lambda
)

from constructs import Construct


class LambdaStack(NestedStack):
    __LAMBDA_RUNTIME = _lambda.Runtime.PYTHON_3_12
    __LAMBDA_ARCH = _lambda.Architecture.ARM_64

    def __create_batch_events_processing_func(self, log_group, log_stream, table):
        function = _lambda.Function(
            self, 'BatchEventsProcessingFunc',
            function_name='processBatchEvents',
            runtime=self.__LAMBDA_RUNTIME,
            architecture=self.__LAMBDA_ARCH,
            handler='index.handler',
            code=_lambda.Code.from_asset('assets/lambda/func_process_batch_events'),
            timeout=Duration.minutes(1),
            retry_attempts=0,
            environment={
                'JOBS_LOG_GROUP': log_group.log_group_name,
                'JOBS_LOG_STREAM': log_stream.log_stream_name,
                'JOBS_TRACKING_TABLE': table.table_name
            }
        )

        log_group.grant_write(function)
        table.grant_read_write_data(function)

        return function

    def __create_container_instance_events_processing_func(self, table):
        function = _lambda.Function(
            self, 'ContainerInstanceEventsProcessingFunc',
            function_name='processContainerInstanceEvents',
            runtime=self.__LAMBDA_RUNTIME,
            architecture=self.__LAMBDA_ARCH,
            handler='index.handler',
            code=_lambda.Code.from_asset('assets/lambda/func_process_container_instance_events'),
            timeout=Duration.minutes(1),
            retry_attempts=0,
            environment={
                'CONTAINER_INSTANCE_TRACKING_TABLE': table.table_name
            }
        )

        table.grant_read_write_data(function)

        return function

    def __create_task_state_events_processing_func(self, container_instance_table, jobs_table):
        function = _lambda.Function(
            self, 'TaskStateEventsProcessingFunc',
            function_name='processTaskStateEvents',
            runtime=self.__LAMBDA_RUNTIME,
            architecture=self.__LAMBDA_ARCH,
            handler='index.handler',
            code=_lambda.Code.from_asset('assets/lambda/func_process_task_state_events'),
            timeout=Duration.minutes(1),
            retry_attempts=0,
            environment={
                'CONTAINER_INSTANCE_TRACKING_TABLE': container_instance_table.table_name,
                'JOBS_TRACKING_TABLE': jobs_table.table_name
            }
        )

        container_instance_table.grant_read_data(function)
        jobs_table.grant_write_data(function)

        return function

    def __init__(self, scope: Construct, construct_id: str, cloudwatch_stack, ddb_stack) -> None:
        super().__init__(scope, construct_id)

        self.batch_events_processing_func = self.__create_batch_events_processing_func(
            cloudwatch_stack.jobs_log_group, cloudwatch_stack.jobs_log_stream, ddb_stack.job_tracking_table
        )

        self.container_instance_events_processing_func = self.__create_container_instance_events_processing_func(
            ddb_stack.container_instance_tracking_table
        )

        self.task_state_events_processing_func = self.__create_task_state_events_processing_func(
            ddb_stack.container_instance_tracking_table, ddb_stack.job_tracking_table
        )
