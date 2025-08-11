from prefect import flow

from prefect.client.schemas.objects import (
    ConcurrencyLimitConfig, 
    ConcurrencyLimitStrategy
)

if __name__ == "__main__":
    with open('requirements.txt', 'r') as file:
        requirements = file.read().splitlines()


    # Deploy the flow
    flow.from_source(
        source="https://<PAT>@<domain>.visualstudio.com/<domain>/_git/<repository>",
        entrypoint="sandbox/flows/_demo/flow.py:take_a_walk",
    ).deploy(
        name="take-a-walk-demo",
        work_pool_name="default",
        job_variables={"pip_packages": requirements},
        concurrency_limit=ConcurrencyLimitConfig(
            limit=3, collision_strategy=ConcurrencyLimitStrategy.CANCEL_NEW
        ),
    )
