from time import sleep
from prefect import flow, task
from prefect.logging import get_run_logger

def get_dynamic_tags(account_name: str):
    # Logic to determine tags based on the account name
    breakpoint()
    if account_name == "block, inc.":
        return ["block", "inc"]
    else:
        return ["default"]

@flow(tags=get_dynamic_tags)
def analyze_accounts(account_name: str):

    # Get dynamic tags based on the account name

    print(f"Analyzing account: {account_name}")


if __name__ == "__main__":
    analyze_accounts(account_name="block, inc.")