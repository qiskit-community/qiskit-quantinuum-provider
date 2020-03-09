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

from ..exceptions import HoneywellError

DEFAULT_QISKITRC_FILE = os.path.join(os.path.expanduser("~"),
                                     '.qiskit', 'qhprc')
SECTION_NAME = 'qiskit-honeywell-provider'
logger = logging.getLogger(__name__)


class HoneywellCredentialsError(HoneywellError):
    """ Base class for errors raised during credential management """
    pass


def discover_credentials(qiskitrc_filename=DEFAULT_QISKITRC_FILE):
    """ Automatically discover credentials from qiskitrc file or environment variables """
    creds = None
    readers = (
        (read_creds_from_environ, {}),
        (read_creds_from_qiskitrc, {'filename': qiskitrc_filename})
    )
    for reader_func, kwargs in readers:
        try:
            creds = reader_func(**kwargs)
            if creds:
                break
        except HoneywellCredentialsError as ex:
            logger.warning('Automatic discovery failed: %s', str(ex))
    return creds


def read_creds_from_environ():
    """ Attempts to read credentials from environment variable """
    return os.getenv('HON_QIS_API')


def read_creds_from_qiskitrc(filename):
    """ Attempts to read credentials from qiskitrc file
    The default qiskitrc location is in ``$HOME/.qiskitrc/qhprc``
    """
    config_parser = ConfigParser()
    try:
        config_parser.read(filename)
    except ParsingError as ex:
        raise HoneywellCredentialsError(str(ex))
    return config_parser.get(SECTION_NAME, 'API_KEY', fallback=None)


def write_creds_to_qiskitrc(token, overwrite=False, filename=DEFAULT_QISKITRC_FILE):
    """ Stores the credentials to qiskitrcc file
    The default qiskitrc location is in ``$HOME/.qiskitrc/qhprc``
    """
    config_parser = ConfigParser()
    try:
        config_parser.read(filename)
    except ParsingError as ex:
        raise HoneywellCredentialsError(str(ex))
    if config_parser.has_section(SECTION_NAME) and \
       config_parser.get(SECTION_NAME, 'API_KEY') and not overwrite:
        return
    config_parser[SECTION_NAME] = {'API_KEY': token}
    with open(filename, 'w') as conf_file:
        config_parser.write(conf_file)


def remove_creds_from_qiskitrc(filename=DEFAULT_QISKITRC_FILE):
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
    with open(filename, 'w') as conf_file:
        config_parser.write(conf_file)
