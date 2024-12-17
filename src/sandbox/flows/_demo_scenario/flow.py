from prefect import flow, task
import pandas as pd
from datetime import datetime
import time
from prefect.artifacts import create_markdown_artifact
from prefect.events import emit_event
from prefect.task_runners import ThreadPoolTaskRunner


# Mock function to simulate fetching employee data
@task
def fetch_data(endpoint):
    time.sleep(1)  # Simulate network delay
    # Mock response data
    return {
        "id": endpoint.split("/")[-1],  # Simulate an ID based on the endpoint
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "job_title": "Engineer",
        "location": "Remote",
    }

@task
def create_dataset(num_employees: int):
    endpoints = [f"https://api.example.com/employees/{i}" for i in range(1, 11)]  # Example API endpoints
    tasks = [fetch_data.submit(endpoint) for endpoint in endpoints]  # Submit tasks for each endpoint
    data = [task.wait() for task in tasks]  # Wait for all tasks to complete

    # Process the fetched data
    employee_data = []
    for i, employee in enumerate(data):
        # Check if employee data is None
        if employee is None:
            employee_data.append({
                "employee_id": i + 1,
                "start_date": "",
                "end_date": "",
                "job_title": "Unknown",
                "location": "Unknown",
            })
            continue
        
        # Ensure the employee data is valid
        employee_id = employee.get("id", i + 1)
        employee_data.append(
            {
                "employee_id": employee_id,
                "start_date": employee.get("start_date", ""),
                "end_date": employee.get("end_date", ""),
                "job_title": employee.get("job_title", ""),
                "location": employee.get("location", ""),
            }
        )

    return pd.DataFrame(employee_data)

# Note: You will need to adjust the mock response handling based on your requirements.


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
    # Safely calculate employment duration
    def calculate_duration(row):
        if row["start_date"]:
            start_date = datetime.strptime(row["start_date"], "%Y-%m-%d")
            return (datetime.now() - start_date).days
        return None  # Return None if start_date is empty

    data["employment_duration"] = data.apply(calculate_duration, axis=1)

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


@flow(task_runner=ThreadPoolTaskRunner(), log_prints=True)
def data_flow(midway_failure: bool = False):
    # Create a dataset based on upstream data
    employee_data = create_dataset(10)  # This can also be the outdated data

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
    data_flow(midway_failure=True)
