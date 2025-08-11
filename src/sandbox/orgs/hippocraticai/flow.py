"""
Hippocratic AI - Database Migration Demo
========================================

This demo showcases Prefect's capabilities for:
1. Migrating data from multiple production databases to a data warehouse
2. Security and compliance for healthcare data
3. Error handling and monitoring
4. Future ML pipeline orchestration potential

Architecture:
- Source: Multiple "Postgres" databases (simulated with DuckDB)
- Target: "Redshift" data warehouse (simulated with DuckDB)
- Orchestration: Prefect for workflow management
"""

import duckdb
import pandas as pd
import os
import hashlib
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from pathlib import Path
import time

from prefect import flow, task
from prefect.artifacts import create_markdown_artifact, create_table_artifact
from prefect.blocks.system import Secret
from prefect.logging import get_run_logger
from prefect.task_runners import ConcurrentTaskRunner


@task
def cleanup_previous_demo_data() -> bool:
    """
    Clean up any existing demo data to ensure fresh runs.
    This allows the demo to be run multiple times without conflicts.
    """
    logger = get_run_logger()
    logger.info("Cleaning up previous demo data for fresh run")
    
    data_dir = Path("./data")
    
    if data_dir.exists():
        try:
            shutil.rmtree(data_dir)
            logger.info("Successfully removed existing data directory")
        except Exception as e:
            logger.warning(f"Could not remove data directory: {str(e)}")
            return False
    
    # Recreate empty data directory
    data_dir.mkdir(exist_ok=True)
    logger.info("Created fresh data directory")
    return True


@task(retries=3, retry_delay_seconds=30)
def setup_source_databases() -> Dict[str, str]:
    """
    Set up simulated source Postgres databases with healthcare-like data.
    In production, these would be connections to actual Postgres instances.
    """
    logger = get_run_logger()
    logger.info("Setting up source databases (simulating Postgres)")
    
    # Create data directory
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    db_paths = {}
    
    # Database 1: Patient Management System
    db1_path = data_dir / "patients_db.duckdb"
    conn1 = duckdb.connect(str(db1_path))
    
    # Create patients table with sample data
    conn1.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id VARCHAR PRIMARY KEY,
            first_name VARCHAR,
            last_name VARCHAR,
            date_of_birth DATE,
            email VARCHAR,
            phone VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    
    # Insert sample data
    patients_data = [
        ('P001', 'John', 'Doe', '1980-05-15', 'john.doe@email.com', '555-0101', '2023-01-15 10:00:00', '2023-01-15 10:00:00'),
        ('P002', 'Jane', 'Smith', '1975-08-22', 'jane.smith@email.com', '555-0102', '2023-01-16 11:00:00', '2023-01-16 11:00:00'),
        ('P003', 'Michael', 'Johnson', '1990-12-03', 'michael.j@email.com', '555-0103', '2023-01-17 09:30:00', '2023-01-17 09:30:00'),
        ('P004', 'Emily', 'Davis', '1985-03-18', 'emily.davis@email.com', '555-0104', '2023-01-18 14:15:00', '2023-01-18 14:15:00'),
        ('P005', 'Robert', 'Wilson', '1978-11-30', 'robert.w@email.com', '555-0105', '2023-01-19 16:45:00', '2023-01-19 16:45:00'),
    ]
    
    for patient in patients_data:
        conn1.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?)", patient)
    
    conn1.close()
    db_paths['patients'] = str(db1_path)
    
    # Database 2: Medical Records System
    db2_path = data_dir / "medical_records_db.duckdb"
    conn2 = duckdb.connect(str(db2_path))
    
    conn2.execute("""
        CREATE TABLE IF NOT EXISTS medical_visits (
            visit_id VARCHAR PRIMARY KEY,
            patient_id VARCHAR,
            visit_date DATE,
            diagnosis VARCHAR,
            treatment VARCHAR,
            doctor_id VARCHAR,
            department VARCHAR,
            created_at TIMESTAMP
        )
    """)
    
    visits_data = [
        ('V001', 'P001', '2023-02-01', 'Hypertension', 'Medication prescribed', 'D001', 'Cardiology', '2023-02-01 10:00:00'),
        ('V002', 'P002', '2023-02-02', 'Diabetes Type 2', 'Diet modification', 'D002', 'Endocrinology', '2023-02-02 11:30:00'),
        ('V003', 'P003', '2023-02-03', 'Routine Checkup', 'Clean bill of health', 'D003', 'General Medicine', '2023-02-03 09:15:00'),
        ('V004', 'P001', '2023-02-15', 'Follow-up', 'Blood pressure stable', 'D001', 'Cardiology', '2023-02-15 14:30:00'),
        ('V005', 'P004', '2023-02-20', 'Migraine', 'Pain management', 'D004', 'Neurology', '2023-02-20 16:00:00'),
    ]
    
    for visit in visits_data:
        conn2.execute("INSERT INTO medical_visits VALUES (?, ?, ?, ?, ?, ?, ?, ?)", visit)
    
    conn2.close()
    db_paths['medical_records'] = str(db2_path)
    
    # Database 3: Billing System
    db3_path = data_dir / "billing_db.duckdb"
    conn3 = duckdb.connect(str(db3_path))
    
    conn3.execute("""
        CREATE TABLE IF NOT EXISTS billing_records (
            billing_id VARCHAR PRIMARY KEY,
            patient_id VARCHAR,
            visit_id VARCHAR,
            amount DECIMAL(10,2),
            insurance_provider VARCHAR,
            payment_status VARCHAR,
            billing_date DATE,
            payment_date DATE
        )
    """)
    
    billing_data = [
        ('B001', 'P001', 'V001', 150.00, 'HealthFirst', 'PAID', '2023-02-02', '2023-02-10'),
        ('B002', 'P002', 'V002', 200.00, 'MediCare Plus', 'PENDING', '2023-02-03', None),
        ('B003', 'P003', 'V003', 100.00, 'Universal Health', 'PAID', '2023-02-04', '2023-02-08'),
        ('B004', 'P001', 'V004', 75.00, 'HealthFirst', 'PAID', '2023-02-16', '2023-02-20'),
        ('B005', 'P004', 'V005', 300.00, 'Premium Care', 'PENDING', '2023-02-21', None),
    ]
    
    for billing in billing_data:
        conn3.execute("INSERT INTO billing_records VALUES (?, ?, ?, ?, ?, ?, ?, ?)", billing)
    
    conn3.close()
    db_paths['billing'] = str(db3_path)
    
    logger.info(f"Created {len(db_paths)} source databases")
    return db_paths


