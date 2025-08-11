import os
from datetime import datetime, timedelta

from prefect import Flow, State, flow, task
from prefect.cache_policies import TASK_SOURCE
from prefect.runtime import flow_run

from src.core.clients.google_maps_ import GoogleMapsClient
from src.core.decorators.log_err_ import log_err_
from src.core.utils import scrub_str_, send_email
from src.core.utils.errors import FlowProcessingError
from src.sandbox.flows.club_registration.helper import (
    email_club_created,
    email_club_exists,
    email_hivebrite_down,
    format_club_name,
    generate_context_message,
    get_region_from_country,
    location_remap,
    parse_json,
)
from src.sandbox.flows.club_registration.lib.api import (
    create_admin,
    create_hivebrite_group,
    get_hb_networks,
    get_hb_region_topic_ids,
    get_hivebrite_groups,
    get_or_create_hb_user,
)
from src.sandbox.flows.club_registration.lib.api.salesforce import (
    create_chapter,
    create_constituent,
    create_contact,
    search_for_club,
)
from src.sandbox.flows.club_registration.typeform import FormResponse
from src.sandbox.flows.club_registration.validations import (
    is_ready_for_group_upload_check,
)


def determine_club_name():

    parameters = flow_run.parameters

    form_response = parameters["form_response"]

    if isinstance(form_response, str):
        form_response = parse_json(form_response)

    club_name = "club-creation-flow"

    try:
        form_ = form_response["form_response"]

        langs = {"TJKqenKZ": "en", "EJH9nF4z": "es", "DmSTGvW5": "pt"}

        names = {"en": "igSVYnXjk0DW", "es": "um58ynnNwFux", "pt": "zFuF2HNDrfM6"}

        for item in form_["answers"]:
            id_ = names[langs[form_["form_id"]]]
            if "id" in item["field"] and item["field"]["id"] == id_:
                club_name = scrub_str_(v=item["text"], replace="-", lowercase=True)
                if os.getenv("ENV") == "DEV":
                    club_name = f"TEST-{club_name}"

    except Exception as exc:
        print(exc)
        pass

    return club_name


@task(retries=2, log_prints=True, name="Process and Vet the Typeform Response")
def process_typeform_data_(form_response: dict):
    """Cleans and preps data for upload"""

    response_ = FormResponse(form_response=form_response)

    # TYPEFORM RESPONSE LANGUAGE SWITCH
    lang_response = {
        "en": response_.process_en_response,
        "pt": response_.process_pt_response,
        "es": response_.process_es_response,
    }
    # DETERMINE LANGUAGE FROM FORM RESPONSE
    lang = response_.determine_lang()
    # PROCESS TYPEFORM RESPONSE
    data = lang_response[lang]()

    data["Language"] = lang

    # CONFIRM LOCATION DATA
    location_data_valid = (
        data["Location"]["Country"] and data["Location"]["CountryCode"]
    )
    if not location_data_valid:
        print("Location data is invalid...🚧")
        raise ValueError("Location data is invalid")

    print("Typeform data consumed...🚀")

    return data


@task(log_prints=True, name="Restructure and Define Variables")
def structure_typeform_data_(form_data):
    """_summary_"""
    # Adjust any countries to meet ISO source data
    form_data = location_remap(form_data)
    # REGIONS
    region, sub_region = get_region_from_country(
        country=form_data["Location"]["Country"],
        code=form_data["Location"]["CountryCode"],
    )

    # CATEGORIES
    categories = get_hb_region_topic_ids(region)

    form_data["CategoryIds"] = [x.get("id", 0) for x in categories]

    form_data["Region"] = region

    form_data["SubRegion"] = sub_region

    form_data["Name"] = format_club_name(form_data["Name"])

    print("Typeform data restructured...🚀")

    return form_data


