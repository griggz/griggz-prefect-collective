from prefect import flow

# Example usage
if __name__ == "__main__":
    # data = [1, 2, 3]
    # governance_flow(data)
    # governance_flow.serve(
    #     name="events-flow-demo",
    # )
    # Deploy the flow to Prefect Cloud
    flow.from_source(
        source="https://github.com/griggz/griggz-prefect-collective.git",
        entrypoint="src/sandbox/flows/_demo_scenario/flow.py:data_flow",
    ).deploy(
        name="data-dependency-flow",
        work_pool_name="managed-pool",
        job_variables={
            "pip_packages": ["prefect", "tabulate", "pydantic", "pandas"],
        },
    )
