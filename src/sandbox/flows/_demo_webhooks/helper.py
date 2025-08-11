import csv
import difflib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

import requests

from src.core.decorators import log_err_


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


# get the root directory
root_dir = get_project_root()


class GlobalISO:
    def __init__(self, code, english, spanish, portuguese):
        self.english = english
        self.spanish = spanish
        self.portuguese = portuguese
        self.code = code

    def get_name_for_language(self, language):
        if language == "English":
            return self.english
        if language == "Spanish":
            return self.spanish
        if language == "Portuguese":
            return self.portuguese

        return ""


@log_err_(title="Global Country Data Err", content="Unable to process country data.")
def load_global_country_data() -> List[GlobalISO]:
    """_summary_

    Returns:
        List[GlobalISO]: _description_
    """
    file_path = os.path.join(
        root_dir, "club_registration/constants/global-country-codes.json"
    )

    with open(file_path, "r") as f:
        data = json.load(f)
    return [
        GlobalISO(
            code=item["Alpha-2 code"],
            english=item["English"],
            spanish=item["Spanish"],
            portuguese=item["Portuguese"],
        )
        for item in data
    ]


class UserNotFoundError(Exception):
    """Exception raised when a user is not found"""

    pass


class UserBasic:
    """Define UserBasic class here"""

    pass


@log_err_(
    title="Get Globalized ISO Error",
    content="There was an error when trying get globalized iso data.",
)
def get_globalized_iso(country_name: str, language: str) -> str:
    """Get the ISO code for a country name in a specified language.

    Args:
        country_name (str): The name of the country.
        language (str): The language of the country name.

    Returns:
        str: The ISO code of the country.
    """
    codes = load_global_country_data()

    # Try exact match first
    for code in codes:
        if code.get_name_for_language(language).casefold() == country_name.casefold():
            return code.code, code.get_name_for_language(language)

    # Use difflib to find the best match
    country_names = [code.get_name_for_language(language) for code in codes]
    closest_matches = difflib.get_close_matches(
        country_name, country_names, n=1, cutoff=0.4
    )

    if closest_matches:
        best_match = closest_matches[0]
        for code in codes:
            if code.get_name_for_language(language) == best_match:
                return code.code, code.get_name_for_language(language)

    return None, None


def must_open_(file_path):
    """Open a file, raise an exception if an error occurs."""
    try:
        file = open(file_path, "rb")
        return file
    except Exception as e:
        raise e


