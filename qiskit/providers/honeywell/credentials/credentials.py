# This code is part of Qiskit.
#
# (C) Copyright IBM 2017.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# Copyright 2019-2020 Honeywell, Intl. (www.honeywell.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Module for handling credentials """
from configparser import ConfigParser, ParsingError
import logging
import json
import re

from pathlib import Path
import datetime
from http import HTTPStatus

from getpass import getpass

import requests
from requests.compat import urljoin

import jwt

import keyring

from ..api.session import RetrySession

from ..api.honeywellclient import _API_URL, _API_VERSION

from ..exceptions import HoneywellError

DEFAULT_QISKITRC_FILE = Path.home()/'.qiskit'/'qhprc'
SECTION_NAME = 'qiskit-honeywell-provider'
logger = logging.getLogger(__name__)


class HoneywellCredentialsError(HoneywellError):
    """ Base class for errors raised during credential management """
    pass


class Credentials:
    """
    Credentials class to encapsulate the data and operations around interacting
    with our credentialing service.
    """
    def __init__(self,
                 user_name: str = None,
                 proxies: dict = None,
                 api_url: str = None):
        """
        Credentials Constructor
        """
        # Default empty config
        self.user_name = None
        self.proxies = None
        self.api_url = None
        self.refresh_token = None

        # Load configuration from config file
        self.load_config(DEFAULT_QISKITRC_FILE)

        # Allow overrides if provided
        if user_name is not None:
            self.user_name = user_name
        if api_url is not None:
            self.api_url = api_url
        if proxies is not None:
            self.proxies = proxies

        # If we don't have a valid username, request it from the user now.
        # NOTE: we want to avoid any prompt for password until we are properly
        #       authenticating to avoid keeping the password any longer than necessary
        self.user_name, _ = self._get_credentials(pwd_prompt=False)

        self.api_url, self.api_version = Credentials._canonicalize_url(self.api_url)
        if self.user_name:
            if self.api_url == _API_URL:
                self.url = urljoin(_API_URL, self.api_version)
                self.keyring_service = 'HQS-API'+self.user_name
            else:
                self.url = urljoin(self.api_url, self.api_version)
                self.keyring_service = 'HQS-API:'+self.url+":"+self.user_name
        else:
            self.url = urljoin(_API_URL, self.api_version)
            self.keyring_service = 'HQS-API'

    @staticmethod
    def _canonicalize_url(url):
        """ Provided a URL, determine if it is near-enough to expected to
        glean user-intent.  Wherever possible default to known good behavior
        or provide error message with suggestions.
        """
        # Assume url is valid until proven otherwise
        valid_url = True

        # Use regular expression to canonicalize URL bits so we can recombine
        # into validated URL
        api_url_validator = re.compile("(https://)?([^/]*)(api.honeywell.com)(/+v[0-9]+)?/?(.*)")
        m = api_url_validator.match(url)
        if m:
            _, api_prefix, api_base, api_version, api_rest = m.groups()
            if api_rest and api_version is None:
                valid_url = False
            elif api_prefix is None:
                valid_url = False
        else:
            valid_url = False

        if not valid_url:
            api_url = _API_URL
            api_version = _API_VERSION
            print("Error: URL {} didn't conform to expected form.".format(url))
            print("Using default url and version: {} and {}.".format(api_url, api_version))
        else:
            api_url = "https://"+api_prefix+api_base
            if api_version:
                api_version = api_version.strip('/')
            else:
                api_version = _API_VERSION
        return api_url, api_version

    @property
    def access_token(self):
        """Return the session access token."""
        return self._login()

    def _request_tokens(self, body):
        """ Method to send login request to machine api and save tokens. """
        try:
            sess = RetrySession(self.url,
                                proxies=self.proxies)

            # send request to login
            response = sess.post(
                '/login',
                json=body,
            )

            # reset body to delete credentials
            body = {}

            if response.status_code != HTTPStatus.OK:
                return response.status_code, response.json()

            else:
                print("***Successfully logged in***")
                self._save_tokens(response.json()['id-token'], response.json()['refresh-token'])
                return response.status_code, None

        except requests.exceptions.RequestException as exception:
            print(exception)
            return None, None

    def _get_credentials(self, pwd_prompt=True):
        """ Method to ask for user's credentials """
        user_name = self.user_name
        if user_name and pwd_prompt:
            pwd = getpass(prompt='Enter your password: ')
        else:
            pwd = None
        return user_name, pwd

    def _authenticate(self, action=None):
        """ This method makes requests to refresh or get new id-token.
        If a token refresh fails due to token being expired, credentials
        get requested from user.
        """
        # login body
        body = {}

        if action == 'refresh':
            body['refresh-token'] = self._get_token('refresh_token')
        else:
            # ask user for crendentials before making login request
            user_name, pwd = self._get_credentials()
            body['email'] = user_name
            body['password'] = pwd

            # clear credentials
            user_name = None
            pwd = None

        # send login request to API
        status_code, message = self._request_tokens(body)

        if status_code != HTTPStatus.OK:
            # check if we got an error because refresh token has expired
            if status_code in (HTTPStatus.FORBIDDEN, HTTPStatus.BAD_REQUEST):
                print(message.get('error', {}).get('text', 'Request forbidden'))

                # ask user for credentials to login again
                user_name, pwd = self._get_credentials()
                body['email'] = user_name
                body['password'] = pwd

                # send login request to API
                status_code, message = self._request_tokens(body)

        if status_code != HTTPStatus.OK:
            raise RuntimeError('HTTP error while logging in:', status_code)

    def _get_token(self, token_name: str):
        """ Method to retrieve id and refresh tokens from system's keyring service.
        Windows keyring backend has a length limitation on passwords.
        To avoid this, passwords get splitted up into two credentials.
        """

        token = None

        token_first = keyring.get_password(self.keyring_service, '{}_first'.format(token_name))
        token_second = keyring.get_password(self.keyring_service, '{}_second'.format(token_name))

        if token_first is not None and token_second is not None:
            token = token_first + token_second

        return token

    def _save_tokens(self, id_token: str, refresh_token: str):
        """ Method to save id and refresh tokens on system's keyring service.
        Windows keyring backend has a length limitation on passwords.
        To avoid this, passwords get splitted up into two credentials.
        """

        # save two id_token halves
        id_token_first = id_token[:len(id_token)//2]
        id_token_second = id_token[len(id_token)//2:]
        keyring.set_password(self.keyring_service, 'id_token_first', id_token_first)
        keyring.set_password(self.keyring_service, 'id_token_second', id_token_second)

        # save refresh_token halves
        refresh_token_first = refresh_token[:len(refresh_token)//2]
        refresh_token_second = refresh_token[len(refresh_token)//2:]
        keyring.set_password(self.keyring_service, 'refresh_token_first', refresh_token_first)
        keyring.set_password(self.keyring_service, 'refresh_token_second', refresh_token_second)

    def _delete_tokens(self):
        """ Method to delete id and refresh tokens on system's keyring service.
        """
        keyring.delete_password(self.keyring_service, 'id_token_first')
        keyring.delete_password(self.keyring_service, 'id_token_second')
        keyring.delete_password(self.keyring_service, 'refresh_token_first')
        keyring.delete_password(self.keyring_service, 'refresh_token_second')

    def _login(self) -> str:
        """ This methods checks if we have a valid (non-expired) id-token
        and returns it, otherwise it gets a new one with refresh-token.
        If refresh-token doesn't exist, it asks user for credentials.
        """
        # check if id_token exists
        id_token = self._get_token('id_token')
        if id_token is None:
            # authenticate against '/login' endpoint
            self._authenticate()

            # get id_token
            id_token = self._get_token('id_token')

        # check id_token is not expired yet
        expiration_date = jwt.decode(id_token, verify=False)['exp']
        if expiration_date < (datetime.datetime.now(datetime.timezone.utc).timestamp()):
            print("Your id token is expired. Refreshing...")

            # get refresh_token
            self.refresh_token = self._get_token('refresh_token')
            if self.refresh_token is not None:
                self._authenticate('refresh')
            else:
                self._authenticate()

            # get id_token
            id_token = self._get_token('id_token')

        return id_token

    def _load_from_qiskitrc(self, filename):
        """ Attempts to read credentials from qiskitrc file
        The default qiskitrc location is in ``$HOME/.qiskitrc/qhprc``
        """
        config_parser = ConfigParser()
        try:
            config_parser.read(str(filename))
        except ParsingError as ex:
            raise HoneywellCredentialsError(str(ex))

        for k, v in {'user_name': self.user_name, 'api_url': _API_URL}.items():
            setattr(self, k, config_parser.get(SECTION_NAME, k, fallback=v))
        setattr(self, 'proxies',
                json.loads(config_parser.get(SECTION_NAME, 'proxies', fallback='{}')))

    def load_config(self, filename=DEFAULT_QISKITRC_FILE):
        """ Read credential information from file """
        self._load_from_qiskitrc(filename)

    def save_config(self, filename=DEFAULT_QISKITRC_FILE, overwrite=False):
        """ Store credential information in a file """
        self._save_qiskitrc(overwrite, filename)

    def _save_qiskitrc(self, overwrite=False, filename=DEFAULT_QISKITRC_FILE):
        """ Stores the credentials and proxy information to qiskitrcc file
        The default qiskitrc location is in ``$HOME/.qiskitrc/qhprc``
        """
        config_parser = ConfigParser()
        try:
            config_parser.read(str(filename))
        except ParsingError as ex:
            raise HoneywellCredentialsError(str(ex))

        if not config_parser.has_section(SECTION_NAME):
            config_parser[SECTION_NAME] = {}
        for k, v in {'user_name': self.user_name,
                     'proxies': self.proxies,
                     'api_url': str(self.api_url)}.items():
            if k not in config_parser[SECTION_NAME] or not overwrite:
                if isinstance(v, dict):
                    config_parser[SECTION_NAME].update({k: json.dumps(v)})
                elif v is not None:
                    config_parser[SECTION_NAME].update({k: v})
        (Path(filename).parent).mkdir(parents=True, exist_ok=True)
        with open(str(filename), 'w') as conf_file:
            config_parser.write(conf_file)

    def remove_creds(self):
        """ Remove access/refresh tokens from keyring """
        self._delete_tokens()
