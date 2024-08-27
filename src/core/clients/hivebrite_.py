import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def must_open_(_f_):
    """summary"""
    try:
        _r_ = open(_f_, "rb")
        return _r_
    except Exception as _e_:
        raise _e_


class HivebriteClient:
    """_summary_"""

    def __init__(self):
        if os.getenv("ENV") == "DEV":
            self.admin_user = os.getenv("SANDBOX_HIVEBRITE_ADMIN_USER")
            self.admin_pw = os.getenv("SANDBOX_HIVEBRITE_ADMIN_PW")
            self.root = os.getenv("SANDBOX_HIVEBRITE_URL")
            self.auth = self.new_oauth(
                os.getenv("SANDBOX_HIVEBRITE_CLIENT_ID"),
                os.getenv("SANDBOX_HIVEBRITE_CLIENT_SECRET"),
            )
        elif os.getenv("ENV") == "LIVE":
            self.admin_user = os.getenv("HIVEBRITE_ADMIN_USER")
            self.admin_pw = os.getenv("HIVEBRITE_ADMIN_PW")
            self.root = os.getenv("HIVEBRITE_URL")
            self.auth = self.new_oauth(
                os.getenv("HIVEBRITE_CLIENT_ID"), os.getenv("HIVEBRITE_CLIENT_SECRET")
            )

    def make_request(self, request, *args, **kwargs):
        """Makes the request
        Args:
            request (_type_): _description_
        Returns:
            _type_: _description_
        """
        response = None
        try:
            req = request(*args, **kwargs)

            req.raise_for_status()
            if req.status_code in [200, 201]:
                res = json.loads(req.content.decode("utf-8"))
                response = ("success", res)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 404:
                response = ("error", f"{str(exc)}")
            else:
                response = ("error", f"{str(exc)}")
        except Exception as exc:
            response = ("error", f"{str(exc)}")

        return response

    def new_oauth(self, client_id, client_secret):
        """HIVEBRITE TOKEN"""
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "admin",
            "grant_type": "password",
            "admin_email": self.admin_user,
            "password": self.admin_pw,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(
            f"{self.root}/api/oauth/token", data=data, headers=headers, timeout=2000
        )
        response.raise_for_status()

        token_data = response.json()

        return token_data

    def get_(self, endpoint):
        """standard get request"""
        return self.make_request(
            requests.get,
            f"{self.root}{endpoint}",
            headers={"Authorization": f"Bearer {self.auth['access_token']}"},
            timeout=2000,
        )

    def post_(self, endpoint, data=None, files=None):
        """standard get request"""

        return self.make_request(
            requests.post,
            f"{self.root}{endpoint}",
            headers={"Authorization": f"Bearer {self.auth['access_token']}"},
            data=data,
            files=files,
            timeout=2000,
        )
