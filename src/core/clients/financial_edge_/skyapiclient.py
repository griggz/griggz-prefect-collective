# coding=utf-8
"""
Blackbaud SKY Api SDK
Documentation: https://developer.sky.blackbaud.com/docs/services/
"""
from __future__ import unicode_literals

import functools
import logging
import os

import requests

SKY_API_ENDPOINT = os.environ["SKY_API_ENDPOINT"]
SKY_API_OAUTH_ENDPOINT = os.environ["SKY_API_OAUTH_ENDPOINT"]

# Handle library reorganisation Python 2 > Python 3.
try:
    from urllib.parse import urlencode, urljoin
except ImportError:
    from urllib import urlencode

    from urlparse import urljoin


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create a logger object
_logger = logging.getLogger("SkyApiLogger")


def _enabled_or_noop(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        if self.enabled:
            return fn(self, *args, **kwargs)

    return wrapper


class SkyAPIError(Exception):
    pass


class SkyAPIAuthenticationError(Exception):
    pass


class SkyAPITokenError(Exception):
    pass


def authentication_handler(func):
    """Decorator to handle authentication errors and refresh tokens."""

    @functools.wraps(func)
    def wrapper(sky_client, *args, **kwargs):
        try:
            response = func(sky_client, *args, **kwargs)
            if response.status_code in [401, 403]:
                print("Access token expired. Refreshing token...")
                new_access_token = sky_client._refresh_access_token().get(
                    "access_token"
                )
                if new_access_token:
                    if "headers" in kwargs:
                        kwargs["headers"][
                            "Authorization"
                        ] = f"Bearer {new_access_token}"
                    else:
                        kwargs["headers"] = {
                            "Authorization": f"Bearer {new_access_token}"
                        }

                    return func(sky_client, *args, **kwargs)
                else:
                    raise SkyAPITokenError("Failed to refresh the access token.")
            return response
        except requests.exceptions.RequestException as exc:
            print(f"Request failed: {exc}")
            raise SkyAPIAuthenticationError(
                "Authentication failed due to a request exception."
            ) from exc

    return wrapper


class SkyAPIClient(object):
    """
    Sky API class to communicate with the Blackbaud API
    """

    def __init__(
        self,
        subscription_key=None,
        access_token=None,
        request_type=None,
        enabled=True,
        timeout=None,
        request_hooks=None,
        request_headers=None,
    ):
        super(SkyAPIClient, self).__init__()
        self.enabled = enabled
        self.timeout = timeout
        if access_token and request_type == "SKY_API_ENDPOINT":
            self.auth = SkyAPIOAuth(access_token, subscription_key, request_type)
            self.base_url = SKY_API_ENDPOINT

        elif request_type == "SKY_API_OAUTH_ENDPOINT":
            self.auth = SkyAPIOAuth(access_token, subscription_key, request_type)
            self.base_url = SKY_API_OAUTH_ENDPOINT
        else:
            raise Exception("You must provide an OAuth access token")

        self.request_headers = request_headers or requests.utils.default_headers()
        self.request_hooks = request_hooks or requests.hooks.default_hooks()

    @authentication_handler
    def _make_request(self, **kwargs):
        _logger.info("{method} Request: {url}".format(**kwargs))

        if kwargs.get("data"):
            _logger.debug("PAYLOAD: {data}".format(**kwargs))
        elif kwargs.get("json"):
            _logger.debug("PAYLOAD: {json}".format(**kwargs))

        response = requests.request(**kwargs)

        _logger.debug(
            "{method} Response: {status} {text}".format(
                method=kwargs["method"], status=response.status_code, text=response.text
            )
        )

        return response

    @_enabled_or_noop
    def _post(self, url, data=None):
        """
        Handle authenticated POST requests
        :param url: The url for the endpoint including path parameters
        :type url: :py:class:`str`
        :param data: The request body parameters
        :type data: :py:data:`none` or :py:class:`dict`
        :returns: The JSON output from the API or an error message
        """
        url = urljoin(self.base_url, url)

        try:
            r = self._make_request(
                **dict(
                    method="POST",
                    url=url,
                    json=data,
                    auth=self.auth,
                    timeout=self.timeout,
                    hooks=self.request_hooks,
                    headers=self.request_headers,
                )
            )
        except requests.exceptions.RequestException as exc:
            raise exc
        else:
            if r.status_code == 401:
                raise SkyAPITokenError(r.json())
            if r.status_code == 400:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = r.json()
                except ValueError:
                    error_data = {"response": r}
                raise SkyAPIError(error_data)
            if r.status_code >= 403:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = r.json()
                except ValueError:
                    error_data = {"response": r}
            if r.status_code == 204:
                return None
            return r.json()

    @_enabled_or_noop
    def _get(self, url, **queryparams):
        """
        Handle authenticated GET requests
        :param url: The url for the endpoint including path parameters
        :type url: :py:class:`str`
        :param queryparams: The query string parameters
        :returns: The JSON output from sthe API
        """
        url = urljoin(self.base_url, url)
        if len(queryparams):
            url += "?" + urlencode(queryparams)
        try:
            res = self._make_request(
                **dict(
                    method="GET",
                    url=url,
                    auth=self.auth,
                    timeout=self.timeout,
                    hooks=self.request_hooks,
                    headers=self.request_headers,
                )
            )
        except requests.exceptions.RequestException as exc:
            raise exc
        else:
            if res.status_code == 401:
                raise SkyAPITokenError(res.json())
            if res.status_code == 400:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = res.json()
                except ValueError:
                    error_data = {"response": res}
                raise SkyAPIError(error_data)
            if res.status_code >= 403:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = res.json()
                except ValueError:
                    error_data = {"response": res}
                raise SkyAPIError(error_data)
            if res.status_code == 204:
                return None
            return res.json()

    @_enabled_or_noop
    def _delete(self, url):
        """
        Handle authenticated DELETE requests
        :param url: The url for the endpoint including path parameters
        :type url: :py:class:`str`
        :returns: The JSON output from the API
        """
        url = urljoin(self.base_url, url)
        try:
            r = self._make_request(
                **dict(
                    method="DELETE",
                    url=url,
                    auth=self.auth,
                    timeout=self.timeout,
                    hooks=self.request_hooks,
                    headers=self.request_headers,
                )
            )
        except requests.exceptions.RequestException as e:
            raise e
        else:
            if r.status_code >= 400:
                raise SkyAPIError(r.json())
            if r.status_code == 204:
                return
            return r.json()

    @_enabled_or_noop
    def _patch(self, url, data=None):
        """
        Handle authenticated PATCH requests
        :param url: The url for the endpoint including path parameters
        :type url: :py:class:`str`
        :param data: The request body parameters
        :type data: :py:data:`none` or :py:class:`dict`
        :returns: The JSON output from the API
        """
        url = urljoin(self.base_url, url)
        try:
            res = self._make_request(
                **dict(
                    method="PATCH",
                    url=url,
                    json=data,
                    auth=self.auth,
                    timeout=self.timeout,
                    hooks=self.request_hooks,
                    headers=self.request_headers,
                )
            )
        except requests.exceptions.RequestException as exc:
            raise exc
        else:
            if res.status_code == 401:
                raise SkyAPITokenError(res.json())
            if res.status_code == 400:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = res.json()
                except ValueError:
                    error_data = {"response": res}
                raise SkyAPIError(error_data)
            if res.status_code >= 403:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = res.json()
                except ValueError:
                    error_data = {"response": res}
                raise SkyAPIError(error_data)
            if res.status_code == 204:
                return None
            return res.json()

    @_enabled_or_noop
    def _put(self, url, data=None):
        """
        Handle authenticated PUT requests
        :param url: The url for the endpoint including path parameters
        :type url: :py:class:`str`
        :param data: The request body parameters
        :type data: :py:data:`none` or :py:class:`dict`
        :returns: The JSON output from the API
        """
        url = urljoin(self.base_url, url)
        try:
            res = self._make_request(
                **dict(
                    method="PUT",
                    url=url,
                    json=data,
                    auth=self.auth,
                    timeout=self.timeout,
                    hooks=self.request_hooks,
                    headers=self.request_headers,
                )
            )
        except requests.exceptions.RequestException as exc:
            raise exc
        else:
            if res.status_code == 401:
                raise SkyAPITokenError(res.json())
            if res.status_code == 400:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = res.json()
                except ValueError:
                    error_data = {"response": res}
                raise SkyAPIError(error_data)
            if res.status_code >= 403:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = res.json()
                except ValueError:
                    error_data = {"response": res}
                raise SkyAPIError(error_data)
            if res.status_code == 204:
                return None
            return res.json()

    @_enabled_or_noop
    def _get_refresh_token(self, url, data=None):
        """
        Handle authenticated POST requests
        :param url: The url for the endpoint including path parameters
        :type url: :py:class:`str`
        :param data: The request body parameters
        :type data: :py:data:`none` or :py:class:`dict`
        :returns: The JSON output from the API or an error message
        """
        url = urljoin(self.base_url, url)

        try:
            res = self._make_request(
                **dict(
                    method="POST",
                    url=url,
                    data=data,
                    timeout=self.timeout,
                    hooks=self.request_hooks,
                    headers=self.request_headers,
                )
            )
        except requests.exceptions.RequestException as exc:
            raise exc
        else:
            if res.status_code == 401:
                raise SkyAPITokenError(res.json())
            if res.status_code == 400:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = res.json()
                except ValueError:
                    error_data = {"response": res}
                raise SkyAPIError(error_data)
            if res.status_code >= 403:
                # in case of a 500 error, the response might not be a JSON
                try:
                    error_data = res.json()
                except ValueError:
                    error_data = {"response": res}
                raise SkyAPIError(error_data)
            if res.status_code == 204:
                return None
            return res.json()


class SkyAPIOAuth(requests.auth.AuthBase):
    """
    Authentication class for authentication with OAuth2. Acquiring an OAuth2
    for Sky API can be done by following the instructions in the
    documentation found at
    https://developer.blackbaud.com/skyapi/docs/authorization/auth-code-flow
    """

    def __init__(self, access_token, subscription_key, request_type):
        """
        Initialize the OAuth and save the access token
        :param access_token: The access token provided by OAuth authentication
        :type access_token: :py:class:`str`
        :param subscription_key: The Blackbaud API Subscription key for your application
        :type subscription_key: :py:class:`str`
        """
        self._access_token = access_token
        self._subscription_key = subscription_key
        self._request_type = request_type

    def __call__(self, r):
        """
        Authorize with the access token provided in __init__
        """

        if self._request_type == "SKY_API_ENDPOINT":
            r.headers["Bb-Api-Subscription-Key"] = self._subscription_key
            r.headers["Authorization"] = "Bearer " + self._access_token
            return r
        elif self._request_type == "SKY_API_OAUTH_ENDPOINT":
            r.headers["Content-Type"]: "application/x-www-form-urlencoded"
            return r
