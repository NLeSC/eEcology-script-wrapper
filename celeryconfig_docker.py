# Use redis as broker+resultstore
BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"

CELERY_IMPORTS = ("script_wrapper.tasks", )
CELERY_DISABLE_RATE_LIMITS = True
# Must be able to send revoke signal to cancel a task
CELERY_SEND_EVENTS = True
# Task expire in 12 weeks
CELERY_TASK_RESULT_EXPIRES = 7257600

CELERYD_CONCURRENCY = 2

matlab = {'location': {'2012a': '/opt/MATLAB/MATLAB_Compiler_Runtime/v717'}}
task_output_directory = '/usr/src/app/jobs'
