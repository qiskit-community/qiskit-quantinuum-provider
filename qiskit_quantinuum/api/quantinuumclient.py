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

"""Client for accessing Quantinuum."""

from requests.compat import urljoin

from .session import RetrySession
from .rest import Api

_API_URL = 'https://qapi.quantinuum.com'
_API_VERSION = 'v1'


class QuantinuumClient:
    """Client for programmatic access to the Quantinuum API."""

    def __init__(self,
                 credentials,
                 proxies: dict = None):
        """ QuantinuumClient constructor """
        self.credentials = credentials
        self.client_api = self._init_service_client(proxies, self.credentials.api_url)

    @property
    def api_url(self):
        """ Returns the api url that the credential object is targeting

        Returns:
            str: API URL
        """
        return self.credentials.api_url

    def _init_service_client(self,
                             proxies: dict = None,
                             api_url: str = None):
        """Initialize the client used for communicating with the API.

        Returns:
            Api: client for the api server.
        """
        service_url = urljoin(api_url, _API_VERSION)

        # Create the api server client
        client_api = Api(RetrySession(service_url,
                                      credentials=self.credentials,
                                      proxies=proxies))

        return client_api

    def has_token(self):
        """Check if a token has been aquired."""
        return bool(self.client_api.session.credentials.access_token)

    def authenticate(self, credentials=None):
        """Authenticate against the API and aquire a token."""
        service_url = urljoin(self.credentials.api_url, _API_VERSION)
        if credentials:
            self.credentials = credentials
        self.client_api = Api(RetrySession(service_url,
                                           credentials=self.credentials))

    # Backend-related public functions.
    def list_backends(self):
        """Return a list of backends.

        Returns:
            list[dict]: a list of backends.
        """
        return self.client_api.backends()

    def backend_status(self, backend_name):
        """Return the status of a backend.

        Args:
            backend_name (str): the name of the backend.

        Returns:
            dict: backend status.
        """
        return self.client_api.backend(backend_name).status()

    # Jobs-related public functions.

    def job_submit(self, backend_name, qobj_config, qasm):
        """Submit a Qobj to a device.

        Args:
            backend_name (str): the name of the backend.
            qobj_config (dict): the Qobj to be executed, as a dictionary.
            qasm (str): the qasm string of the job to submit

        Returns:
            dict: job status.
        """
        return self.client_api.submit_job(backend_name, qobj_config, qasm)

    def job_status(self, job_id):
        """Return the status of a job.

        Args:
            job_id (str): the id of the job.

        Returns:
            dict: job status.
        """
        return self.client_api.job(job_id).status()
