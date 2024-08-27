import functools
import os

from dotenv import load_dotenv
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest

load_dotenv()


class SalesforceAPIError(Exception):
    pass


def extract_id_from_error_message(error_message):
    try:
        # Parsing the message from the error
        message = error_message[0]["message"]

        # Finding the position where the ID starts in the message
        id_start = message.find("id: ") + 4  # 'id: ' has 4 characters

        # The ID seems to follow a specific format, starting with 'a0'
        id_end = message.find(
            "'", id_start
        )  # Assuming ID ends before the next single quote

        # Extracting the ID
        record_id = message[id_start:id_end]
        return record_id
    except (IndexError, KeyError, ValueError):
        # Handling possible errors in case the message format is different
        print("Attempted to extract ID and failed. 🛠")


def handle_salesforce_malformed_request(func):
    """Decorator to handle SalesforceMalformedRequest exceptions."""

    @functools.wraps(func)  # Preserves information about the original function
    def wrapper(*args, **kwargs):
        record = None
        try:
            return func(*args, **kwargs)  # Execute the original function
        except SalesforceMalformedRequest as exc:
            duplicate_result = None
            response_content = exc.content

            try:
                try:
                    duplicate_result = response_content[0]["duplicateResut"]
                except KeyError:
                    try:
                        duplicate_result = response_content[0]["duplicateResult"]
                    except KeyError:
                        print(
                            f"Attempting to handle SalesforceMalformedRequest: {response_content} 🛠"
                        )
                        duplicate_result = {
                            "matchResults": [
                                {
                                    "matchRecords": [
                                        {
                                            "record": {
                                                "Id": extract_id_from_error_message(
                                                    response_content
                                                )
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                match_result = duplicate_result["matchResults"][0]
                record = match_result["matchRecords"][0]["record"]

                print(
                    f"Handled SalesforceMalformedRequest: extracted record ID {record['Id']} 🛠"
                )
            except Exception:
                print(
                    f"Handled SalesforceMalformedRequest: Error: {response_content[0]['message']} 🛠"
                )

            return {k.lower(): v for k, v in dict(record).items()}

    return wrapper


class SalesforceClient:
    """_summary_"""

    def __init__(self, *args, **kwargs):
        """
        Initialize the class with your client and attach all of your endpoints
        """

        self.client_ = Salesforce(
            username=os.getenv("SF_ACCOUNT"),
            password=os.getenv("SF_SECRET"),
            security_token=os.getenv("SF_TOKEN"),
        )

    @handle_salesforce_malformed_request
    def query_(self, *args, **kwargs):
        """Makes Request"""
        entity_client = self.client_

        response = entity_client.query(*args, **kwargs)

        return {k.lower(): v for k, v in dict(response).items()}

    @handle_salesforce_malformed_request
    def query_all_(self, *args, **kwargs):
        """Makes Request"""
        entity_client = self.client_

        response = entity_client.query_all(*args, **kwargs)

        return {k.lower(): v for k, v in dict(response).items()}

    @handle_salesforce_malformed_request
    def create_(self, entity, *args, **kwargs):
        """Makes Request"""
        entity_client = getattr(self.client_, entity)

        response = entity_client.create(*args, **kwargs)

        return {k.lower(): v for k, v in dict(response).items()}

    @handle_salesforce_malformed_request
    def get_(self, entity, *args, **kwargs):
        """Makes Request"""
        entity_client = getattr(self.client_, entity)

        response = entity_client.get(*args, **kwargs)

        return {k.lower(): v for k, v in dict(response).items()}

    @handle_salesforce_malformed_request
    def patch_(self, entity, fields, values, obj_id):
        """Makes Request"""
        entity_client = getattr(self.client_, entity)
        res = None
        try:
            data_ = {}
            for field, value in zip(fields, values):
                data_[field] = value
            # Update
            res = entity_client.update(obj_id, data_)

        except Exception as exc:
            raise SalesforceAPIError(str(exc))

        return res

    def get_entity_client(self, entity):
        """
        Retrieve the client for a specific Salesforce entity (e.g., Opportunity, Account).
        """
        return getattr(self.client_, entity)

    def __getattr__(self, name):
        """
        Dynamically access Salesforce objects as attributes (e.g., sf.Opportunity).
        """
        return self.get_entity_client(name)
