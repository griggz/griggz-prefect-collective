"""
This is a demo flow that simulates taking a walk and storing the walk details in a SQLite database. 
The flow also triggers a dbt build to update the models based on the latest walk data.

source: https://www.prefect.io/blog/dbt-and-prefect
"""
import os
import sqlite3
from sandbox.flows._demo.flow import take_a_walk
from prefect_dbt.cli.commands import DbtCoreOperation, DbtCliProfile
from prefect import task, flow
from pathlib import Path

profiles_path = Path(os.path.abspath(".dbt/profiles.yml"))

# # Define the DbtCliProfile with the full path to the profiles.yml file
# dbt_profile = DbtCliProfile(
#     name="sqlite_profile",  # Name of your dbt profile
#     target="dev",           # The target environment
#     profiles_dir=profiles_path,  # Full directory path to profiles.yml
#     # project_dir="path_to_your_dbt_project",  # Your dbt project directory
#     overwrite=True,         # Whether to overwrite the profile or not
#     target_configs={        # The required target configurations for SQLite
#         "type": "sqlite",
#         "threads": 1,
#         "database": "dev.db",  # Path to your SQLite database
#         "schema": "main"  
#     }

# )

# Define a function to initialize the SQLite table
def initialize_db():
    # Construct the path to the database directory
    db_dir = Path(".").resolve().parent.parent / "src/core/database"
    # Ensure the directory exists (create it if it doesn't)
    db_dir.mkdir(parents=True, exist_ok=True)
    # Define the path for the SQLite database file
    db_path = db_dir / "my_database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create a table to store walk details
    cursor.execute("""CREATE TABLE IF NOT EXISTS walks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        city TEXT,
                        near TEXT,
                        cafe_name TEXT,
                        park_name TEXT
                      )""")
    conn.commit()
    conn.close()


# Task to insert walk data into the SQLite database
@task
def store_walk_in_db(walk_data: dict):
    # Construct the path to the database directory
    db_dir = Path(".").resolve().parent.parent / "src/core/database"
    # Ensure the directory exists (create it if it doesn't)
    db_dir.mkdir(parents=True, exist_ok=True)
    # Define the path for the SQLite database file
    db_path = db_dir / "my_database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert the walk details into the walks table
    cursor.execute(
        """INSERT INTO walks (city, near, cafe_name, park_name)
                      VALUES (?, ?, ?, ?)""",
        (
            walk_data["city"],
            walk_data["near"],
            walk_data["cafe"]["name"],
            walk_data["park"]["name"],
        ),
    )

    conn.commit()
    conn.close()

@task
def trigger_dbt_flow() -> str:
    result = DbtCoreOperation(
        commands=["dbt build -t dev"],       # dbt commands to run
        profiles_dir=str(profiles_path),  # Programmatically get the path
    ).run()
    return result


# Flow to simulate a walk and store it in the database
@flow
def dbt_injections():
    # Initialize the database
    initialize_db()

    # Simulate taking a walk and store the results
    my_walk = take_a_walk(city="Lyon, France", near="Place de Tapis")
    store_walk_in_db(my_walk)

    # Trigger dbt to build models using the latest walk data
    dbt = trigger_dbt_flow()


if __name__ == "__main__":
    dbt_injections()
