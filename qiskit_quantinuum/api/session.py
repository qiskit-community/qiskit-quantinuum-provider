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

"""Session customized for Quantinuum access."""

from requests import Session, RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .exceptions import RequestsApiError

STATUS_FORCELIST = (
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
)
CLIENT_APPLICATION = 'qiskit-api-py'


class RetrySession(Session):
    """Session with retry and handling of Quantinuum parameters.

    Custom session for use with Quantinuum, that includes a retry mechanism based
    on urllib3 and handling of specific parameters based on
    ``requests.Session``.
    """

    def __init__(self, base_url, credentials=None,
                 retries=5, backoff_factor=0.5,
                 verify=True, proxies=None, auth=None):
        """RetrySession constructor.

        Args:
            base_url (str): base URL for the session's requests.
            credentials (Credentials): credential class that allows for access token refresh.
            retries (int): number of retries for the requests.
            backoff_factor (float): backoff factor between retry attempts.
            verify (bool): enable SSL verification.
            proxies (dict): proxy URLs mapped by protocol.
            auth (AuthBase): authentication handler.
        """
        super().__init__()

        self.base_url = base_url
        self._credentials = credentials

        self._initialize_retry(retries, backoff_factor)
        self._initialize_session_parameters(verify, proxies or {}, auth)

    def update_auth(self):
        """ Updates the headers with updated authorization, or removes
            the authorization if credentials have been cleared. """
        if self._credentials is not None:
            self.headers.update({'Authorization': self._credentials.access_token})
        else:
            self.headers.pop('Authorization', None)

    @property
    def credentials(self):
        """Return the session access token."""
        self.update_auth()
        return self._credentials

    @credentials.setter
    def credentials(self, value):
        """Set the session access token."""
        self._credentials = value
        self.update_auth()

    def _initialize_retry(self, retries, backoff_factor):
        """Set the Session retry policy.

        Args:
            retries (int): number of retries for the requests.
            backoff_factor (float): backoff factor between retry attempts.
        """
        retry = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=STATUS_FORCELIST,
        )

        retry_adapter = HTTPAdapter(max_retries=retry)
        self.mount('http://', retry_adapter)
        self.mount('https://', retry_adapter)

    def _initialize_session_parameters(self, verify, proxies, auth):
        """Set the Session parameters and attributes.

        Args:
            verify (bool): enable SSL verification.
            proxies (dict): proxy URLs mapped by protocol.
            auth (AuthBase): authentication handler.
        """
        self.headers.update({'X-Qx-Client-Application': CLIENT_APPLICATION})

        self.auth = auth
        self.proxies = proxies or {}
        self.verify = verify

    def prepare_request(self, request):
        # Before making the request use this as an opportunity to check/update authorization field
        self.update_auth()
        return super().prepare_request(request)

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """Constructs a Request, prepending the base url.

        Args:
            method (string): method for the new `Request` object.
            url (string): URL for the new `Request` object.
            kwargs (dict): additional arguments for the request.

        Returns:
            Request: Request object.

        Raises:
            RequestsApiError: if the request failed.
        """
        final_url = self.base_url + url

        try:
            response = super().request(method,
                                       final_url,
                                       proxies=self.proxies['urls'] if self.proxies else {},
                                       **kwargs)
            response.raise_for_status()
        except RequestException as ex:
            # Wrap the requests exceptions into a Quantinuum custom one, for
            # compatibility.
            message = str(ex)
            if self.credentials:
                message = message.replace(self.credentials.access_token, '...')

            raise RequestsApiError(ex, message) from None

        return response
