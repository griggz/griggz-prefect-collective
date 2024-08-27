import os

import requests
from dotenv import load_dotenv

load_dotenv()


class PrefectClient:
    """
    This is a sample of how to call this client_
    data = {
        "form_response": json.dumps(form_response),
        "club_name": club_name,
    }

    return prefect_.create_flow_run(
        os.getenv("PREFECT_GU_CLUB_CREATION_DEPLOYMENT_ID"),
        parameters=data,
        flow_name=club_name,
    )
    """

    def __init__(self, api_version="0.8.4"):
        api_url = os.getenv("PREFECT_API_URL")
        api_key = os.getenv("PREFECT_API_KEY")
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-PREFECT-API-VERSION": api_version,
        }

    def create_flow_run(self, deployment_id, parameters={}, flow_name=""):
        url = f"{self.api_url}/deployments/{deployment_id}/create_flow_run"
        body = {
            "name": flow_name,
            "parameters": parameters,
            # Include any other required fields according to the API specification
        }
        # Add context, state, infrastructure_document_id, tags etc. as necessary
        try:
            response = requests.post(url, headers=self.headers, json=body, timeout=3000)
            response.raise_for_status()
            print("Flow run created successfully!")
            return response.json()

        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Oops: Something Else", err)
        return None
