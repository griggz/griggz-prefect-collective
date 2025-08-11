from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta
import time
import random
import json
import os
from typing import Dict, List, Any, Optional

# Mock data functions
def generate_mock_s3_data() -> List[Dict[str, Any]]:
    """Generate mock data that would come from S3"""
    return [
        {"id": i, "timestamp": time.time(), "source": "s3", "data": {"value": random.randint(1, 100)}}
        for i in range(5)
    ]

def generate_mock_mongodb_data() -> List[Dict[str, Any]]:
    """Generate mock data that would come from MongoDB"""
    return [
        {"_id": i, "timestamp": time.time(), "source": "mongodb", "metrics": {"engagement": random.random()}}
        for i in range(5)
    ]

def generate_mock_app_data() -> List[Dict[str, Any]]:
    """Generate mock data that would come from React App"""
    return [
        {"user_id": i, "event": random.choice(["click", "view", "purchase"]), "timestamp": time.time()}
        for i in range(5)
    ]

def generate_mock_mmp_data(platform: str) -> List[Dict[str, Any]]:
    """Generate mock data from marketing platforms"""
    return [
        {
            "campaign_id": f"{platform}_{i}",
            "spend": round(random.uniform(100, 1000), 2),
            "impressions": random.randint(1000, 10000),
            "clicks": random.randint(10, 500),
            "platform": platform
        }
        for i in range(3)
    ]

