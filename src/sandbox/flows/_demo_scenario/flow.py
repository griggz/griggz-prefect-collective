from prefect import flow, task
import pandas as pd
import random
from datetime import datetime, timedelta
import time
from prefect.artifacts import create_markdown_artifact
from prefect.events import emit_event


# Create a base dataset
def create_employee_dataset(num_employees: int):
    job_titles = ["Engineer", "Manager", "Analyst", "Designer", "Sales"]
    locations = ["New York", "San Francisco", "Chicago", "Austin", "Remote"]

    data = []
    for i in range(num_employees):
        start_date = datetime.now() - timedelta(days=random.randint(0, 365))
        end_date = (
            start_date + timedelta(days=random.randint(30, 365))
            if random.choice([True, False])
            else ""
        )
        job_title = random.choice(job_titles)
        location = random.choice(locations)

        data.append(
            {
                "employee_id": i + 1,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d") if end_date else "",
                "job_title": job_title,
                "location": location,
            }
        )

    return pd.DataFrame(data)


@task
def upstream_task_1(simulate_failure: bool):
    if simulate_failure:
        raise Exception("Upstream Task 1 failed: No updated data found.")
    print("Upstream Task 1 completed successfully.")
    return "Data from upstream task 1"


@task
def upstream_task_2(simulate_failure: bool):
    if simulate_failure:
        raise Exception("Upstream Task 2 failed: No updated data found.")
    print("Upstream Task 2 completed successfully.")
    return "Data from upstream task 2"


@task
def analyze(data):
    print("Analyzing data...")
    time.sleep(2)  # Sleep for 2 seconds
    analysis_result = data["job_title"].value_counts().to_dict()
    return analysis_result


@task
def gauge_warehouse_availability(simulate_error: bool):
    time.sleep(2)  # Sleep for 2 seconds
    if simulate_error:
        emit_event(
            event="Warehouse Availability Failure",
            resource={"prefect.resource.id": "warehouse_id_1"},
        )
        raise Exception("Midway Task failed: Simulated error.")
    print("Midway Task completed successfully.")


@task
def validate(data, analysis_result):
    print("Validating data...")
    time.sleep(2)  # Sleep for 2 seconds
    missing_end_dates = data[data["end_date"] == ""]
    # You can use analysis_result here for validation logic if needed
    return len(missing_end_dates)


@task
def review(analysis_result, validation_result):
    print("Reviewing data...")
    time.sleep(2)  # Sleep for 2 seconds
    review_result = {
        "analysis": analysis_result,
        "missing_end_dates": validation_result,
    }
    return review_result


@task
def transform(data, midway_failure: bool, review_result: dict):
    print("Transforming data...")
    time.sleep(2)  # Sleep for 2 seconds
    data["employment_duration"] = data.apply(
        lambda row: (
            datetime.now() - datetime.strptime(row["start_date"], "%Y-%m-%d")
        ).days,
        axis=1,
    )
    # Run the midway task that may simulate an error
    try:
        gauge_warehouse_availability(midway_failure)
    except Exception as e:
        print(f"Warning: {e}. Continuing with the flow.")

    return data


@task
def submit(data):
    print("Submitting data...")
    time.sleep(2)  # Sleep for 2 seconds
    markdown_table = data.to_markdown(index=False)
    print(markdown_table)  # Print the markdown table for visibility
    create_markdown_artifact(
        key="audit-report",
        markdown=markdown_table,
        description="Employee Data",
    )
    return markdown_table


@task
def special_task_for_engineers(data):
    print("Special task for Engineers...")
    time.sleep(2)  # Sleep for 2 seconds
    engineers = data[data["job_title"] == "Engineer"]
    return engineers


@task
def special_task_for_remote(data):
    print("Special task for Remote employees...")
    time.sleep(2)  # Sleep for 2 seconds
    remote_employees = data[data["location"] == "Remote"]
    return remote_employees


@flow
def data_flow(midway_failure: bool = False):
    # Create a dataset based on upstream data
    employee_data = create_employee_dataset(10)  # This can also be the outdated data

    # Analyze the employee data
    analysis_result = analyze(employee_data)

    # Validate the employee data using the analysis result
    validation_result = validate(employee_data, analysis_result)

    # Review the analysis and validation results
    review_result = review(analysis_result, validation_result)

    # Transform the employee data
    transformed_data = transform(employee_data, midway_failure, review_result)

    # Trigger special tasks based on conditions and run them concurrently
    engineer_task = None
    remote_task = None

    if "Engineer" in employee_data["job_title"].values:
        engineer_task = special_task_for_engineers.submit(transformed_data)

    if "Remote" in employee_data["location"].values:
        remote_task = special_task_for_remote.submit(transformed_data)

    # Wait for special tasks to complete
    engineer_data = engineer_task.wait() if engineer_task else None
    remote_data = remote_task.wait() if remote_task else None

    # Submit the transformed data
    submission_result = submit(transformed_data)

    return {
        "analysis": analysis_result,
        "validation": validation_result,
        "review": review_result,
        "submission": submission_result,
        "engineers": engineer_data,
        "remote": remote_data,
    }


# Example of running the flow
if __name__ == "__main__":
    data_flow(midway_failure=False)
