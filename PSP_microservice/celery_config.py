"""
Declaration of variables used for the Celery configureation  
in the PSP microservice
"""
broker_url = 'pyamqp://guest@localhost:5672//'
result_backend = 'rpc://'
