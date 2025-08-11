from src.core.clients.salesforce_ import SalesforceClient


def search_for_club(club_name: str):
    salesforce_client = SalesforceClient()
    club = salesforce_client.query_all_(
        f"SELECT Id, c4g_Group_Id__c, c4g_Email__c, Name FROM c4g_Club_Chapter__c WHERE Name = '{club_name}'"
    )

    return club


def create_chapter(data: dict):
    """Create Chapter"""
    results = None
    salesforce_client = SalesforceClient()

    if "new_group" in data.keys():
        group_ = data["new_group"]
        chapter_ = {
            "Name": group_["name"],
            "c4g_Date_Founded__c": group_["created_at"],
            "c4g_Email__c": data["form_data"]["Email"],
            "UNF_CC_Girl_Up_Club_Type__c": "Community Org",
            "Group_Description__c": group_["description"],
            "c4g_Group_Id__c": group_["id"],
            "HivebriteCreation__c": data["success"],
            "HivebriteCreationContext__c": data["hivebrite_creation_context"],
            "Latitude_Longitude__Latitude__s": data.get("lat_", ""),
            "Latitude_Longitude__Longitude__s": data.get("long_", ""),
            "c4g_Country__c": group_["location"]["country_code"],
            "Country_Name__c": group_["location"]["country"],
            "c4g_Girl_Up_Region__c": data["form_data"]["Region"],
            "Girl_Up_Sub_Region__c": data["form_data"]["SubRegion"],
            "c4g_City__c": group_["location"]["city"],
            "c4g_Postal_Code__c": group_["location"]["postal_code"],
            "c4g_State__c": group_["location"].get("state", ""),
            "RecordTypeId": "0121N0000019C39QAE",
        }

        results = salesforce_client.create_("c4g_Club_Chapter__c", chapter_)

    if "id" in results.keys():
        print(f"Chapter created/exists @ id: {results.get('id')} 🚀")

    return results


def create_contact(data: dict):
    """Create Contact"""
    salesforce_client = SalesforceClient()
    user = data.get("user")

    contact_ = {
        "Email": user.get("email"),
        "FirstName": user.get("firstname"),
        "LastName": user.get("lastname"),
        "Hivebrite_User_ID__c": user.get("id"),
    }
    results = salesforce_client.create_("Contact", contact_)

    if "id" in results.keys():
        print(f"Contact created/exists @ id: {results.get('id')} 🚀")

    return results


def create_constituent(data: dict, chapter: dict, contact: dict):
    """Create Constituent"""
    salesforce_client = SalesforceClient()

    constituent_ = {"Chapter__c": chapter["id"], "Contact__c": contact["id"]}
    results = salesforce_client.create_("Constituent_Role__c", constituent_)

    if "id" in results.keys():
        print(f"Constituent created/exists @ id: {results.get('id')} 🚀")

    return results


def weekly_club_registration_summary(date_range):
    salesforce_client = SalesforceClient()

    query = f"""
        SELECT Id, Name, c4g_Group_Id__c, CreatedDate
        FROM c4g_Club_Chapter__c WHERE c4g_Date_Founded__c <= {date_range[0]}
        AND c4g_Date_Founded__c >= {date_range[1]}
        ORDER BY CreatedDate DESC
        """

    data = salesforce_client.query_all_(query)

    return data