@task(
    log_prints=True,
    name="Check if the club name already exists",
    cache_policy=TASK_SOURCE,
    cache_expiration=timedelta(minutes=30),
    retries=2,
)
def check_if_club_exists(data):
    club_name = data["Name"].lower()
    in_salesforce = False
    existing_group = None

    # Check Salesforce
    print(f"Checking Salesforce to see if {club_name} exists...")
    results = search_for_club(club_name)
    if results.get("records") and results["records"][0]["Name"].lower() == club_name:
        print(
            f"{club_name} already exists in Salesforce as object {results['records'][0]['Id']}👷"
        )
        in_salesforce = True
        group_id = results["records"][0]["c4g_Group_Id__c"]
    else:
        # Check Hivebrite
        print(f"Double checking Hivebrite to see if {club_name} exists...")
        two_days_ago = datetime.now() - timedelta(days=2)
        updated_since = two_days_ago.isoformat() + "Z"
        hivebrite_groups = get_hivebrite_groups(updated_since=updated_since)

        group_id = None
        for group in hivebrite_groups:
            group_name = group.get("name", "NONE")
            if group_name and group_name.lower() == club_name:
                print(
                    f"{club_name} already exists in Hivebrite as group {group['id']}👷"
                )
                group_id = group["id"]
                existing_group = group
                break

    if group_id is not None:
        print(f"Notifying {data['Email']}...🚀")
        email_club_exists(
            recipients=[data["Email"]],
            club_name=data["Name"],
            existing_club=group_id,
            lang=data.get("Language", "en"),
        )
        return True, in_salesforce, existing_group

    print("Club does not exist...🚀")

    return False, in_salesforce, existing_group


@task(retries=2, log_prints=True, name="Retrieve or Create the Hivebrite User")
def retrieve_hivebrite_user(form_data):
    """_summary_"""

    user = None
    try:
        user = get_or_create_hb_user(email=form_data.get("Email"))

        if user:
            print(f"Hivebrite user: {user['email']} found! 🚀")

    except Exception as err:
        print(
            f"Could not find user. Moving to create user: {form_data['Email']}. Artifact Error: {err}."
        )
    if not user or user == "user not found":
        network = get_hb_networks()

        sub_network = (
            next(
                (
                    sub_network
                    for sub_network in network.get("sub_networks", [])
                    if "Admin" not in sub_network.get("title", "")
                ),
                None,
            ).get("id", 468)
            if network
            else 468
        )

        new_user_ = {
            "user[email]": form_data.get("Email").lower(),
            "user[firstname]": form_data.get("FirstName", ""),
            "user[lastname]": form_data.get("LastName", ""),
            "user[sub_network_ids][]": [sub_network],
        }
        try:

            user_ = get_or_create_hb_user(data=new_user_)
            if user_ and isinstance(user_, dict) and "id" in user_.keys():
                user = get_or_create_hb_user(email=form_data.get("Email"))
                if user:
                    print(f"Hivebrite user: {user['email']} created...🚀")

        except Exception as err:
            print(f"Hivebrite user not found...Response Error: {err}")
            log_err_(
                title="could not find or create user",
                content=f"Could not find or create user: {form_data['Email']}",
            )
            return

    if not user or user == "user not found":
        print("Hivebrite user not found...")
        raise ValueError(f"Could not find or create user: {form_data['Email']}")
    else:
        form_data["Experts"] = [{"UserId": user["id"]}]

    return form_data, user


@task(log_prints=True, name="Check if the data is ready for upload")
def is_ready_for_group_upload(form_data):
    """Checks if the group data is ready for upload"""
    is_ready_, message = is_ready_for_group_upload_check(form_data)

    if is_ready_:
        print("Upload Data Checked and Confirmed. Ready to create group...🚀")
    else:
        print("Upload Data Checked and Errors Were Found...🚀")
        print(message)

    return is_ready_


