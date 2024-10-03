from datetime import timedelta
from prefect import flow, task
from prefect.cache_policies import INPUTS, RUN_ID


@task(cache_policy=INPUTS + RUN_ID, cache_expiration=timedelta(days=1))
def hello_task(name_input):
    # Doing some work
    print("Saying hello")
    return "hello " + name_input


@flow(log_prints=True)
def hello_flow(name_input):
    # reruns each time the flow is run
    hello_task(name_input) 

    # but the same call within the same flow run is Cached
    hello_task(name_input) 
