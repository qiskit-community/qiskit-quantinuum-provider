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

"""Backend REST adapter for the Honeywell Api."""

from .base import RestAdapterBase


class Backend(RestAdapterBase):
    """Rest adapter for backend related endpoints."""

    URL_MAP = {
        'status': ''
    }

    def __init__(self, session, backend_name):
        """Backend constructor.

        Args:
            session (Session): session to be used in the adaptor.
            backend_name (str): name of the backend.
        """
        self.backend_name = backend_name
        super().__init__(session, '/machine/{}'.format(backend_name))

    def status(self):
        """Return backend status."""
        url = self.get_url('status')
        response = self.session.get(url).json()

        # Adjust fields according to the specs (BackendStatus).
        ret = {
            'backend_name': self.backend_name,
            'backend_version': response.get('version', '0.0.0'),
            'status_msg': response.get('state', ''),
            'operational': bool(response.get('state', False))
        }

        # 'pending_jobs' is required, and should be >= 0
        if 'pending_jobs' in response:
            ret['pending_jobs'] = max(response['pending_obs'], 0)
        else:
            ret['pending_jobs'] = 0

        return ret
