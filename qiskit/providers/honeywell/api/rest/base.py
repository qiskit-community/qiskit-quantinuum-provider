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

# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""REST clients for accessing Honeywell."""


class RestAdapterBase:
    """Base class for REST adapters."""

    URL_MAP = {}
    """Mapping between the internal name of an endpoint and the actual URL"""

    def __init__(self, session, prefix_url=''):
        """RestAdapterBase constructor.

        Args:
            session (Session): The session instance to use
            prefix_url (str): string to be prefixed to all urls.
        """
        self.session = session
        self.prefix_url = prefix_url

    def get_url(self, identifier):
        """Return the resolved URL for the specified identifier.

        Args:
            identifier (str): internal identifier of the endpoint.

        Returns:
            str: the resolved URL of the endpoint (relative to the session
                base url).
        """
        return '{}{}'.format(self.prefix_url, self.URL_MAP[identifier])
