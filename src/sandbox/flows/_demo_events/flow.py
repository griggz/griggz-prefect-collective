from prefect import flow, task
from prefect.logging import get_run_logger
from prefect.context import get_run_context
from prefect.events import emit_event
from prefect.runtime import task_run
from prefect.artifacts import create_markdown_artifact
from pydantic import BaseModel
from controlflow import Agent, Task


class AuditReport(BaseModel):
    title: str
    markdown: str


auditor = Agent(
    name="Auditor",
    description="An AI agent that is an expert in auditing, compliance, and writing reports.",
    instructions="""
        Your primary goal is to validate the data, generate an audit report, and ensure that the data
        is compliant with the governance standards. You will be working with the data provided to you,
        and you will need to validate it, generate a report one paragraph long. 
        """,
)


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
def generate_audit_data(events):
    logger = get_run_logger()
    logger.info("Audit Report: Generated compliance report.")
    return events


# Task for auditing and compliance
@task
def log_artifact(markdown, title):
    logger = get_run_logger()
    logger.info("Audit Report: Logged compliance report as artifact.")
    create_markdown_artifact(
        key="audit-report",
        markdown=markdown,
        description=title,
    )


# Main flow
@flow
def governance_flow(data=[1, 2, 3]):
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

    audit_data = generate_audit_data(events)

    report = Task(
        """
            Lets take the data and write a compliance report. I want the report to be a paragraph long and
            written in markdown, and include the details of the data and the flow run status. The context I'm giving you is output of a 
            prefect flow and data. 
        """,
        context=dict(
            data=audit_data,
        ),
        result_type=AuditReport,
        agents=[auditor],
    )

    report.run()

    log_artifact(report.result.markdown, report.result.title)

    return report


# Example usage
if __name__ == "__main__":
    data = [1, 2, 3]
    # governance_flow(data)
    # governance_flow.serve(
    #     name="events-flow-demo",
    # )
    # Deploy the flow to Prefect Cloud
    flow.from_source(
        source="https://github.com/griggz/griggz-prefect-collective.git",
        entrypoint="src/sandbox/flows/_demo_events/flow.py:governance_flow",
    ).deploy(
        name="events-flow-demo",
        work_pool_name="managed-pool",
    )