@task(retries=2, log_prints=True, name="Upload Group to Hivebrite")
def upload_to_hivebrite(form_data):
    """Uploads group data to hivebrite"""

    results = None
    status = None

    try:

        status, results = create_hivebrite_group(data=form_data)

        if status == "error" or status == "failed":
            print(f"Response Error: {results}")
            if "500 Server Error" in results:
                email_hivebrite_down(
                    club_name=form_data["Name"],
                    recipients=[form_data["Email"]],
                    user=form_data["FirstName"],
                )
            raise FlowProcessingError(
                f"could not post new group to hivebrite for Club Name: {form_data['Name']}"
            )
        else:
            print(f"New Group: {results['group']['name']} Created in Hivebrite...🚀")

    except Exception as err:
        print(f"Response Error: {err}")
        print(
            f"could not post new group to hivebrite for Club Name: {form_data['Name']} due to error: {err}"
        )
        raise err

    return status, results.get("group", {})


@task(log_prints=True, name="Add Admins to Hivebrite Group")
def add_admins_to_hivebrite(user):
    results = None
    status = None

    if user:
        try:
            admin_name = f"{user['firstname']} {user['lastname']}"
            new_admin = {
                "admin[name]": admin_name,
                "admin[email]": user["email"],
                "admin[user_id]": user["id"],
            }

            status, results = create_admin(data=new_admin)

            if status == "error" or status == "failed":
                print(f"Response Error: {results}")
                print(
                    f"Could not create admin user for {admin_name}, it may already exist...🚧"
                )
            else:
                print(f"New Admin account created for {admin_name}...🚀")

        except Exception as err:
            print(f"Response Error: {err}")
            print(f"could not create new admin user for {admin_name}")
            raise err

    else:
        print(
            "Unable to create and associate admins as there is no user data present...🚧"
        )

    return results


@task(log_prints=True, name="Notify Admins of New Club")
def notify_admins(new_group, user, language):
    """Notify admins of new club creation"""
    print(f"Notifying {user['name']} via email @ {user['email']}...")

    email_club_created(
        club_name=new_group["name"],
        new_club=new_group["id"],
        recipients=[user["email"]],
        user=user["firstname"],
        lang=language,
    )


@task(log_prints=True, name="Prepare data for upload to Salesforce")
def prepare_data_for_salesforce(new_group: dict, form_data: dict, user: dict):
    """Upload the typeform data to strapi table."""
    maps_client_ = GoogleMapsClient()

    hivebrite_creation_context = None
    post_object = {}
    post_object.update({"user": user})

    try:
        postal_code = new_group["location"]["postal_code"]
    except KeyError:
        postal_code = form_data["Location"]["PostalCode"]

    lat_ = None
    long_ = None
    if isinstance(new_group, dict) and "location" in new_group.keys():
        lat_ = new_group["location"]["lat"]
        long_ = new_group["location"]["lng"]
    else:
        lat_, long_ = maps_client_.get_location_from_postal_code(postal_code)

    hivebrite_creation_context = generate_context_message(new_group)
    post_object.update(
        {
            "form_data": form_data,
            "lat_": lat_,
            "long_": long_,
            "success": True,
            "hivebrite_creation_context": hivebrite_creation_context,
            "new_group": new_group,
        }
    )

    return post_object


@task(log_prints=True, name="Upload Data to Salesforce")
def upload_to_salesforce(post_object):
    """Upload data to salesforce"""
    # create chapter club
    contact = create_contact(post_object)

    chapter = create_chapter(post_object)

    constituent = create_constituent(post_object, chapter, contact)
    if "id" in contact.keys() and "id" in chapter.keys() and "id" in constituent.keys():
        print("Data successfully uploaded to salesforce...👷")

    post_object.update(
        {
            "salesforce": {
                "contact": contact,
                "chapter": chapter,
                "constuent": constituent,
            }
        }
    )
    return post_object


