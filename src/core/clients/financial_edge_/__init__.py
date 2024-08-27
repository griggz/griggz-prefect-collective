# coding=utf-8
"""
Sky API SDK
https://developer.sky.blackbaud.com/docs/services/
"""
# API Client
from clients.financial_edge_.entities.access_token import AccessToken
from clients.financial_edge_.entities.accounts_payable import AccountsPayable

# Journal Entry Batch
from clients.financial_edge_.entities.general_ledger import GeneralLedger
from clients.financial_edge_.skyapiclient import SkyAPIClient


class SkyApi(SkyAPIClient):
    def __init__(self, *args, **kwargs):
        """
        Initialize the class with your access_key and subscription_key and attach all of your endpoints
        """
        super(SkyApi, self).__init__(*args, **kwargs)
        self.general_ledger = GeneralLedger(self)
        self.access_token = AccessToken(self)
        self.accounts_payable = AccountsPayable(self)