# Tasks for data extraction
@task(retries=3, retry_delay_seconds=30, cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def extract_from_s3(bucket_name: str = "mock-bucket") -> List[Dict[str, Any]]:
    """Extract data from S3 (mock)"""
    logger = get_run_logger()
    logger.info(f"Extracting data from S3 bucket: {bucket_name}")
    time.sleep(2)  # Simulate API call
    
    # Randomly fail sometimes to demonstrate error handling
    if random.random() < 0.1:
        raise Exception("S3 connection error (simulated)")
    
    data = generate_mock_s3_data()
    logger.info(f"Extracted {len(data)} records from S3")
    return data

@task(retries=3, retry_delay_seconds=30, cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def extract_from_mongodb(collection: str = "events") -> List[Dict[str, Any]]:
    """Extract data from MongoDB (mock)"""
    logger = get_run_logger()
    logger.info(f"Extracting data from MongoDB collection: {collection}")
    time.sleep(1.5)  # Simulate database query
    
    data = generate_mock_mongodb_data()
    logger.info(f"Extracted {len(data)} records from MongoDB")
    return data

@task(retries=2, retry_delay_seconds=20, cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def extract_from_app_api() -> List[Dict[str, Any]]:
    """Extract data from React app API (mock)"""
    logger = get_run_logger()
    logger.info("Extracting data from React App API")
    time.sleep(1)  # Simulate API call
    
    data = generate_mock_app_data()
    logger.info(f"Extracted {len(data)} user events from app API")
    return data

@task(retries=2, retry_delay_seconds=60, cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def extract_from_mmp(platform: str) -> List[Dict[str, Any]]:
    """Extract data from marketing platform (mock)"""
    logger = get_run_logger()
    logger.info(f"Extracting data from marketing platform: {platform}")
    time.sleep(random.uniform(1.0, 2.5))  # Different platforms take different times
    
    data = generate_mock_mmp_data(platform)
    logger.info(f"Extracted {len(data)} marketing records from {platform}")
    return data

# Tasks for transformation/processing
@task(retries=1, cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def process_with_hevo(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Simulate Hevo ETL processing"""
    logger = get_run_logger()
    logger.info(f"Processing {len(data)} records through Hevo")
    time.sleep(3)  # Hevo processing takes time
    
    # Add Hevo processing metadata
    processed_data = []
    for record in data:
        processed_record = record.copy()
        processed_record["hevo_processed_at"] = time.time()
        processed_record["hevo_batch_id"] = f"batch_{int(time.time())}"
        processed_data.append(processed_record)
    
    logger.info(f"Hevo processing complete for {len(processed_data)} records")
    return processed_data

@task(retries=2, cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def load_to_snowflake_raw_layer(data: List[Dict[str, Any]], table: str) -> bool:
    """Mock loading data to Snowflake raw layer"""
    logger = get_run_logger()
    logger.info(f"Loading {len(data)} records to Snowflake raw layer table: {table}")
    time.sleep(2)  # Simulate Snowflake insertion
    
    # Validate data before loading
    invalid_records = []
    for i, record in enumerate(data):
        if not record:
            invalid_records.append(i)
    
    if invalid_records:
        logger.warning(f"Found {len(invalid_records)} invalid records: {invalid_records}")
        
    # Simulate occasional Snowflake connection issues
    if random.random() < 0.05:
        raise Exception("Snowflake connection timeout (simulated)")
        
    logger.info(f"Successfully loaded data to Snowflake raw layer table: {table}")
    return True

@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def run_snowflake_stored_proc(proc_name: str) -> Dict[str, Any]:
    """Mock execution of Snowflake stored procedure"""
    logger = get_run_logger()
    logger.info(f"Executing Snowflake stored procedure: {proc_name}")
    time.sleep(random.uniform(3.0, 5.0))  # Stored procs take variable time
    
    result = {
        "procedure": proc_name,
        "rows_processed": random.randint(100, 1000),
        "execution_time": random.uniform(2.5, 4.5),
        "status": "success" if random.random() > 0.1 else "partial_success"
    }
    
    logger.info(f"Stored procedure complete: {proc_name}, processed {result['rows_processed']} rows")
    return result

@task(retries=2, cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=2))
def build_summary_tables(source_table: str, target_table: str, simulate_error: bool = False) -> Dict[str, Any]:
    """Mock building of summary tables/dimensions in Snowflake"""
    logger = get_run_logger()
    logger.info(f"Building summary table {target_table} from {source_table}")
    time.sleep(random.uniform(2.0, 4.0))
    
    # Simulate data issues that would prevent summary table building
    if simulate_error and random.random() < 0.7:  # 70% chance of error when flag is True
        logger.error(f"Error building summary table {target_table}: Data schema validation failed")
        logger.error("Some required fields are missing in the source data")
        raise Exception(f"Failed to build summary table {target_table}: Invalid source data schema (simulated error)")
    
    # Sometimes we should simulate partial data issues
    row_count = random.randint(50, 500)
    warnings = []
    if random.random() < 0.2:
        warnings.append("Some dimension keys have null values")
    
    result = {
        "source": source_table,
        "target": target_table,
        "rows_created": row_count,
        "warnings": warnings
    }
    
    logger.info(f"Summary table {target_table} built with {row_count} rows")
    if warnings:
        logger.warning(f"Warnings during summary table build: {', '.join(warnings)}")
    
    return result

@task
def validate_data_quality(table: str) -> Dict[str, Any]:
    """Perform data quality validation on Snowflake tables"""
    logger = get_run_logger()
    logger.info(f"Running data quality validation on table: {table}")
    time.sleep(1.5)
    
    # Simulate data quality metrics
    metrics = {
        "null_percentage": round(random.uniform(0, 5), 2),
        "duplicate_keys": random.randint(0, 10),
        "out_of_range_values": random.randint(0, 20),
        "failed_constraints": random.randint(0, 3)
    }
    
    validation_passed = all([
        metrics["null_percentage"] < 2.0,
        metrics["duplicate_keys"] < 5,
        metrics["out_of_range_values"] < 10,
        metrics["failed_constraints"] == 0
    ])
    
    if not validation_passed:
        logger.warning(f"Data quality issues detected in {table}: {metrics}")
    else:
        logger.info(f"Data quality validation passed for {table}")
    
    return {
        "table": table,
        "validation_passed": validation_passed,
        "metrics": metrics
    }

@task
def prepare_looker_metadata(tables: List[str]) -> Dict[str, Any]:
    """Prepare metadata for Looker integration"""
    logger = get_run_logger()
    logger.info(f"Preparing Looker metadata for tables: {', '.join(tables)}")
    time.sleep(1)
    
    return {
        "tables_refreshed": tables,
        "timestamp": time.time(),
        "ready_for_analysis": True
    }

# Main flow
@flow(name="KashKick ETL Pipeline", log_prints=True)
def kashkick_pipeline(
    process_s3: bool = True,
    process_mongodb: bool = True,
    process_app: bool = True,
    marketing_platforms: List[str] = ["Facebook", "TikTok", "Google Ads"],
    simulate_errors: bool = False
):
    """Main flow that orchestrates the KashKick data pipeline"""
    logger = get_run_logger()
    logger.info("Starting KashKick data pipeline")
    
    if simulate_errors:
        logger.info("Error simulation is enabled - pipeline will demonstrate failure and recovery with caching")
    
    # Extract data from sources
    all_source_data = []
    
    if process_s3:
        try:
            s3_data = extract_from_s3("kashkick-events")
            all_source_data.append(("s3_events", s3_data))
        except Exception as e:
            logger.error(f"Error extracting S3 data: {e}")
    
    if process_mongodb:
        try:
            mongo_data = extract_from_mongodb("user_activities")
            all_source_data.append(("mongodb_events", mongo_data))
        except Exception as e:
            logger.error(f"Error extracting MongoDB data: {e}")
    
    if process_app:
        try:
            app_data = extract_from_app_api()
            all_source_data.append(("app_events", app_data))
        except Exception as e:
            logger.error(f"Error extracting App data: {e}")
    
    # Process marketing platform data
    for platform in marketing_platforms:
        try:
            mmp_data = extract_from_mmp(platform)
            all_source_data.append((f"{platform.lower()}_ads", mmp_data))
        except Exception as e:
            logger.error(f"Error extracting data from {platform}: {e}")
    
    # Process with Hevo and load to Snowflake raw layer
    snowflake_tables_loaded = []
    for source_name, source_data in all_source_data:
        try:
            if source_data:  # Make sure we have data
                processed_data = process_with_hevo(source_data)
                load_success = load_to_snowflake_raw_layer(processed_data, f"raw_{source_name}")
                if load_success:
                    snowflake_tables_loaded.append(f"raw_{source_name}")
                    logger.info(f"Successfully processed and loaded {source_name} data")
        except Exception as e:
            logger.error(f"Error in Hevo processing or Snowflake loading for {source_name}: {e}")
    
    # Run stored procedures to transform data
    stored_proc_results = []
    procs_to_run = [
        "sp_transform_app_events", 
        "sp_aggregate_marketing_metrics",
        "sp_join_user_activities"
    ]
    
    for proc in procs_to_run:
        try:
            result = run_snowflake_stored_proc(proc)
            stored_proc_results.append(result)
        except Exception as e:
            logger.error(f"Error running stored procedure {proc}: {e}")
    
    # Build summary tables and dimensions
    summary_tables = []
    summary_configs = [
        ("raw_app_events", "dim_users"),
        ("raw_app_events", "fact_user_engagement"),
        ("raw_mongodb_events", "dim_activities"),
        ("combined_marketing", "fact_campaign_performance")
    ]
    
    for source, target in summary_configs:
        try:
            # Pass the simulate_errors flag to the build_summary_tables task
            result = build_summary_tables(source, target, simulate_error=simulate_errors)
            if not result.get("warnings"):
                summary_tables.append(target)
        except Exception as e:
            logger.error(f"Error building summary table {target}: {e}")
    
    # Validate data quality of generated tables
    validation_results = []
    for table in summary_tables:
        try:
            result = validate_data_quality(table)
            validation_results.append(result)
        except Exception as e:
            logger.error(f"Error validating data quality for {table}: {e}")
    
    # Prepare for Looker integration
    try:
        looker_metadata = prepare_looker_metadata(summary_tables)
        logger.info(f"Data pipeline complete, {len(summary_tables)} tables ready for analysis in Looker")
    except Exception as e:
        logger.error(f"Error preparing Looker metadata: {e}")
    
    # Final summary
    failed_steps = sum(1 for r in validation_results if not r.get("validation_passed", False))
    logger.info(f"Pipeline complete with {len(validation_results)} tables validated, {failed_steps} quality issues detected")
    
    return {
        "tables_processed": len(snowflake_tables_loaded),
        "summary_tables_created": len(summary_tables),
        "quality_issues": failed_steps,
        "pipeline_status": "success" if failed_steps == 0 else "completed_with_warnings"
    }

# For local execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KashKick ETL Pipeline Demo")
    parser.add_argument("--simulate-errors", action="store_true", help="Simulate errors to demonstrate failure recovery")
    args = parser.parse_args()
    
    print("Starting KashKick ETL pipeline demo...")
    if args.simulate_errors:
        print("Error simulation enabled - pipeline will demonstrate failure and recovery")
    
    result = kashkick_pipeline(simulate_errors=args.simulate_errors)
    print(f"Pipeline completed with result: {result}")
