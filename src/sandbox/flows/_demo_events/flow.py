from prefect import flow, task
from prefect.logging import get_run_logger
from prefect.context import get_run_context
from prefect.events import emit_event
from prefect.runtime import task_run


def logger(logger):
    # this logger instance will emit logs
    # associated with both the flow run *and* the individual task run
    logger = get_run_logger()
    logger.info("INFO level log message from a task.")
    logger.debug("DEBUG level log message from a task.")


# Task for data validation
@task
def validate_data(data):
    logger = get_run_logger()
    if not data:
        logger.info("Validation Failure: Data is empty")
        emit_event(
            event="Governance Validation Failure",
            resource={"prefect.resource.id": task_run.id},
        )
        raise ValueError("Data validation failed.")
    logger.info("Validation Success: Data validated successfully.")

    return True


# Task for auditing and compliance
@task
def generate_audit_report(events):
    logger = get_run_logger()
    logger.info("Audit Report: Generated compliance report.")
    return events


# Main flow
@flow
def governance_flow(data=None):
    logger = get_run_logger()

    initiate_validations = logger.info("Governance validations flow initiated.")
    try:
        validation = validate_data(data)
    except Exception as e:
        logger.info("Error", str(e))
        return

    end_of_validations = logger.info("Governance validations flow completed.")

    # Generate compliance report
    events = {
        "initiate_validations": initiate_validations,
        "validation": validation,
        "end_of_validations": end_of_validations,
    }

    report = generate_audit_report(events)

    context = get_run_context()

    return report, context


# Example usage
if __name__ == "__main__":
    # governance_flow()
    # governance_flow.serve(
    #     name="events-flow-demo",
    # )
    # Deploy the flow to Prefect Cloud
    governance_flow.from_source(
        source="https://github.com/griggz/griggz-prefect-collective.git",
        entrypoint="src/sandbox/flows/_demo_events/flows.py:governance_flow", 
    ).deploy(
        name="events-flow-demo",
        work_pool_name="managed-pool",
    )
