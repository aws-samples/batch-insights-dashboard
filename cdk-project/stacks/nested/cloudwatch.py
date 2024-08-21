from aws_cdk import (
    NestedStack,
    RemovalPolicy,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
)
from constructs import Construct
from .. import log_queries


class CloudWatchStack(NestedStack):
    __LOG_GROUP_RETENTION_PERIOD = logs.RetentionDays.ONE_YEAR

    # -------------------- WIDGET HELPER METHODS -------------------- #

    def __build_succeeded_rate_widget(self, by_field):
        return cloudwatch.LogQueryWidget(
            log_group_names=[self.jobs_log_group.log_group_name],
            height=6,
            width=12,
            query_string=log_queries.build_succeeded_rate_query(by_field),
            title='Succeeded rate',
            view=cloudwatch.LogQueryVisualizationType.BAR
        )

    def __build_avg_running_widget(self, by_field):
        return cloudwatch.LogQueryWidget(
            log_group_names=[self.jobs_log_group.log_group_name],
            height=6,
            width=12,
            query_string=log_queries.build_avg_running_query(by_field),
            title='Average RUNNING duration (minutes)',
            view=cloudwatch.LogQueryVisualizationType.BAR
        )

    def __build_avg_runnable_widget(self, by_field):
        return cloudwatch.LogQueryWidget(
            log_group_names=[self.jobs_log_group.log_group_name],
            height=6,
            width=12,
            query_string=log_queries.build_avg_runnable_query(by_field),
            title='Average RUNNABLE duration (minutes)',
            view=cloudwatch.LogQueryVisualizationType.BAR
        )

    def __build_avg_starting_widget(self, by_field):
        return cloudwatch.LogQueryWidget(
            log_group_names=[self.jobs_log_group.log_group_name],
            height=6,
            width=12,
            query_string=log_queries.build_avg_starting_query(by_field),
            title='Average STARTING duration (minutes)',
            view=cloudwatch.LogQueryVisualizationType.BAR
        )

    # -------------------- /WIDGET HELPER METHODS -------------------- #

    def __create_jobs_log_group(self):
        log_group = logs.LogGroup(
            self, 'BatchJobsLogGroup',
            log_group_name='/aws-batch-insights/jobs',
            retention=self.__LOG_GROUP_RETENTION_PERIOD,
            removal_policy=RemovalPolicy.DESTROY
        )

        log_stream = logs.LogStream(
            self, 'BatchJobsLogStream',
            log_group=log_group,
            log_stream_name='Jobs',
            removal_policy=RemovalPolicy.DESTROY
        )

        return log_group, log_stream

    def __create_job_analysis_widgets(self):
        title = cloudwatch.TextWidget(
            markdown='# Batch jobs overview',
            background=cloudwatch.TextWidgetBackground.TRANSPARENT,
            height=1,
            width=24
        )

        job_status_overview = cloudwatch.LogQueryWidget(
            log_group_names=[self.jobs_log_group.log_group_name],
            height=6,
            width=7,
            query_string=log_queries.build_count_query('Status', 'Job_Status'),
            title='Succeeded / Failed ratio',
            view=cloudwatch.LogQueryVisualizationType.PIE
        )

        job_log_history = cloudwatch.LogQueryWidget(
            log_group_names=[self.jobs_log_group.log_group_name],
            height=job_status_overview.height,
            width=24 - job_status_overview.width,
            query_string=log_queries.JOB_LOG_HISTORY,
            title='Log history',
            view=cloudwatch.LogQueryVisualizationType.TABLE
        )

        return [title, job_status_overview, job_log_history]

    def __create_queue_analysis_widgets(self):
        by_field = 'JobQueue'

        title = cloudwatch.TextWidget(
            markdown='# Job queue analysis\nThe widgets in this section show how your jobs have performed at the **job queue** level.',
            background=cloudwatch.TextWidgetBackground.TRANSPARENT,
            height=2,
            width=24
        )

        succeeded_rate = self.__build_succeeded_rate_widget(by_field)
        avg_runtime = self.__build_avg_running_widget(by_field)
        avg_runnable = self.__build_avg_runnable_widget(by_field)
        avg_starting = self.__build_avg_starting_widget(by_field)

        return [title, succeeded_rate, avg_runnable, avg_starting, avg_runtime]

    def __create_job_definition_analysis_widgets(self):
        by_field = 'JobDefinition'

        title = cloudwatch.TextWidget(
            markdown='# Job definition analysis\nThe widgets in this section show how your jobs have performed at the **job definition** level.',
            background=cloudwatch.TextWidgetBackground.TRANSPARENT,
            height=2,
            width=24
        )

        succeeded_rate = self.__build_succeeded_rate_widget(by_field)
        avg_runtime = self.__build_avg_running_widget(by_field)
        avg_runnable = self.__build_avg_runnable_widget(by_field)
        avg_starting = self.__build_avg_starting_widget(by_field)

        return [title, succeeded_rate, avg_runnable, avg_starting, avg_runtime]

    def __create_job_placement_analysis_widgets(self):
        title = cloudwatch.TextWidget(
            markdown='# Job placement analysis\nThe widgets in this section show where your jobs have run.',
            background=cloudwatch.TextWidgetBackground.TRANSPARENT,
            height=2,
            width=24
        )

        instance_placement = cloudwatch.LogQueryWidget(
            log_group_names=[self.jobs_log_group.log_group_name],
            height=6,
            width=title.width,
            query_string=log_queries.build_count_query('InstanceType'),
            title='Jobs run per Instance type',
            view=cloudwatch.LogQueryVisualizationType.BAR
        )

        az_placement = cloudwatch.LogQueryWidget(
            log_group_names=[self.jobs_log_group.log_group_name],
            height=instance_placement.height,
            width=title.width / 2,
            query_string=log_queries.build_count_query('AvailabilityZone', 'AZ'),
            title='Jobs run per Availability Zone',
            view=cloudwatch.LogQueryVisualizationType.PIE
        )

        arch_placement = cloudwatch.LogQueryWidget(
            log_group_names=[self.jobs_log_group.log_group_name],
            height=instance_placement.height,
            width=az_placement.width,
            query_string=log_queries.build_count_query('Architecture', 'CPU_Arch'),
            title='Jobs run per CPU architecture',
            view=cloudwatch.LogQueryVisualizationType.PIE
        )

        return [title, instance_placement, az_placement, arch_placement]

    def __create_arch_analysis_widgets(self):
        by_field = 'Architecture'

        title = cloudwatch.TextWidget(
            markdown='# CPU architecture analysis\nThe widgets in this section show how your jobs have performed at the **CPU architecture** level.',
            background=cloudwatch.TextWidgetBackground.TRANSPARENT,
            height=2,
            width=24
        )

        succeeded_rate = self.__build_succeeded_rate_widget(by_field)
        avg_runtime = self.__build_avg_running_widget(by_field)
        avg_runnable = self.__build_avg_runnable_widget(by_field)
        avg_starting = self.__build_avg_starting_widget(by_field)

        return [title, succeeded_rate, avg_runnable, avg_starting, avg_runtime]

    def __create_dashboard(self):
        cloudwatch.Dashboard(
            self, 'AWSBatchJobsDashboard',
            dashboard_name='AWS_Batch_Insights',
            start='-P12M',
            widgets=[
                self.__create_job_analysis_widgets() +
                self.__create_job_placement_analysis_widgets() +
                self.__create_arch_analysis_widgets() +
                self.__create_job_definition_analysis_widgets() +
                self.__create_queue_analysis_widgets()
            ]
        )

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.jobs_log_group, self.jobs_log_stream = self.__create_jobs_log_group()
        self.__create_dashboard()
