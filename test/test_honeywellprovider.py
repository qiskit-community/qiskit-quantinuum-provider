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
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Honeywell TestCase for testing Providers."""

from qiskit.test.providers import ProviderTestCase
from qiskit.providers.honeywell import HoneywellProvider

from .decorators import online_test


class HoneywellProviderTestCase(ProviderTestCase):
    """Test case for Honeywell Provider.

    Members:
        provider_cls (BaseProvider): provider to be used in this test case. Its
            instantiation can be further customized by overriding the
            ``_get_provider`` function.
        backend_names (list<str>): names of backends provided by the provider.
    """
    provider_cls = HoneywellProvider
    backend_names = ['HQS-LT-1.0', 'HQS-LT-1.0-APIVAL']

    @online_test
    def setUp(self):
        super().setUp()
        self.provider.load_account()

    @online_test
    def test_backends(self):
        """Test the provider has abackends."""
        super().test_backends()

    @online_test
    def test_get_backend(self):
        """Test getting a backend from the provider."""
        for backend_name in self.backend_names:
            backend = self.provider.get_backend(name=backend_name)
            self.assertEqual(backend.name(), backend_name)
