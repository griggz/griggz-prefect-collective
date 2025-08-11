import pycountry

from .helper import get_globalized_iso, parse_json


def process_name(data):
    # Copy the input data to avoid modifying it directly
    updated_data = data.copy()

    # Check if 'LastName' is empty
    if not updated_data.get("LastName"):
        # Split 'FirstName' by spaces
        name_parts = updated_data.get("FirstName", "").split()

        # If 'FirstName' has more than one word
        if len(name_parts) > 1:
            # Set the last word as 'LastName'
            updated_data["LastName"] = name_parts[-1]
            # Set the remaining part as 'FirstName'
            updated_data["FirstName"] = " ".join(name_parts[:-1])

    return updated_data


def standardize_country_name(country_name):
    try:
        # Try to get the country by exact name
        country = pycountry.countries.get(name=country_name)
        if not country:
            # If exact match is not found, use fuzzy search
            country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.name
    except LookupError:
        # Handle the case where the country name is not found
        return None


# Function to get the ISO country code
def get_country_code(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.alpha_2
    except LookupError:
        # Handle the case where the country name is not found
        return None


class FormResponse:
    def __init__(self, form_response):
        # Check and convert form_response if it's a JSON string

        if isinstance(form_response, str):
            form_response = parse_json(form_response)
        self.answers = form_response["form_response"]["answers"]
        self.cover_image = "https://s3.amazonaws.com/data.unf/Club-Import-Banner.png"
        self.logo_image = "https://s3.amazonaws.com/data.unf/Club-Import-Icon.png"
        self.form_response = form_response["form_response"]
        self.data = None

    def determine_lang(self):
        lang = None
        if self.form_response["form_id"] == "TJKqenKZ":
            lang = "en"
        elif self.form_response["form_id"] == "DmSTGvW5":
            lang = "pt"
        elif self.form_response["form_id"] == "EJH9nF4z":
            lang = "es"

        return lang

    def get_answer_as_interface(self, fieldname):
        answer = self.get_answer_by_field_id(fieldname)
        if answer["type"] == "text":
            return answer["text"]
        if answer["type"] == "email":
            return answer["email"]
        if answer["type"] == "date":
            return answer["date"]
        if answer["type"] == "choices":
            return answer["choices"]["labels"]
        if answer["type"] == "boolean":
            return answer["boolean"]
        if answer["type"] == "number":
            return answer["number"]
        if answer["type"] == "choice":
            return answer["choice"]["label"]
        if answer["type"] == "file_url":
            return ""
        if answer["type"] == "empty":
            return ""

        return None

    def get_answer_by_field_id(self, id_):
        for ans in self.answers:
            if ans["field"]["id"] == id_:
                return ans

        return {"type": "empty"}

    def process_en_response(self):
        """Processes the English response.

        Args:
            form_response (Dict): Description of the form response.

        Returns:
            dict: Processed data based on the English response.
        """

        data = {}

        if self.form_response["form_id"] == "TJKqenKZ":  # English
            country_base_name = self.get_answer_as_interface("eFmCb4TrzalN")
            country_code, country_name = get_globalized_iso(
                country_base_name, "English"
            )
            # Update data
            data["CategoryIds"] = []
            data["FirstName"] = self.get_answer_as_interface("PIz3d3fGM3HZ")
            data["LastName"] = self.get_answer_as_interface("cWnwODUfXWey")
            data["Email"] = self.get_answer_as_interface("yZP7zicvakGa")
            data["Location"] = {
                "Country": country_name,
                "Address": self.get_answer_as_interface("v6GmHDuoeB9Y"),
                "City": self.get_answer_as_interface("urwB9EiXWZPB"),
                "PostalCode": self.get_answer_as_interface("nY5wemUAHuWb"),
                "CountryCode": country_code,
            }
            data["Name"] = self.get_answer_as_interface("igSVYnXjk0DW")
            data["ClubType"] = self.get_answer_as_interface("iH95HN9d4uJu")
            data["GroupDescription"] = self.get_answer_as_interface("sSR1LXZiMvS1")
            data["CoverPicture"] = self.cover_image
            data["Logo"] = self.logo_image
        # Confirms Name Structure
        if data["LastName"] == "" or not data["LastName"]:
            data = process_name(data)

        self.data = data
        return data

    def process_pt_response(self):
        """Processes the Portuguese response.

        Args:
            form_response (Dict): Description of the form response.

        Returns:
            dict: Processed data based on the Portuguese response.
        """

        data = {}

        if self.form_response["form_id"] == "DmSTGvW5":  # Portuguese
            country_base_name = self.get_answer_as_interface("qWkZxKFLcL46")
            country_code, country_name = get_globalized_iso(
                country_base_name, "Portuguese"
            )
            data["CategoryIds"] = []
            data["FirstName"] = self.get_answer_as_interface("I1Oy3nh68r6e")
            data["LastName"] = self.get_answer_as_interface("aR1KrOHkc72m")
            data["Email"] = self.get_answer_as_interface("8phFYuF7AsOK")
            data["Location"] = {
                "Country": country_name,
                "Address": self.get_answer_as_interface("MqzhDbj8IUSL"),
                "City": self.get_answer_as_interface("S0LLjz8UyUIH"),
                "PostalCode": self.get_answer_as_interface("OhnVOe8hmqYP"),
                "CountryCode": country_code,
            }
            data["Name"] = self.get_answer_as_interface("zFuF2HNDrfM6")
            data["ClubType"] = self.get_answer_as_interface("isX6NPiyWNKG")
            data["GroupDescription"] = self.get_answer_as_interface("aAxk8zaJYPRv")
            data["CoverPicture"] = self.cover_image
            data["Logo"] = self.logo_image
        # Confirms Name Structure
        if data["LastName"] == "" or not data["LastName"]:
            data = process_name(data)

        self.data = data
        return data

    def process_es_response(self):
        """_summary_

        Args:
            form_response (Dict): _description_

        Returns:
            _type_: _description_
        """

        data = {}

        if self.form_response["form_id"] == "EJH9nF4z":  # Spanish
            country_base_name = self.get_answer_as_interface("TI3XLZZlZPn9")
            country_code, country_name = get_globalized_iso(
                country_base_name, "Spanish"
            )
            # Update data
            data["CategoryIds"] = []
            data["FirstName"] = self.get_answer_as_interface("vEsZYyxzo5tV")
            data["LastName"] = self.get_answer_as_interface("cWnwODUfXWey")
            data["Email"] = self.get_answer_as_interface("1w55msS1MWE0")
            data["Location"] = {
                "Country": country_name,
                "Address": self.get_answer_as_interface("pZkzlG4P4njo"),
                "City": self.get_answer_as_interface("mMMnfMYOBQ9Z"),
                "PostalCode": self.get_answer_as_interface("ANG2cBoF8CGQ"),
                "CountryCode": country_code,
            }
            data["Name"] = self.get_answer_as_interface("um58ynnNwFux")
            data["ClubType"] = self.get_answer_as_interface("3wvR46MYHpBf")
            data["GroupDescription"] = self.get_answer_as_interface("LRdaM7MVJOHP")
            data["CoverPicture"] = self.cover_image
            data["Logo"] = self.logo_image
        # Confirms Name Structure
        if data["LastName"] == "" or not data["LastName"]:
            data = process_name(data)

        self.data = data
        return data

    def confirm_localization(self):
        location = self.data["Location"]

        location["Country"] = standardize_country_name(location["Country"])

        location["CountryCode"] = get_country_code(location["CountryCode"])

        self.data["Location"] = location

        return self.data
