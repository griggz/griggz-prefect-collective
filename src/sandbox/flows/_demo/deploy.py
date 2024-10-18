from prefect import flow
 

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/griggz/griggz-prefect-collective.git",
        entrypoint="src/sandbox/flows/_demo/flow.py:take_a_walk",
    ).deploy(
        name="take-a-walk-demo",
        work_pool_name="managed-pool",
    )