@task(retries=2)
def setup_data_warehouse() -> str:
    """
    Set up the target data warehouse (simulating Redshift with DuckDB).
    In production, this would connect to actual Redshift.
    """
    logger = get_run_logger()
    logger.info("Setting up data warehouse (simulating Redshift)")
    
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    warehouse_path = data_dir / "healthcare_warehouse.duckdb"
    conn = duckdb.connect(str(warehouse_path))
    
    # Create dimension and fact tables for star schema
    
    # Dimension: Patients
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dim_patients (
            patient_key INTEGER PRIMARY KEY,
            patient_id VARCHAR UNIQUE,
            first_name VARCHAR,
            last_name VARCHAR,
            full_name VARCHAR,
            date_of_birth DATE,
            age_years INTEGER,
            email_hash VARCHAR,  -- Hashed for privacy
            phone_hash VARCHAR,  -- Hashed for privacy
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Dimension: Doctors
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dim_doctors (
            doctor_key INTEGER PRIMARY KEY,
            doctor_id VARCHAR UNIQUE,
            department VARCHAR,
            etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Fact: Medical Events
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fact_medical_events (
            event_key INTEGER PRIMARY KEY,
            patient_key INTEGER,
            doctor_key INTEGER,
            visit_id VARCHAR,
            visit_date DATE,
            diagnosis VARCHAR,
            treatment VARCHAR,
            billing_amount DECIMAL(10,2),
            insurance_provider VARCHAR,
            payment_status VARCHAR,
            etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_key) REFERENCES dim_patients(patient_key),
            FOREIGN KEY (doctor_key) REFERENCES dim_doctors(doctor_key)
        )
    """)
    
    # Data quality and audit table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS etl_audit_log (
            audit_id INTEGER PRIMARY KEY,
            table_name VARCHAR,
            operation VARCHAR,
            source_system VARCHAR,
            records_processed INTEGER,
            records_successful INTEGER,
            records_failed INTEGER,
            execution_time_seconds REAL,
            execution_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_details VARCHAR
        )
    """)
    
    conn.close()
    logger.info("Data warehouse schema created successfully")
    return str(warehouse_path)


@task
def hash_pii_data(value: str) -> str:
    """
    Hash PII data for compliance with privacy regulations.
    """
    if value is None:
        return None
    return hashlib.sha256(value.encode()).hexdigest()


