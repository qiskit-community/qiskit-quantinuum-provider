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

# Copyright 2019-2020 Quantinuum, Intl. (www.quantinuum.com)
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

from getpass import getpass

from requests.compat import urljoin

import jwt

import keyring

from ..api.quantinuumclient import _API_URL, _API_VERSION

from ..exceptions import QuantinuumError

DEFAULT_QISKITRC_FILE = Path.home()/'.qiskit'/'qhprc'
SECTION_NAME = 'qiskit-quantinuum-provider'
logger = logging.getLogger(__name__)


class QuantinuumCredentialsError(QuantinuumError):
    """ Base class for errors raised during credential management """
    pass


class Credentials:
    """
    Credentials class to encapsulate the data and operations around interacting
    with our credentialing service.
    """
    def __init__(self,
                 pytket_backend,
                 user_name: str = None,
                 api_url: str = None):
        """
        Credentials Constructor
        """
        # Default empty config
        self.user_name = None
        self.api_url = None
        self.refresh_token = None

        # Load configuration from config file
        self.load_config(DEFAULT_QISKITRC_FILE)

        # Create pytket backend
        self.pytket_backend = pytket_backend

        # Allow overrides if provided
        if user_name is not None:
            self.user_name = user_name
        if api_url is not None:
            self.api_url = api_url

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

        # Load existing tokens into pytket backend
        self.pytket_backend.api_handler._cred_store._id_token = self._get_token('id_token')
        self.pytket_backend.api_handler._cred_store._refresh_token = \
            self._get_token('refresh_token')
        self.pytket_backend.api_handler._cred_store._user_name = self.user_name

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
        if url:
            api_url_validator = \
                re.compile("(https://)?([^/]*)(api.quantinuum.com)(/+v[0-9]+)?/?(.*)")
            m = api_url_validator.match(url)
            if m:
                _, api_prefix, api_base, api_version, api_rest = m.groups()
                if api_rest and api_version is None:
                    valid_url = False
                elif api_prefix is None:
                    valid_url = False
            else:
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

    def _get_credentials(self, pwd_prompt=True):
        """ Method to ask for user's credentials """
        user_name = self.user_name
        if user_name and pwd_prompt:
            pwd = getpass(prompt='Enter your password: ')
        else:
            pwd = None
        return user_name, pwd

    def _authenticate(self):
        """ This method makes requests to refresh or get new id-token via pytket.
        Pytket will request user/password information if required.
        """
        self.pytket_backend.api_handler.login()

        # Grab tokens from pytket and save to keychain
        id_token = self.pytket_backend.api_handler._cred_store._id_token
        refresh_token = self.pytket_backend.api_handler._cred_store.refresh_token
        self._save_tokens(id_token, refresh_token)

        return id_token

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
        id_token = self._get_token('id_token')

        # If is_token is missing or expired call auth
        if id_token is None or self._token_is_expired(id_token):
            id_token = self._authenticate()

        return id_token

    def _load_from_qiskitrc(self, filename):
        """ Attempts to read credentials from qiskitrc file
        The default qiskitrc location is in ``$HOME/.qiskitrc/qhprc``
        """
        config_parser = ConfigParser()
        try:
            config_parser.read(str(filename))
        except ParsingError as ex:
            raise QuantinuumCredentialsError(str(ex))

        for k, v in {'user_name': self.user_name, 'api_url': _API_URL}.items():
            setattr(self, k, config_parser.get(SECTION_NAME, k, fallback=v))

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
            raise QuantinuumCredentialsError(str(ex))

        if not config_parser.has_section(SECTION_NAME):
            config_parser[SECTION_NAME] = {}
        for k, v in {'user_name': self.user_name,
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

    def _token_is_expired(self, id_token):
        """ Checks if id token is valid """
        is_expired = False
        try:
            jwt_options = {'verify_aud': False, 'verify_signature': False}
            expiration_date = jwt.decode(id_token, options=jwt_options, algorithms=["RS256"])['exp']
            if expiration_date < (datetime.datetime.now(datetime.timezone.utc).timestamp()):
                print("Your id token is expired. Refreshing...")
                is_expired = True

        except jwt.ExpiredSignatureError:
            print('Your id token is expired. Refreshing...')
            is_expired = True
        except jwt.InvalidTokenError as ex:
            # catch any other error and prompt login retry
            print(ex)
            print('Error processing your id token. Refreshing...')
            is_expired = True

        return is_expired
