import os

from src.core.clients.hivebrite_ import HivebriteClient
from src.sandbox.flows.club_registration.helper import generate_mpv


def get_hb_networks():
    """Fetches network data from hivebrite"""
    client_ = HivebriteClient()
    endpoint = "/api/admin/v1/network"
    status, results = client_.get_(endpoint=endpoint)

    response = None

    if status == "error":
        response = {}
    else:
        response = results

    return response


def get_or_create_hb_user(email: str = None, user_id: int = None, data: dict = None):
    """_summary_

    Args:
        email (str): _description_

    Raises:
        UserNotFoundError: _description_

    Returns:
        UserBasic: _description_
    """
    endpoint = None
    hivebrite_client = HivebriteClient()
    response = None

    if email:
        endpoint = "/api/admin/v1/users/find"
        data = {"field": "email", "value": email.lower()}
        status, results = hivebrite_client.post_(endpoint=endpoint, data=data)
    elif user_id:
        endpoint = f"/api/admin/v1/users/{user_id}"
        status, results = hivebrite_client.get_(endpoint=endpoint)
    elif data:
        endpoint = "/api/admin/v1/users"
        status, results = hivebrite_client.post_(endpoint=endpoint, data=data)

    if status == "success":
        response = results["user"]
    else:
        response = results["error"]

    return response


def get_hb_region_topic_ids(region_name: str):
    """getting region topic ids"""
    endpoint = "/api/admin/v1/topics/categories/"
    hivebrite_client = HivebriteClient()
    status, results = hivebrite_client.get_(endpoint=endpoint)

    categories = []
    # categories = results.get("topic_categories", [])

    return categories


def create_hivebrite_group(data: dict):
    """Create Hivebrite Group"""
    endpoint = "/api/admin/v2/topics"
    hivebrite_client = HivebriteClient()

    values, logo_image_path, cover_image_path = generate_mpv(data, True)

    logo_image = open(logo_image_path, "rb")
    cover_image = open(cover_image_path, "rb")

    files = {"logo": logo_image, "cover_picture": cover_image}

    status, results = hivebrite_client.post_(
        endpoint=endpoint, data=values, files=files
    )

    logo_image.close()
    cover_image.close()

    try:
        os.remove(cover_image_path)
        os.remove(logo_image_path)
    except Exception as e:
        print(f"Error: {e}")

    return status, results


def get_hivebrite_groups(updated_since: str):
    """getting region topic ids"""
    page = 1
    per_page = 30
    hivebrite_client = HivebriteClient()
    all_results = []

    while True:
        endpoint = f"/api/admin/v2/topics?updated_since={updated_since}&page={page}&per_page={per_page}"
        print(endpoint)
        status, results = hivebrite_client.get_(endpoint=endpoint)

        if status != "success" or len(results["groups"]) < per_page:
            break

        all_results.extend(results["groups"])

        page += 1

    return all_results


def create_admin(data: dict):
    """Create Admins"""
    hivebrite_client = HivebriteClient()

    status, results = hivebrite_client.post_(
        endpoint="/api/admin/v3/admins/create", data=data
    )

    return status, results