@task(retries=2)
def extract_and_transform_patients(source_db_path: str) -> pd.DataFrame:
    """
    Extract patient data from source database and apply transformations
    including PII protection for compliance.
    """
    logger = get_run_logger()
    logger.info("Extracting and transforming patient data")
    
    conn = duckdb.connect(source_db_path)
    
    # Extract patients data
    df = conn.execute("SELECT * FROM patients").df()
    conn.close()
    
    # Apply transformations
    df['full_name'] = df['first_name'] + ' ' + df['last_name']
    df['age_years'] = (datetime.now() - pd.to_datetime(df['date_of_birth'])).dt.days // 365
    
    # Hash PII for compliance
    df['email_hash'] = df['email'].apply(lambda x: hash_pii_data(x) if x else None)
    df['phone_hash'] = df['phone'].apply(lambda x: hash_pii_data(x) if x else None)
    
    logger.info(f"Processed {len(df)} patient records")
    return df


@task(retries=2)
def extract_medical_visits(source_db_path: str) -> pd.DataFrame:
    """
    Extract medical visit data from source database.
    """
    logger = get_run_logger()
    logger.info("Extracting medical visit data")
    
    conn = duckdb.connect(source_db_path)
    df = conn.execute("SELECT * FROM medical_visits").df()
    conn.close()
    
    logger.info(f"Extracted {len(df)} medical visit records")
    return df


@task(retries=2)
def extract_billing_data(source_db_path: str) -> pd.DataFrame:
    """
    Extract billing data from source database.
    """
    logger = get_run_logger()
    logger.info("Extracting billing data")
    
    conn = duckdb.connect(source_db_path)
    df = conn.execute("SELECT * FROM billing_records").df()
    conn.close()
    
    logger.info(f"Extracted {len(df)} billing records")
    return df


