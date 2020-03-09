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

"""Honeywell TestCase for testing backends."""

from qiskit import execute
from qiskit import QuantumCircuit
from qiskit.providers.jobstatus import JobStatus

from qiskit.providers.honeywell import HoneywellProvider
from qiskit.providers.honeywell.api import HoneywellClient
from qiskit.providers.models import BackendStatus
from qiskit.providers.honeywell import HoneywellJob

from qiskit.test import QiskitTestCase
from qiskit.providers.honeywell import HoneywellBackend

from .decorators import online_test


@online_test
class HoneywellBackendTestCase(QiskitTestCase):
    """Test case for Honeywell backend.

    Members:
        proivder_cls (BaseProvider): provider to be used in this test case.
        api_cls (HoneywellClient): api to be used in this test case
        backend_cls (BaseBackend): backend to be used in this test case. Its
            instantiation can be further customized by overriding the
            ``_get_backend`` function.
        backend_name (str): name of backend to be used in tests.
    """
    provider_cls = HoneywellProvider
    api_cls = HoneywellClient

    backend_cls = HoneywellBackend
    backend_name = 'deadhead'

    def setUp(self):
        provider = self.provider_cls()
        self.backend = provider.get_backend(self.backend_name)
        self.circuit = QuantumCircuit(2)
        self.circuit.h(0)
        self.circuit.cx(0, 1)
        self.circuit.measure_all()

    def test_configuration(self):
        """Test backend.configuration()."""
        pass

    def test_properties(self):
        """Test backend.properties()."""
        pass

    def test_provider(self):
        """Test backend.provider()."""
        provider = self.backend.provider()
        self.assertEqual(provider, self.provider_cls())

    def test_status(self):
        """Test backend.status()."""
        status = self.backend.status()
        self.assertIsInstance(status, BackendStatus)

    def test_name(self):
        """Test backend.name()."""
        name = self.backend.name()
        self.assertEqual(name, self.backend_name)

    def _submit_job(self):
        """Helper method to submit job and return job instance"""
        return execute(self.circuit, self.backend)

    def test_submit_job(self):
        """Test running a single circuit."""
        job = self._submit_job()
        self.assertIsInstance(job, HoneywellJob)

    def test_get_job_result(self):
        """Test get result of job"""
        job = self._submit_job()
        result = job.result()
        self.assertEqual(result.success, True)
        return result

    def test_get_job_status(self):
        """Test get status of job"""
        job = self._submit_job()
        status = job.status()
        self.assertIsInstance(status, JobStatus)

    def test_get_job_error_message(self):
        """Test get error message of job"""
        pass

    def test_get_creation_date(self):
        """Test get creation date of job"""
        job = self._submit_job()
        creation_date = job.creation_date()
        self.assertIsNotNone(creation_date)

    def test_get_job_id(self):
        """Test get id of job"""
        job = self._submit_job()
        job_id = job.job_id()
        self.assertIsNotNone(job_id)

    def test_job_with_id(self):
        """Test creating a job with an id."""
        job = self._submit_job()
        job_id = job.job_id()
        job_created_with_id = HoneywellJob(self.backend, job_id, self.api_cls())
        result = job_created_with_id.result()
        self.assertEqual(result.success, True)
        return result
