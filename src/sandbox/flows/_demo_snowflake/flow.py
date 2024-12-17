from prefect import flow, task
from prefect_snowflake import SnowflakeConnector
import pandas as pd


# @task(name="get_customer_data", retries=2)
# def get_customer_data(block_name: str) -> list:
#     query = "SELECT * FROM customer"
#     with SnowflakeConnector.load(block_name) as connector:
#         connector.execute(query, parameters={"address": "Space"})
#         result = connector.fetch_one(query,parameters={"address": "Space"})
#     return result


# @task(name="get_orders_data")
# def get_orders_data(block_name: str)->list:
#     result = []
#     query = "SELECT * FROM ORDERS LIMIT 3"
#     with SnowflakeConnector.load(block_name) as connector:
#         connector.execute(query)
#         result.append(connector.fetch_one(query))
#     return result


# @task(name="process_customer_orders", log_prints=True)
# def process_customer_orders(customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
#     """Join and process customer and order data"""
#     # Merge customers and orders
#     merged_df = customers_df.merge(
#         orders_df,
#         left_on='C_CUSTKEY',
#         right_on='O_CUSTKEY',
#         how='inner'
#     )

#     # Calculate some basic metrics
#     summary_df = merged_df.groupby('C_CUSTKEY').agg({
#         'C_NAME': 'first',
#         'C_MKTSEGMENT': 'first',
#         'O_ORDERKEY': 'count',
#         'O_TOTALPRICE': 'sum'
#     }).reset_index()

#     summary_df.columns = ['CustomerKey', 'CustomerName', 'MarketSegment',
#                          'TotalOrders', 'TotalSpend']

#     return summary_df


# @flow(name="snowflake_analysis_flow", log_prints=True)
# def snowflake_analysis_flow():
#     """Main flow for Snowflake data analysis"""

#     # Create Snowflake connector with insecure mode enabled
#     #connector = SnowflakeConnector.load("snowflake-connector")


#     # Get data from Snowflake
#     customers_df = get_customer_data("snowflake-connector")
#     orders_df = get_orders_data("snowflake-connector")

#     print(customers_df)
#     print(orders_df)
#     # Process the data
#     #summary_df = process_customer_orders(customers_df, orders_df)

#     #print(f"Processed {len(summary_df)} customer records")
#     #return summary_df


# if __name__ == "__main__":
#     snowflake_analysis_flow()


@task(name="setup_table", log_prints=True)
def setup_table(block_name: str) -> None:
    with SnowflakeConnector.load(block_name) as conn:
        table = conn.execute_many(
            "INSERT INTO customers (name, address) VALUES (%(name)s, %(address)s);",
            seq_of_parameters=[
                {"name": "Marvin", "address": "Highway 42"},
                {"name": "Ford", "address": "Highway 42"},
                {"name": "Unknown", "address": "Highway 42"},
                {"name": "Me", "address": "Highway 42"},
            ],
        )
    print("Table created and data inserted")


@task(name="fetch_data", log_prints=True)
def fetch_data(block_name: str) -> list:
    all_rows = []
    with SnowflakeConnector.load(block_name, validate=False) as conn:
        while True:
            # Repeated fetch* calls using the same operation will
            # skip re-executing and instead return the next set of results
            query_string = 'select * from Customers'
            breakpoint()
            result = conn.fetch_many(query_string, size=2)
            print(result)
            if len(result) == 0:
                break
            all_rows.append(result)
            breakpoint()
    return all_rows


@flow(name="snowflake_flow", log_prints=True)
def snowflake_flow(block_name: str) -> list:
    setup_table(block_name)
    all_rows = fetch_data(block_name)
    return all_rows


if __name__ == "__main__":
    snowflake_flow("snowflake-connector")
