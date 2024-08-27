import os

import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError

# load .env file
load_dotenv()


class Strapi:
    """_summary_"""

    def __init__(self):
        self.base_url = os.getenv("DATA_WAREHOUSE_URL")
        self.headers = {
            "Authorization": f"Bearer {os.getenv('DATA_WAREHOUSE_TOKEN')}",
            "Content-Type": "application/json",
        }

    def handle_response_(self, response):
        # Check for a successful request
        if response.status_code >= 200 and response.status_code < 300:
            return "Success", response.json()

        # Check for client errors
        if response.status_code >= 400 and response.status_code < 500:
            return f"Client error: {response.status_code}, {response.reason}", None

        # Check for server errors
        if response.status_code >= 500:
            return f"Server error: {response.status_code}, {response.reason}", None

        # Default case
        return (
            f"Unexpected status code: {response.status_code}, {response.reason}",
            None,
        )

    def post_(self, method, endpoint, data=None):
        """post request

        Args:
            method (_type_): _description_
            endpoint (_type_): _description_
            data (_type_, optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
            http_err: _description_
            err: _description_

        Returns:
            _type_: _description_
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            if method.upper() == "POST":
                res_ = requests.post(
                    url, headers=self.headers, json=data, timeout=10000
                )
                print(res_.content)
                message, data = self.handle_response_(res_)
            else:
                raise ValueError(f"HTTP method {method} not supported.")

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            raise http_err
        except Exception as err:
            print(f"Other error occurred: {err}")
            raise err
        else:
            return message

    def get_(self, method, endpoint):
        """Get request

        Args:
            method (_type_): _description_
            endpoint (_type_): _description_

        Raises:
            ValueError: _description_
            http_err: _description_
            err: _description_

        Returns:
            _type_: _description_
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=2000)
            else:
                raise ValueError(f"HTTP method {method} not supported.")

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            raise http_err
        except Exception as err:
            print(f"Other error occurred: {err}")
            raise err
        else:
            return response.json()  # return python dict
