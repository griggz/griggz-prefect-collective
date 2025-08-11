"""
Hippocratic AI Demo Runner
=========================

This script demonstrates:
1. Running the healthcare data migration flow
2. Showcasing potential ML pipeline integration
3. Monitoring and observability features
"""

import sys
import time
from pathlib import Path
from flow import healthcare_data_migration_flow
from prefect.logging import get_run_logger
import duckdb
import pandas as pd

def print_banner():
    """Print demo banner"""
    print("=" * 80)
    print("🏥 HIPPOCRATIC AI - PREFECT DEMO")
    print("=" * 80)
    print("📊 Healthcare Data Migration & ML Pipeline Demo")
    print("🔄 Postgres → Redshift Migration (simulated with DuckDB)")
    print("🔒 Security & Compliance Features")
    print("🤖 ML Pipeline Orchestration Potential")
    print("🔄 Auto-cleanup enabled - safe to run multiple times!")
    print("=" * 80)
    print()

def run_migration_demo():
    """Run the main data migration flow"""
    print("🚀 Starting Healthcare Data Migration Demo...")
    print()
    
    start_time = time.time()
    
    try:
        # Run the main flow
        result = healthcare_data_migration_flow()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print()
        print("✅ Migration Completed Successfully!")
        print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        print(f"📈 Data Quality Score: {result['data_quality_score']}%")
        print(f"👥 Patients Migrated: {result['records_migrated']['patients']}")
        print(f"👨‍⚕️ Doctors Identified: {result['records_migrated']['doctors']}")
        print(f"🏥 Medical Events: {result['records_migrated']['events']}")
        print()
        
        return result
        
    except Exception as e:
        print(f"❌ Migration Failed: {str(e)}")
        return None

def demonstrate_data_warehouse_queries(warehouse_path: str):
    """Demonstrate querying the data warehouse for business insights"""
    print("📊 BUSINESS INTELLIGENCE DEMO")
    print("-" * 40)
    
    conn = duckdb.connect(warehouse_path)
    
    # Query 1: Patient Demographics
    print("1. Patient Demographics Summary:")
    demographics = conn.execute("""
        SELECT 
            CASE 
                WHEN age_years < 30 THEN '18-29'
                WHEN age_years < 50 THEN '30-49'
                WHEN age_years < 70 THEN '50-69'
                ELSE '70+'
            END as age_group,
            COUNT(*) as patient_count
        FROM dim_patients
        GROUP BY age_group
        ORDER BY age_group
    """).df()
    print(demographics.to_string(index=False))
    print()
    
    # Query 2: Department Workload
    print("2. Department Workload Analysis:")
    workload = conn.execute("""
        SELECT 
            d.department,
            COUNT(f.event_key) as total_visits,
            AVG(f.billing_amount) as avg_billing
        FROM dim_doctors d
        JOIN fact_medical_events f ON d.doctor_key = f.doctor_key
        GROUP BY d.department
        ORDER BY total_visits DESC
    """).df()
    print(workload.to_string(index=False))
    print()
    
    # Query 3: Revenue Analysis
    print("3. Revenue Analysis:")
    revenue = conn.execute("""
        SELECT 
            payment_status,
            COUNT(*) as count,
            SUM(billing_amount) as total_amount,
            AVG(billing_amount) as avg_amount
        FROM fact_medical_events
        WHERE billing_amount IS NOT NULL
        GROUP BY payment_status
    """).df()
    print(revenue.to_string(index=False))
    print()
    
    conn.close()

def demonstrate_ml_pipeline_potential():
    """Demonstrate potential ML pipeline integration"""
    print("🤖 ML PIPELINE INTEGRATION DEMO")
    print("-" * 40)
    print("🔮 Potential ML Use Cases for Hippocratic AI:")
    print()
    
    ml_use_cases = [
        {
            "name": "🎯 Patient Risk Prediction",
            "description": "Predict patient readmission risk based on historical data",
            "input": "Patient demographics, visit history, diagnosis patterns",
            "output": "Risk score (0-100) and recommended interventions"
        },
        {
            "name": "💰 Revenue Optimization", 
            "description": "Predict payment delays and optimize billing processes",
            "input": "Insurance provider, patient history, billing amounts",
            "output": "Payment probability and suggested follow-up actions"
        },
        {
            "name": "👨‍⚕️ Resource Allocation",
            "description": "Optimize doctor schedules and department capacity",
            "input": "Historical visit patterns, seasonal trends, doctor availability",
            "output": "Optimal staffing recommendations and capacity forecasts"
        },
        {
            "name": "🔍 Anomaly Detection",
            "description": "Detect unusual patterns in medical data for quality assurance",
            "input": "Visit patterns, diagnosis frequencies, billing anomalies",
            "output": "Alerts for unusual patterns requiring investigation"
        }
    ]
    
    for i, use_case in enumerate(ml_use_cases, 1):
        print(f"{i}. {use_case['name']}")
        print(f"   📝 {use_case['description']}")
        print(f"   📥 Input: {use_case['input']}")
        print(f"   📤 Output: {use_case['output']}")
        print()
    
    print("🔧 Prefect would orchestrate:")
    print("   • 📊 Data preparation and feature engineering")
    print("   • 🧠 Model training and validation")
    print("   • 🚀 Model deployment and versioning")
    print("   • 📈 Performance monitoring and retraining")
    print("   • 🔔 Alert systems for model drift")
    print()

def demonstrate_security_compliance():
    """Demonstrate security and compliance features"""
    print("🔒 SECURITY & COMPLIANCE DEMO")
    print("-" * 40)
    
    print("✅ Implemented Security Features:")
    print("   🔐 PII Data Hashing (email, phone)")
    print("   📋 Audit Trail Logging")
    print("   ⚠️  Error Handling & Retries")
    print("   🔍 Data Quality Monitoring")
    print("   📊 Compliance Reporting")
    print()
    
    print("🛡️  Production Security Recommendations:")
    print("   🔑 Implement encryption at rest and in transit")
    print("   🎫 Use role-based access control (RBAC)")
    print("   📜 Maintain detailed audit logs")
    print("   🔄 Implement automated backup and recovery")
    print("   🌍 Ensure HIPAA, GDPR, and international compliance")
    print("   🚨 Set up real-time monitoring and alerting")
    print()

def main():
    """Main demo runner"""
    print_banner()
    
    # Run the migration demo
    result = run_migration_demo()
    
    if result:
        # Demonstrate data warehouse queries
        demonstrate_data_warehouse_queries(result['warehouse_path'])
        
        # Show ML pipeline potential
        demonstrate_ml_pipeline_potential()
        
        # Security and compliance demo
        demonstrate_security_compliance()
        
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("📞 Next Steps for Hippocratic AI:")
        print("   1. Schedule a technical deep-dive session")
        print("   2. Discuss production architecture requirements")
        print("   3. Plan pilot implementation timeline")
        print("   4. Review security and compliance requirements")
        print("=" * 80)
    else:
        print("❌ Demo failed to complete. Please check the logs.")

if __name__ == "__main__":
    main() 