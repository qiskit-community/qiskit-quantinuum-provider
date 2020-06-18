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
import os
import json
from pathlib import Path

from ..exceptions import HoneywellError

DEFAULT_QISKITRC_FILE = Path.home()/'.qiskit'/'qhprc'
SECTION_NAME = 'qiskit-honeywell-provider'
logger = logging.getLogger(__name__)


class HoneywellCredentialsError(HoneywellError):
    """ Base class for errors raised during credential management """
    pass


class Credentials:
    """ Class implementing all credential handling for id/refresh tokens """
    def __init__(self,
                 token: str = None,
                 proxies: dict = None):
        """
        Credentials Constructor
        """
        # Default empty config
        self.token = None
        self.proxies = None

        # Load configuration from env/config file
        self.load_config(DEFAULT_QISKITRC_FILE)

        # Allow overrides if provided
        if token is not None:
            self.token = token
        if proxies is not None:
            self.proxies = proxies

    def load_from_environ(self):
        """ Attempts to read credentials from environment variable """
        self.token = os.getenv('HON_QIS_API')

    def load_from_qiskitrc(self, filename):
        """ Attempts to read credentials from qiskitrc file
        The default qiskitrc location is in ``$HOME/.qiskitrc/qhprc``
        """
        config_parser = ConfigParser()
        try:
            config_parser.read(filename)
        except ParsingError as ex:
            raise HoneywellCredentialsError(str(ex))

        setattr(self, 'token',
                config_parser.get(SECTION_NAME, 'API_KEY', fallback=self.token))
        setattr(self, 'proxies',
                json.loads(config_parser.get(SECTION_NAME, 'proxies', fallback='{}')))

    def load_config(self, filename):
        """ Load config information from environment or configuration file """
        self.load_from_environ()
        self.load_from_qiskitrc(filename)

    def save_config(self, filename=DEFAULT_QISKITRC_FILE, overwrite=False):
        """ Save configuration to resource file. """
        self.save_qiskitrc(overwrite, filename)

    def save_qiskitrc(self, overwrite=False, filename=DEFAULT_QISKITRC_FILE):
        """ Stores the credentials and proxy information to qiskitrcc file
        The default qiskitrc location is in ``$HOME/.qiskitrc/qhprc``
        """
        config_parser = ConfigParser()
        try:
            config_parser.read(filename)
        except ParsingError as ex:
            raise HoneywellCredentialsError(str(ex))

        if not config_parser.has_section(SECTION_NAME):
            config_parser[SECTION_NAME] = {}
        for k, v in {'API_KEY': self.token, 'proxies': self.proxies}.items():
            if k not in config_parser[SECTION_NAME] or not overwrite:
                if isinstance(v, dict):
                    config_parser[SECTION_NAME].update({k: json.dumps(v)})
                else:
                    config_parser[SECTION_NAME].update({k: v})
        (Path(filename).parent).mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as conf_file:
            config_parser.write(conf_file)

    def remove_creds_from_qiskitrc(self, filename=DEFAULT_QISKITRC_FILE):
        """ Removes the credentials from the configuration file
            The default qiskitrc location is in ``$HOME/.qiskitrc/qhprc``
        """
        config_parser = ConfigParser()
        try:
            config_parser.read(filename)
        except ParsingError as ex:
            raise HoneywellCredentialsError(str(ex))
        if not (config_parser.has_section(SECTION_NAME) and config_parser.get(SECTION_NAME,
                                                                              'API_KEY')):
            return
        config_parser.remove_option(SECTION_NAME, 'API_KEY')
        (Path(filename).parent).mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as conf_file:
            config_parser.write(conf_file)