@task(log_prints=True, name="Confirm Completion Status")
def determine_success(data):
    """
    Determine if the overall upload process was successfull.

    Args:
        data (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    # salesforce
    salesforce_results = data["salesforce"]
    salesforce_completed = all("id" in obj for obj in salesforce_results.values())
    # hivebrite
    hivebrite_results = data["new_group"]
    hivebrite_user_results = data["user"]
    hivebrite_complete = (
        "id" in hivebrite_results.keys() and "id" in hivebrite_user_results
    )
    if not salesforce_completed and hivebrite_complete:
        print("Group Creation Process Failed 👷")
        raise ValueError

    return data


def failed_notifications(flow: Flow, flow_run: any, state: State):
    """
    Send notification of failure.

    Args:
        flow (Flow): _description_
        flow_run (any): _description_
        state (State): _description_
    """

    club_name = ""
    try:
        parameters = flow_run.parameters

        form_response = parameters["form_response"]

        if isinstance(form_response, str):
            form_response = parse_json(form_response)

        form_ = form_response["form_response"]
        langs = {"TJKqenKZ": "en", "EJH9nF4z": "es", "DmSTGvW5": "pt"}

        names = {"en": "igSVYnXjk0DW", "es": "um58ynnNwFux", "pt": "zFuF2HNDrfM6"}

        for item in form_["answers"]:
            id_ = names[langs[form_["form_id"]]]
            if "id" in item["field"] and item["field"]["id"] == id_:
                club_name = scrub_str_(v=item["text"], replace="-", lowercase=True)
        flow_id = flow_run.id.urn.split(":")[2]
        send_email(
            sender="data@unfoundation.org",
            recipients=["wgrigsby@unfoundation.org"],
            subject="Girl Up Club Creation Flow Error",
            content=f"An error occurred trying to create {club_name}. Flow ID: {flow_id}",
            content_type="Text",
        )

    except TypeError:
        send_email(
            sender="data@unfoundation.org",
            recipients=["wgrigsby@unfoundation.org"],
            subject="Girl Up Club Creation Flow Error",
            content="An error occurred trying to create a club.",
            content_type="Text",
        )


@flow(
    log_prints=True,
    on_failure=[failed_notifications],
    flow_run_name=determine_club_name,
)
def sandbox_club_creation(form_response=None):
    """Recieves typeform data object, cleans and process and uploads to salesforce
    Args:
        form_data (_type_): typeform data object
    """

    flow_name = flow_run.flow_name

    print(f"Flow beginning to create {flow_name}👷")
    if form_response:
        process_response = process_typeform_data_(form_response)
        clean_data = structure_typeform_data_(process_response)
        ready_data, user = retrieve_hivebrite_user(clean_data)
        exists, in_salesforce, existing_group = check_if_club_exists(clean_data)

        if not exists:
            is_ready = is_ready_for_group_upload(ready_data)
            if is_ready:
                status, new_group = upload_to_hivebrite(ready_data)
                if status == "success":
                    add_admins_to_hivebrite(user)
                    notify_admins(new_group, user, ready_data.get("Language", "en"))
                    prep_for_salesforce_ = prepare_data_for_salesforce(
                        new_group, ready_data, user
                    )
                    upload_to_salesforce_ = upload_to_salesforce(prep_for_salesforce_)
                    determine_success_ = determine_success(upload_to_salesforce_)
                    print("Upload Complete 👷")

                    return determine_success_

        elif exists and not in_salesforce:
            print(
                f"{ready_data['Name']} exists in Hivebrite, but not in Salesforce...🚧"
            )
            print(f"Moving to create {ready_data['Name']} in Salesforce...🚀")
            prep_for_salesforce_ = prepare_data_for_salesforce(
                new_group=existing_group, form_data=ready_data, user=user
            )
            upload_to_salesforce_ = upload_to_salesforce(prep_for_salesforce_)
            determine_success_ = determine_success(upload_to_salesforce_)
            print("Upload Complete 👷")

            return determine_success_


if __name__ == "__main__":
    sandbox_club_creation(form_response=None)
