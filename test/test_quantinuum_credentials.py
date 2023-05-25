# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=missing-class-docstring, missing-function-docstring

"""Test credentials."""

from unittest import mock
from pytket.extensions import quantinuum

from qiskit.test import QiskitTestCase

from qiskit_quantinuum.credentials import Credentials
from qiskit_quantinuum.api.quantinuumclient import _API_URL, _API_VERSION


class TestCredentials(QiskitTestCase):

    @mock.patch.object(Credentials, '_login',
                       return_value=None)
    def test_credentials_no_creds(self, login_mock):
        pytket_backend = quantinuum.QuantinuumBackend(device_name='')
        self.assertEqual(None,
                         Credentials(pytket_backend).access_token)
        login_mock.assert_called_once_with()

    def test_credentials_valid_urls(self):
        c = Credentials

        https_valid = ['https://', '']
        api_valid_prefix = ['test', 'test.', 'qa', 'qa.', 'dev', 'dev.', 'q']
        api_valid_version = ['/v1', '/v1234', '/v019', '', '/']
        api_valid_rest = ['/login', '']

        for h_v in https_valid:
            for p_v in api_valid_prefix:
                for v_v in api_valid_version:
                    if 'v' in v_v:
                        for r_v in api_valid_rest:
                            url = h_v+p_v+'api.quantinuum.com'+v_v+r_v
                            api, version = c._canonicalize_url(url)
                            self.assertEqual(api, 'https://'+p_v+'api.quantinuum.com')
                            self.assertEqual(version, v_v.strip('/'))
                    else:
                        url = h_v+p_v+'api.quantinuum.com'+v_v
                        api, version = c._canonicalize_url(url)
                        self.assertEqual(api, 'https://'+p_v+'api.quantinuum.com')
                        self.assertEqual(version, _API_VERSION)

    def test_credentials_invalid_urls(self):
        c = Credentials

        https_valid = ['https://', '']
        api_valid_prefix = ['test', 'test.', 'qa', 'qa.', 'dev', 'dev.', 'q']
        api_valid_version = ['/v1', '/v1234', '/v019', '', '/']
        api_valid_rest = ['/login']

        https_invalid = ['http://']
        api_invalid_version = ['/vA', '/1']

        for h_v in https_valid:
            for p_v in api_valid_prefix:
                for v_v in api_valid_version:
                    # Now invalidate any single component and validate we get the
                    # default api url/version
                    for h_i in https_invalid:
                        url = h_i+p_v+'api.quantinuum.com'+v_v
                        api, version = c._canonicalize_url(url)
                        self.assertEqual(api, _API_URL)
                        self.assertEqual(version, _API_VERSION)

                    for v_i in api_invalid_version:
                        url = h_v+p_v+'api.quantinuum.com'+v_i
                        api, version = c._canonicalize_url(url)
                        self.assertEqual(api, _API_URL)
                        self.assertEqual(version, _API_VERSION)

                    if 'v' not in v_v:
                        # If we don't have a valid version, verify that even
                        # valid (non-empty) rest elements will invalidate URL
                        for r_v in api_valid_rest:
                            url = h_v+p_v+'api.quantinuum.com'+v_v+r_v
                            api, version = c._canonicalize_url(url)
                            self.assertEqual(api, _API_URL)
                            self.assertEqual(version, _API_VERSION)
