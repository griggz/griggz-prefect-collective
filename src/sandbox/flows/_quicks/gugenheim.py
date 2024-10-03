from time import sleep
from prefect import flow, task
from prefect.logging import get_run_logger


# Task for data validation
@task(retries=1, retry_delay_seconds=5)
def ingest_raw_data(data):
    logger = get_run_logger()
    logger.info("Validation Success: Data validated successfully.")
    sleep(5)

    return data


# Task for auditing and compliance
@task
def find_nulls_in_df(data):
    logger = get_run_logger()
    logger.info("Audit Report: Generated compliance report.")
    sleep(2)
    return data


@task
def historical_raw_integration(data):
    logger = get_run_logger()
    logger.info("Audit Report: Generated compliance report.")
    sleep(2)
    return data


@task
def get_geographical_data(data):
    sleep(2)
    return data


@flow(name="load-in-historical-data")
def list_s3_objects(item):
    get_geographical_data(item)
    sleep(2)
    return data


# Main flow
@flow
def gugenheim_sample(data=[1, 2, 3]):
    validation = ingest_raw_data(data)
    null = find_nulls_in_df(validation)
    # raw_source = historical_raw_integration(null)

    for item in [0, 1, 3]:
        list_s3_objects(item)

    return validation


# Example usage
if __name__ == "__main__":
    data = [1, 2, 3]
    gugenheim_sample(data)
