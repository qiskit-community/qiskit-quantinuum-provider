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

"""Provider for a Honeywell backends."""

import logging
from collections import OrderedDict

from qiskit.providers import BaseProvider
from qiskit.providers.models import BackendConfiguration

from .api import HoneywellClient
from .credentials import discover_credentials, write_creds_to_qiskitrc, remove_creds_from_qiskitrc
from .exceptions import HoneywellCredentialsNotFound
from .honeywellbackend import HoneywellBackend


logger = logging.getLogger(__name__)


class HoneywellProvider(BaseProvider):
    """Provider for Honeywell backends."""

    def __init__(self):
        """Return a new HoneywellProvider."""
        super().__init__()

        # Get a connection to Honeywell.
        self._api = HoneywellClient()

        # Populate the list of remote backends.
        self._backends = None

    def load_account(self):
        """ Obtain stored credentials """
        credentials = discover_credentials()

        if not credentials:
            raise HoneywellCredentialsNotFound

        self._api.authenticate(credentials)

    def save_account(self, token, overwrite=False, filename=None):
        """ Save the credentials onto disk """
        self._api.authenticate(token)
        if filename:
            write_creds_to_qiskitrc(token, overwrite, filename)
        else:
            write_creds_to_qiskitrc(token, overwrite)

    def delete_credentials(self, filename=None):
        """ Delete the credentials from disk """
        if filename:
            remove_creds_from_qiskitrc(filename)
        else:
            remove_creds_from_qiskitrc()

    def backends(self, name=None, **kwargs):
        if not self._api.has_token():
            self.load_account()

        if not self._backends:
            self._backends = self._discover_remote_backends()

        backends = self._backends.values()

        if name:
            backends = [b for b in backends if b.name() == name]

        return list(backends)

    def _discover_remote_backends(self):
        """Return the remote backends available.

        Returns:
            dict[str:HoneywellBackend]: a dict of the remote backend instances,
                keyed by backend name.
        """
        configuration = {
            'backend_name': '',
            'backend_version': '0.0.1',
            'simulator': False,
            'local': False,
            'basis_gates': ['rx', 'ry', 'rz', 'cx', 'h'],
            'memory': False,
            'n_qubits': 0,
            'conditional': True,
            'max_shots': 10000,
            'open_pulse': False,
            'gates': [
                {
                    'name': 'x',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'y',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'z',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'CX',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'cx',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'h',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 's',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'sdg',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 't',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'tdg',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'rx',
                    'parameters': ['theta'],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'ry',
                    'parameters': ['theta'],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'rz',
                    'parameters': ['phi'],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'cz',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'cy',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'ch',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'ccx',
                    'parameters': [],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'crz',
                    'parameters': ['lambda'],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'cu1',
                    'parameters': ['lambda'],
                    'qasm_def': 'TODO'
                },
                {
                    'name': 'cu3',
                    'parameters': ['theta', 'phi', 'lambda'],
                    'qasm_def': 'TODO'
                }
            ],
            'coupling_map': None
        }
        ret = OrderedDict()
        machine_list = self._api.list_backends()
        for machine in machine_list:
            backend_cls = HoneywellBackend
            configuration['backend_name'] = machine['name']
            configuration['n_qubits'] = machine['n_qubits']
            ret[machine['name']] = backend_cls(
                name=machine['name'],
                configuration=BackendConfiguration.from_dict(configuration),
                provider=self,
                api=self._api)

        return ret