def download_file(url, filepath):
    """Download a file from a URL and save it to a local file path."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download file: {url}")

    with open(filepath, "wb") as file:
        file.write(response.content)


def location_remap(group):
    """summary"""

    if group["Location"]["Country"] == "United States of America":
        group["Location"]["Country"] = "United States"

    return group


def get_region_from_country(country: str, code: str) -> str:
    """summary"""
    region = None
    sub_region = None
    regions_by_country_name = parse_regions(
        "club_registration/constants/regions_by_country_name.json"
    )
    regions_by_country_code = parse_regions(
        "club_registration/constants/regions_by_country_code.json"
    )
    try:
        region = regions_by_country_code[code]["region"]
        sub_region = regions_by_country_code[code]["sub_region"]
    except KeyError:
        for rx in regions_by_country_name:
            if code in rx["Country"] or rx["Country"] == country:
                region = rx["Region"]
                sub_region = rx["Sub-Region"]

    return region, sub_region


def parse_regions(file_) -> list:
    """summary"""
    file_path = os.path.join(root_dir, file_)
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def load_source_file(file):
    try:
        csvfile = open(file, "r")
        return csvfile
    except Exception as _e_:
        sys.exit(f"Couldn't open the csv file: {_e_}")


@dataclass
class Locale:
    zip_code: str
    latitude: str
    longitude: str
    town: str
    state: str
    county: str


def load_locations():
    out = []
    file = os.path.join(root_dir, "club_registration/constants/zip_codes.csv")
    _f_ = load_source_file(file)
    csv_reader = csv.reader(_f_)

    for record in csv_reader:
        _l_ = Locale(
            zip_code=record[0],
            latitude=record[1],
            longitude=record[2],
            town=record[3],
            state=record[4],
            county=record[5],
        )
        out.append(_l_)

    return out


def get_state_from_postal(code):
    locales = load_locations()
    for l in locales:
        if l.zip_code == code:
            return l.state
    return ""


def generate_mpv(group, is_new):
    """summary"""

    values = {
        "group[name]": group["Name"],
        "group[description]": group["GroupDescription"],
        "group[location][country]": group["Location"]["Country"],
        "group[location][country_code]": group["Location"]["CountryCode"],
        "group[location][city]": group["Location"]["City"],
        "group[location][address]": group["Location"]["Address"],
        "group[location][postal_code]": group["Location"]["PostalCode"],
        "group[config][home_tab_enabled]": True,
        "group[config][news_tab_enabled]": True,
        "group[config][memberships_tab_enabled]": False,
        "group[config][media_center_tab_enabled]": True,
        "group[config][events_tab_enabled]": True,
        "group[config][followers_tab_enabled]": True,
        "group[config][default_group_activity_frequency]": "none",
        "group[public]": True,
        "group[secret]": True,
        "group[published]": True,
    }

    if group["CategoryIds"]:
        values["group[category_ids][]"] = [int(cxi) for cxi in group["CategoryIds"]]

    if group["Experts"] and group["Experts"][0]["UserId"] > 0:
        values["group[experts][][user_id]"] = [
            int(ex["UserId"]) for ex in group["Experts"]
        ]

    if is_new:
        cover_image_path = "sandbox_cover.png"
        logo_image_path = "sandbox_logo.png"

        download_file(group.get("CoverPicture"), cover_image_path)
        download_file(group.get("Logo"), logo_image_path)

    return values, logo_image_path, cover_image_path


def generate_context_message(data, error_message=None):
    message = None

    name = data.get("name")
    group_id = data.get("id")
    message = (
        f"A new hivebrite group named {name} was created! "
        f"You can access it here https://community.sandbox.org/backoffice/networks/468/topics/{group_id}/edit."
    )

    return message


def parse_json(input_data_):
    """
    Parse a string into a dictionary if it's a valid JSON.

    Args:
    - input_string (str): A string potentially containing JSON data.

    Returns:
    - dict: Parsed dictionary if the input_string is valid JSON.
            None otherwise.
    """
    try:
        return json.loads(input_data_)
    except json.JSONDecodeError:
        return input_data_


def email_club_exists(
    recipients: [], club_name: str, existing_club: str | int, lang: str
):
    from src.core.utils import send_email
    from src.sandbox.flows.club_registration.translations.club_exists_text import (
        en_club_exists,
        es_club_exists,
        pt_club_exists,
    )

    lang_switch = {"en": en_club_exists, "es": es_club_exists, "pt": pt_club_exists}

    rich_text, title = lang_switch.get(lang, "en")(club_name)

    send_email(
        sender="clubs@sandbox.org",
        recipients=recipients,
        subject=title,
        content_type="HTML",
        content=rich_text,
    )


def email_club_created(
    recipients: [], club_name: str, new_club: str | int, user: str, lang: str
):
    from src.core.utils import send_email
    from src.sandbox.flows.club_registration.translations.club_created_text import (
        en_club_created_text,
        es_club_created_text,
        pt_club_created_text,
    )

    lang_switch = {
        "en": en_club_created_text,
        "es": es_club_created_text,
        "pt": pt_club_created_text,
    }

    rich_text, title = lang_switch.get(lang, "en")(
        club_name=club_name, user=user, new_club=new_club
    )

    send_email(
        sender="clubs@sandbox.org",
        recipients=recipients,
        subject=title,
        content_type="HTML",
        content=rich_text,
    )


def email_hivebrite_down(recipients: [], club_name: str, user: str):
    from src.core.utils import send_email

    rich_text = f"""
                <div class="container">
                    <p>Hi there, {user} 👋</p>
                    <p>Thank you so much for taking the time to register a new club!</p>
                    <p>Currently, Hivebrite is experiencing issues with creating clubs. We are actively working with Hivebrite to resolve these issues.</p>
                    <p>Once repaired, your club will be created and you will be notified. In the meantime, please check out the resources below to prepare for club leadership.</p>
                    <ul>
                        <li><strong>Step 1:</strong> So what's first? Explore our online Community where youth leaders connect, share experiences, and utilize our resources to advocate for gender equality and equity. (Hint: Bookmark the Girl Up Community in your web browser for easy access or download our mobile app available in the apple and android app stores.)</li>
                        <li><strong>Step 2:</strong> Did you know that we have thousands of clubs around the world AND we have Coalition and Regional Leaders who are specially trained to support your club in your region? We highly recommend connecting either with your <a href="https://community.sandbox.org/page/coalitions">Coalition</a> or <a href="https://community.sandbox.org/page/regions">Regional Leader</a>! Not only will they be an amazing support system while you get started, they will be able to connect you with other leaders in your area."</li>
                        <li><strong>Step 3:</strong> As a Club Leader, you are shaping the world that you want for girls in generations to come. Now, it's time to get to work. Below is your check-list to help guide you as you become familiar with your role as a club leader:</li>
                        <ul>
                            <li><a href="https://community.sandbox.org/page/get-started-center-community">Explore the Get Started Center</a></li>
                            <li><a href="https://community.sandbox.org/page/issues">Learn about the Issues</a></li>
                            <li><a href="https://community.sandbox.org/topics">Build your Club Page</a></li>
                            <li><a href="https://community.sandbox.org/">Introduce yourself in the Live Feed</a></li>
                            <li><a href="https://community.sandbox.org/events">Check out Girl Up's Events and Opportunities</a></li>
                            <li><a href="https://community.sandbox.org/topics/14447/feed">Organize with your Girl Up Club</a></li>
                        </ul>
                    </ul>
                    <p>Check each of these off your list and you'll be a pro in no time 👏. Remember, within just a few days, you'll be able to access your club page and get started.</p>
                    <p>If you have any questions, just reply to this email!</p>
                    <p>Talk soon!</p>
                    <p>Girl Up Team</p>
                </div>
            """
    title = f"New Club, {club_name} Submitted but Not Created!"

    send_email(
        sender="clubs@sandbox.org",
        recipients=recipients,
        subject=title,
        content_type="HTML",
        content=rich_text,
    )


def format_club_name(name):
    try:
        # Convert the entire name to lowercase
        name = name.lower()

        # Split the name into words
        words = name.split()

        # Ensure "Girl Up" is correctly formatted
        name = name.replace("sandbox", "girl up")

        # Capitalize each word
        formatted_words = [word.capitalize() for word in words]
        # Join the words back into a single string
        formatted_name = " ".join(formatted_words)

        # Add spaces around dashes
        formatted_name = formatted_name.replace("-", " - ")

        # Remove any extra spaces that might have been added
        formatted_name = " ".join(formatted_name.split())

        return formatted_name

    except Exception:
        # Log the error if necessary
        # print(f"Error formatting club name: {e}")
        return name
