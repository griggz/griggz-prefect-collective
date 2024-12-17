from prefect import flow, task
from prefect.task_runners import ThreadPoolTaskRunner
# from prefect_fivetran import FivetranCredentials
# from prefect_fivetran.connectors import fivetran_sync_flow
from prefect_dbt.cloud import DbtCloudCredentials, DbtCloudJob, run_dbt_cloud_job
import time


@task
def run_fivetran_ingestion():
    fivetran_result = None
    # Load Fivetran credentials
    # fivetran_credentials = FivetranCredentials(
    #     api_key="my_api_key",
    #     api_secret="my_api_secret",
    # )

    # Define the Fivetran sync configuration
    sync_config = {
        "connector_id": "your_connector_id",  # Replace with your Fivetran connector ID
    }

    # Run the Fivetran sync
    # fivetran_result = await fivetran_sync_flow(
    #     fivetran_credentials=fivetran_credentials,
    #     connector_id="my_connector_id",
    #     schedule_type="my_schedule_type",
    #     poll_status_every_n_seconds=30,
    # )

    time.sleep(2)
    return fivetran_result


@task
def run_dbt_transformations1(fivetran_results):
    dbt_result = [1, 2, 3]
    # Load dbt Cloud credentials
    # dbt_cloud_credentials = DbtCloudCredentials.load("CREDENTIALS-BLOCK-NAME-PLACEHOLDER")

    # Run the dbt Cloud job
    # dbt_result = await run_dbt_cloud_job(
    #     dbt_cloud_job=await DbtCloudJob.load("JOB-BLOCK-NAME-PLACEHOLDER"),
    #     targeted_retries=0,
    # )

    # core_result = DbtCoreOperation(
    #     commands=["pwd", "dbt debug", "dbt run"],
    #     project_dir="PROJECT-DIRECTORY-PLACEHOLDER",
    #     profiles_dir="PROFILES-DIRECTORY-PLACEHOLDER"
    # ).run()
    time.sleep(6)
    return dbt_result


@task
def run_dbt_transformations2(fivetran_results):
    dbt_result = [4, 5, 6]
    time.sleep(6)
    return dbt_result



@task
def trigger_tableau_refresh():
    # Custom logic for further processing

    time.sleep(2)
    return 200


@flow(task_runner=ThreadPoolTaskRunner(), log_prints=True)
def fivetran_dbt_pipeline():
    # Step 1: Run Fivetran sync to ingest data
    fivetran_results = run_fivetran_ingestion.submit()

    # Step 2: Run dbt transformations
    dbt_results1 = run_dbt_transformations1.submit(fivetran_results)
    dbt_results2 = run_dbt_transformations2.submit(fivetran_results)

    # Wait for the results of dbt transformations
    dbt_results1.wait()
    dbt_results2.wait()

    if dbt_results1.result() and dbt_results2.result():
        trigger_tableau_refresh.submit()


if __name__ == "__main__":
    fivetran_dbt_pipeline()
