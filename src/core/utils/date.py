import pendulum


def format_date_for_salesforce(value: str) -> str:
    if not value.strip():
        return None

    try:
        dt = pendulum.parse(value, strict=False)
        return dt.to_iso8601_string()
    except pendulum.exceptions.ParserError:
        print("An Error occurred trying to format a date for salesforce...")
        return None