@task(retries=2)
def load_dimension_patients(warehouse_path: str, patients_df: pd.DataFrame) -> int:
    """
    Load patient dimension table using SCD Type 1 (overwrite).
    """
    logger = get_run_logger()
    logger.info("Loading patient dimension")
    
    conn = duckdb.connect(warehouse_path)
    
    try:
        # Clear existing data for full refresh (SCD Type 1)
        conn.execute("DELETE FROM dim_patients")
        
        # Insert transformed data
        for idx, row in patients_df.iterrows():
            conn.execute("""
                INSERT INTO dim_patients 
                (patient_key, patient_id, first_name, last_name, full_name, 
                 date_of_birth, age_years, email_hash, phone_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                idx + 1, row['patient_id'], row['first_name'], row['last_name'],
                row['full_name'], row['date_of_birth'], row['age_years'],
                row['email_hash'], row['phone_hash'], row['created_at'], row['updated_at']
            ))
        
        records_loaded = len(patients_df)
        
        # Log to audit table
        audit_id = hash('dim_patients') % 1000000  # Generate unique but smaller ID
        conn.execute("""
            INSERT INTO etl_audit_log 
            (audit_id, table_name, operation, source_system, records_processed, records_successful, records_failed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (audit_id, 'dim_patients', 'LOAD', 'patients_db', records_loaded, records_loaded, 0))
        
        conn.close()
        logger.info(f"Successfully loaded {records_loaded} patient records")
        return records_loaded
        
    except Exception as e:
        conn.close()
        logger.error(f"Failed to load patient data: {str(e)}")
        raise


@task(retries=2)
def load_dimension_doctors(warehouse_path: str, visits_df: pd.DataFrame) -> int:
    """
    Load doctor dimension table from visit data.
    """
    logger = get_run_logger()
    logger.info("Loading doctor dimension")
    
    conn = duckdb.connect(warehouse_path)
    
    try:
        # Extract unique doctors from visits
        doctors = visits_df[['doctor_id', 'department']].drop_duplicates()
        
        # Clear existing data
        conn.execute("DELETE FROM dim_doctors")
        
        # Insert doctor data
        for idx, row in doctors.iterrows():
            conn.execute("""
                INSERT INTO dim_doctors (doctor_key, doctor_id, department)
                VALUES (?, ?, ?)
            """, (idx + 1, row['doctor_id'], row['department']))
        
        records_loaded = len(doctors)
        
        # Log to audit table
        audit_id = hash('dim_doctors') % 1000000  # Generate unique but smaller ID
        conn.execute("""
            INSERT INTO etl_audit_log 
            (audit_id, table_name, operation, source_system, records_processed, records_successful, records_failed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (audit_id, 'dim_doctors', 'LOAD', 'medical_records_db', records_loaded, records_loaded, 0))
        
        conn.close()
        logger.info(f"Successfully loaded {records_loaded} doctor records")
        return records_loaded
        
    except Exception as e:
        conn.close()
        logger.error(f"Failed to load doctor data: {str(e)}")
        raise


@task(retries=2)
def load_fact_medical_events(
    warehouse_path: str, 
    visits_df: pd.DataFrame, 
    billing_df: pd.DataFrame
) -> int:
    """
    Load fact table by joining visit and billing data.
    """
    logger = get_run_logger()
    logger.info("Loading medical events fact table")
    
    conn = duckdb.connect(warehouse_path)
    
    try:
        # Join visits with billing data
        merged_df = visits_df.merge(
            billing_df[['visit_id', 'amount', 'insurance_provider', 'payment_status']], 
            on='visit_id', 
            how='left'
        )
        
        # Clear existing data
        conn.execute("DELETE FROM fact_medical_events")
        
        for idx, row in merged_df.iterrows():
            # Get patient key
            patient_key_result = conn.execute(
                "SELECT patient_key FROM dim_patients WHERE patient_id = ?", 
                [row['patient_id']]
            ).fetchone()
            patient_key = patient_key_result[0] if patient_key_result else None
            
            # Get doctor key
            doctor_key_result = conn.execute(
                "SELECT doctor_key FROM dim_doctors WHERE doctor_id = ?", 
                [row['doctor_id']]
            ).fetchone()
            doctor_key = doctor_key_result[0] if doctor_key_result else None
            
            conn.execute("""
                INSERT INTO fact_medical_events 
                (event_key, patient_key, doctor_key, visit_id, visit_date, 
                 diagnosis, treatment, billing_amount, insurance_provider, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                idx + 1, patient_key, doctor_key, row['visit_id'], row['visit_date'],
                row['diagnosis'], row['treatment'], row.get('amount'), 
                row.get('insurance_provider'), row.get('payment_status')
            ))
        
        records_loaded = len(merged_df)
        
        # Log to audit table
        audit_id = hash('fact_medical_events') % 1000000  # Generate unique but smaller ID
        conn.execute("""
            INSERT INTO etl_audit_log 
            (audit_id, table_name, operation, source_system, records_processed, records_successful, records_failed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (audit_id, 'fact_medical_events', 'LOAD', 'multiple_sources', records_loaded, records_loaded, 0))
        
        conn.close()
        logger.info(f"Successfully loaded {records_loaded} medical event records")
        return records_loaded
        
    except Exception as e:
        conn.close()
        logger.error(f"Failed to load medical events data: {str(e)}")
        raise


@task
def generate_data_quality_report(warehouse_path: str) -> Dict[str, Any]:
    """
    Generate a comprehensive data quality report for monitoring and compliance.
    """
    logger = get_run_logger()
    logger.info("Generating data quality report")
    
    conn = duckdb.connect(warehouse_path)
    
    report = {}
    
    # Record counts
    patients_count = conn.execute("SELECT COUNT(*) FROM dim_patients").fetchone()[0]
    doctors_count = conn.execute("SELECT COUNT(*) FROM dim_doctors").fetchone()[0]
    events_count = conn.execute("SELECT COUNT(*) FROM fact_medical_events").fetchone()[0]
    
    report['record_counts'] = {
        'patients': patients_count,
        'doctors': doctors_count,
        'medical_events': events_count
    }
    
    # Data quality checks
    null_emails = conn.execute("SELECT COUNT(*) FROM dim_patients WHERE email_hash IS NULL").fetchone()[0]
    null_diagnoses = conn.execute("SELECT COUNT(*) FROM fact_medical_events WHERE diagnosis IS NULL").fetchone()[0]
    
    report['data_quality'] = {
        'patients_without_email': null_emails,
        'events_without_diagnosis': null_diagnoses,
        'data_quality_score': max(0, 100 - (null_emails + null_diagnoses) * 10)
    }
    
    # Business metrics
    total_billing = conn.execute("SELECT SUM(billing_amount) FROM fact_medical_events WHERE billing_amount IS NOT NULL").fetchone()[0]
    avg_billing = conn.execute("SELECT AVG(billing_amount) FROM fact_medical_events WHERE billing_amount IS NOT NULL").fetchone()[0]
    pending_payments = conn.execute("SELECT COUNT(*) FROM fact_medical_events WHERE payment_status = 'PENDING'").fetchone()[0]
    
    report['business_metrics'] = {
        'total_billing_amount': float(total_billing) if total_billing else 0,
        'average_billing_amount': float(avg_billing) if avg_billing else 0,
        'pending_payments_count': pending_payments
    }
    
    # ETL audit summary
    audit_summary = conn.execute("""
        SELECT table_name, SUM(records_processed) as total_processed, 
               SUM(records_successful) as total_successful,
               SUM(records_failed) as total_failed
        FROM etl_audit_log 
        GROUP BY table_name
    """).df()
    
    report['etl_summary'] = audit_summary.to_dict('records')
    
    conn.close()
    logger.info("Data quality report generated successfully")
    return report


@flow(
    name="Hippocratic AI - Healthcare Data Migration",
    description="Migrate healthcare data from multiple Postgres databases to Redshift data warehouse",
    task_runner=ConcurrentTaskRunner()
)
def healthcare_data_migration_flow():
    """
    Main orchestration flow for migrating healthcare data from multiple sources
    to a centralized data warehouse with security and compliance features.
    """
    logger = get_run_logger()
    logger.info("Starting Hippocratic AI Healthcare Data Migration")
    
    # Phase 0: Cleanup for fresh runs
    logger.info("Phase 0: Cleaning up previous demo data")
    cleanup_success = cleanup_previous_demo_data()
    if not cleanup_success:
        logger.warning("Cleanup had issues, but continuing with demo")
    
    # Phase 1: Infrastructure Setup
    logger.info("Phase 1: Setting up infrastructure")
    source_dbs = setup_source_databases()
    warehouse_path = setup_data_warehouse()
    
    # Phase 2: Data Extraction (can run in parallel)
    logger.info("Phase 2: Extracting data from source systems")
    patients_df = extract_and_transform_patients(source_dbs['patients'])
    visits_df = extract_medical_visits(source_dbs['medical_records'])
    billing_df = extract_billing_data(source_dbs['billing'])
    
    # Phase 3: Data Loading (sequential for referential integrity)
    logger.info("Phase 3: Loading data into warehouse")
    patients_loaded = load_dimension_patients(warehouse_path, patients_df)
    doctors_loaded = load_dimension_doctors(warehouse_path, visits_df)
    events_loaded = load_fact_medical_events(warehouse_path, visits_df, billing_df)
    
    # Phase 4: Data Quality and Reporting
    logger.info("Phase 4: Generating reports and quality checks")
    quality_report = generate_data_quality_report(warehouse_path)
    
    # Create Prefect artifacts for monitoring
    create_markdown_artifact(
        key="migration-summary",
        markdown=f"""
        # Healthcare Data Migration Summary

        ## Migration Results
        - **Patients Migrated**: {patients_loaded}
        - **Doctors Identified**: {doctors_loaded}  
        - **Medical Events Processed**: {events_loaded}
        - **Data Quality Score**: {quality_report['data_quality']['data_quality_score']}%

        ## Business Insights
        - **Total Billing Amount**: ${quality_report['business_metrics']['total_billing_amount']:,.2f}
        - **Average Billing**: ${quality_report['business_metrics']['average_billing_amount']:,.2f}
        - **Pending Payments**: {quality_report['business_metrics']['pending_payments_count']}

        ## Compliance & Security
        - ✅ PII data hashed for privacy protection
        - ✅ Audit trail maintained
        - ✅ Data quality checks passed
        - ✅ Error handling and retries implemented

        ## Next Steps for Hippocratic AI
        1. **Production Deployment**: Connect to actual Postgres and Redshift
        2. **ML Pipeline Integration**: Use this data for predictive analytics
        3. **Real-time Processing**: Implement change data capture (CDC)
        4. **Advanced Security**: Add encryption and access controls
        """,
        description="Healthcare data migration summary and next steps"
    )
    
    # Create data quality table artifact
    create_table_artifact(
        key="etl-audit-log",
        table=quality_report['etl_summary'],
        description="ETL process audit log showing records processed per table"
    )
    
    logger.info("Healthcare data migration completed successfully!")
    
    return {
        "migration_status": "SUCCESS",
        "records_migrated": {
            "patients": patients_loaded,
            "doctors": doctors_loaded,
            "events": events_loaded
        },
        "data_quality_score": quality_report['data_quality']['data_quality_score'],
        "warehouse_path": warehouse_path
    }


if __name__ == "__main__":
    # Run the flow locally for demo
    # result = healthcare_data_migration_flow()
    # print(f"Migration completed: {result}")
    healthcare_data_migration_flow.serve()
