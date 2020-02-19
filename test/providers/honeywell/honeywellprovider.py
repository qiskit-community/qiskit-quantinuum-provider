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

"""Honeywell TestCase for testing Providers."""

from .. import ProviderTestCase

from qiskit.providers.honeywell import HoneywellProvider


class HoneywellProviderTestCase(ProviderTestCase):
    """Test case for Honeywell Provider.

    Members:
        provider_cls (BaseProvider): provider to be used in this test case. Its
            instantiation can be further customized by overriding the
            ``_get_provider`` function.
        backend_names (list<str>): names of backends provided by the provider.
    """
    provider_cls = HoneywellProvider
    backend_names = ['ARC1', 'deadhead', 'pikasim', 'pika']

    def test_backends(self):
        """Test the provider has backends."""
        super().test_backends()

    def test_get_backend(self):
        """Test getting a backend from the provider."""
        for backend_name in self.backend_names:
            backend = self.provider.get_backend(name=backend_name)
            self.assertEqual(backend.name(), backend_name)
