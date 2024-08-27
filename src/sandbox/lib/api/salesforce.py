from core.clients.salesforce_ import SalesforceClient


def get_opp_accounts():
    sf_client_ = SalesforceClient()

    query = """SELECT Id FROM Opportunity"""

    response = sf_client_.query_(query)

    return response.get("records", {})

