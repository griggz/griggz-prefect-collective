import functools
import json
import os

import requests
from dotenv import load_dotenv

# load .env file
load_dotenv()


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class TokenRefreshError(Exception):
    """Raised when the access token cannot be refreshed."""


class ConcurRequestError(Exception):
    """Raised when the request doesnt return status=200."""


class ConcurResponseError(Exception):
    """Raised when the response was successful but an error occured."""


def authentication_handler(func):
    """Decorator to handle authentication errors and refresh tokens."""

    @functools.wraps(func)
    def wrapper(sap_concur_client, *args, **kwargs):
        try:
            response = func(sap_concur_client, *args, **kwargs)
            if response.status_code in [401, 403]:
                print("Access token expired. Refreshing token...")
                (
                    new_access_token,
                    new_refresh_token,
                ) = sap_concur_client.refresh_access_token()
                if new_access_token:
                    if "headers" in kwargs:
                        kwargs["headers"][
                            "Authorization"
                        ] = f"Bearer {new_access_token}"
                    else:
                        kwargs["headers"] = {
                            "Authorization": f"Bearer {new_access_token}"
                        }

                    return func(sap_concur_client, *args, **kwargs)
                else:
                    raise TokenRefreshError("Failed to refresh the access token.")
            return response
        except requests.exceptions.RequestException as exc:
            print(f"Request failed: {exc}")
            raise AuthenticationError(
                "Authentication failed due to a request exception."
            ) from exc

    return wrapper


class SAPConcurClient:
    def __init__(self):
        self.client_id = os.getenv("CONCUR_CLIENT_ID")
        self.client_secret = os.getenv("CONCUR_CLIENT_SECRET")
        self.uuid = os.getenv("CONCUR_UUID")
        self.request_token = os.getenv("CONCUR_REQUEST_TOKEN")
        self.refresh_token = os.getenv("CONCUR_REFRESH_TOKEN")
        self.access_token = os.getenv("CONCUR_ACCESS_TOKEN")
        self.geolocation = os.getenv("CONCUR_GEOLOCATION")

    def get_access_token(self):
        """This function should only be used once every 6 months, and only after
        receiving a new request_token from here https://www.concursolutions.com/nui/authadmin/companytokens.
        Once you have the new request_token, use this function to fetch a new access_token and
        refresh_token. Replace the variables in your respective .env(s).
        """
        url = f"{self.geolocation}/oauth2/v0/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "username": self.uuid,  # company uuid
            "password": self.request_token,  # request token
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "credtype": "authtoken",
        }
        response = requests.post(url, headers=headers, data=data, timeout=3000)
        if response.status_code == 200:
            response_data = response.json()
            self.access_token = response_data["access_token"]  # expires in 1 hour
            self.refresh_token = response_data.get(
                "refresh_token"
            )  # expires in 6 months
            return self.access_token, self.refresh_token
        else:
            print("Failed to get access token:", response.text)
            return None, None

    def refresh_access_token(self):
        """Use this to refresh the access token every hour. Use the refresh_token,
        which expires every 6 months, to obtain a new access_token"""
        if not self.refresh_token:
            print("No refresh token available.")
            return None

        url = "https://us2.api.concursolutions.com/oauth2/v0/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        response = requests.post(url, headers=headers, data=data, timeout=3000)
        if response.status_code == 200:
            response_data = response.json()
            self.access_token = response_data["access_token"]
            self.refresh_token = response_data.get("refresh_token")
            return self.access_token, self.refresh_token
        else:
            print("Failed to refresh access token:", response.text)
            return None, None

    @authentication_handler
    def make_(
        self, endpoint, method="GET", headers=None, data=None, token=None, **kwargs
    ):
        """Request to endpoints"""
        if not self.access_token and not token:
            print("Access token not available. Please obtain it first.")
            return None
        if self.geolocation in endpoint:
            url = endpoint
        else:
            url = f"{self.geolocation}/{endpoint}"
        print(f"{method} request to {url}")
        if not headers:
            headers = {}
            headers["Authorization"] = f"Bearer {token if token else self.access_token}"

        headers["Accept"] = "application/json"
        response = requests.request(
            method, url, headers=headers, data=data, timeout=2000
        )

        return response

    @staticmethod
    def paginate(api_function):
        """Decorator to paginate API requests."""

        @functools.wraps(api_function)
        def wrapper(self, *args, **kwargs):
            all_data = []
            new_token_ = kwargs.pop("token", None)
            current_endpoint = args[0]

            while current_endpoint:
                response, new_token_ = api_function(
                    self, current_endpoint, token=new_token_
                )
                items = response.get("Items", [])
                all_data.extend(items)  # Add data
                next_page_url = response.get("NextPage", None)

                if next_page_url:
                    current_endpoint = next_page_url
                else:
                    current_endpoint = None  # No more pages

            return all_data, new_token_

        return wrapper

    @paginate
    def request_(self, *args, **kwargs):
        """Request handler for concur client"""
        response = self.make_(*args, **kwargs)
        if response.status_code != 200:
            if response.content:
                content = json.loads(response.content)
                message = (
                    content["Message"]
                    if "Message" in content.keys()
                    else content["Error"]["Message"]
                )

                raise ConcurRequestError(
                    f"The request failed with status code {response.status_code}. Error => {message}"
                )
            else:
                raise ConcurRequestError(
                    f"The request failed with status code {response.status_code}"
                )
        if response.content:
            content = response.content
            res = None
            try:
                res = json.loads(content)
                # Check if there are items in the response
                if "Items" not in res.keys():
                    if len(res) > 0:
                        res = {"Items": [res]}
                    else:
                        print("The response contains no items.")
                elif "Items" in res.keys() and len(res.get("Items", [])) == 0:
                    print("The response contains no items.")

            except json.JSONDecodeError as exc:
                raise ConcurResponseError(
                    f"Failed to parse JSON content: {exc}"
                ) from exc
        else:
            raise ConcurResponseError("The response is empty.")

        new_token_ = kwargs.pop("token", None)
        token = new_token_ if new_token_ else self.access_token

        return res, token
