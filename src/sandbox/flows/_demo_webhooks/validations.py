expected_fields = {
    "CategoryIds": list,
    "FirstName": str,
    "LastName": str,
    "Email": str,
    "Location": dict,
    "Name": str,
    "ClubType": str,
    "GroupDescription": str,
    "Logo": str,
    "Experts": list,
}


def is_ready_for_group_upload_check(hivebrite_user):
    """
    Validate a hivebrite_user dictionary based on the predefined criteria.
    Args:
        hivebrite_user (dict): A dictionary containing the hivebrite_user data.

    Returns:
        bool: True if the dictionary is valid, False otherwise.
    """
    status = True
    message = None
    if not isinstance(hivebrite_user, dict):
        status = False

    for field, field_type in expected_fields.items():
        if field not in hivebrite_user or not isinstance(
            hivebrite_user[field], field_type
        ):
            status = False
            message = f"{field} not in hivebrite_user variable or the field types dont match for the {field} field"

    return status, message
