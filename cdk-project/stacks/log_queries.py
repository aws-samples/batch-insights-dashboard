JOB_LOG_HISTORY = \
'''
fields @timestamp, JobId, JobName, JobQueue, JobDefinition, Status, TotalRunnableSeconds, TotalStartingSeconds, TotalRunningSeconds, AvailabilityZone, InstanceType, Architecture
| sort @timestamp desc
'''


def build_count_query(by_field, label='Count'):
    return f'''
fields {by_field}
| stats count(*) as {label} by {by_field}
'''


def build_succeeded_rate_query(by_field):
    return f'stats sum(Status="SUCCEEDED") / count(*) * 100 as Percentage by {by_field}'


def build_avg_running_query(by_field):
    return f'''
fields {by_field}
| stats avg(TotalRunningSeconds) / 60 as Minutes by {by_field}
'''


def build_avg_runnable_query(by_field):
    return f'''
fields f{by_field}
| stats avg(TotalRunnableSeconds) / 60 as Minutes by {by_field}
'''


def build_avg_starting_query(by_field):
    return f'''
fields f{by_field}
| stats avg(TotalStartingSeconds) / 60 as Minutes by {by_field}
'''
