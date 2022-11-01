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

"""Job REST adapter for the Quantinuum Api"""

from .base import RestAdapterBase


class Job(RestAdapterBase):
    """Rest adapter for job related endpoints."""

    URL_MAP = {
        'status': ''
    }

    def __init__(self, session, job_id):
        """Job constructor.

        Args:
            session (Session): session to be used in the adaptor.
            job_id (str): id of the job.
        """
        self.job_id = job_id
        super().__init__(session, '/job/{}'.format(job_id))

    def status(self):
        """Return the status of a job."""
        if isinstance(self.session.proxies, dict) and 'urls' in self.session.proxies:
            print('Using proxy, websockets not supported, falling back to polling')
            url = "{url}?websocket={use_ws}".format(url=self.get_url("status"), use_ws="false")
        else:
            url = "{url}?websocket={use_ws}".format(url=self.get_url("status"), use_ws="true")
        return self.session.get(url).json()
