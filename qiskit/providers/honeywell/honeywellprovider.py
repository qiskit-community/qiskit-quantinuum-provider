#   Copyright 2019-2020 Honeywell, Intl. (www.honeywell.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Provider for a Honeywell backends."""

import logging
from collections import OrderedDict

from qiskit.providers import BaseProvider

from .api import HoneywellClient
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

    def authenticate(self, token=None):
        """ Updates the API to use the provided token """
        self._api.authenticate(token)

    def backends(self, name=None, filters=None, **kwargs):
        # pylint: disable=arguments-differ
        if not self._api.has_token():
            self._api.authenticate()

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
        ret = OrderedDict()
        machine_list = self._api.list_backends()
        for machine in machine_list:
            backend_cls = HoneywellBackend
            ret[machine] = backend_cls(
                name=machine,
                provider=self,
                api=self._api)

        return ret
