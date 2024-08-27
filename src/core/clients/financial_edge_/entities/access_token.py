import urllib

from clients.financial_edge_.baseapi import BaseApi


class AccessToken(BaseApi):
    def __init__(self, *args, **kwargs):
        super(AccessToken, self).__init__(*args, **kwargs)
        self.endpoint = "token"
        self.type = "refresh_token"

    def get_refresh_token(
        self,
        subscription_key,
        refresh_token,
        redirect_uri,
        application_id,
        application_secret,
        environment_id,
    ):
        self.subscription_key = subscription_key
        self.refresh_token = refresh_token
        self.redirect_uri = redirect_uri
        self.application_id = application_id
        self.application_secret = application_secret
        self.environment_id = environment_id
        self.data = {
            "grant_type": self.type,
            "refresh_token": self.refresh_token,
            "redirect_uri": self.redirect_uri,
            "client_id": self.application_id,
            "client_secret": self.application_secret,
            "environment_id": self.environment_id,
            "preserve_refresh_token": "true",
        }

        return self._sky_client._get_refresh_token(
            url=self._build_path(self.endpoint, self.type),
            data=urllib.parse.urlencode(self.data),
        )
