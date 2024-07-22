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
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Quantinuum TestCase for testing backends."""

from qiskit import execute
from qiskit import QuantumCircuit
from qiskit.providers.jobstatus import JobStatus
from qiskit.providers.models import BackendStatus
from qiskit.test import QiskitTestCase

from qiskit_quantinuum import Quantinuum
from qiskit_quantinuum import QuantinuumProvider
from qiskit_quantinuum import QuantinuumJob
from qiskit_quantinuum import QuantinuumBackend
from qiskit_quantinuum.api import QuantinuumClient

from .decorators import online_test


class QuantinuumBackendTestCase(QiskitTestCase):
    """Test case for Quantinuum backend.

    Members:
        proivder_cls (BaseProvider): provider to be used in this test case.
        api_cls (QuantinuumClient): api to be used in this test case
        backend_cls (BaseBackend): backend to be used in this test case. Its
            instantiation can be further customized by overriding the
            ``_get_backend`` function.
        backend_name (str): name of backend to be used in tests.
    """
    provider_cls = QuantinuumProvider
    api_cls = QuantinuumClient

    backend_cls = QuantinuumBackend
    backend_name = 'H1-1SC'

    def setUp(self):
        super().setUp()
        self.circuit = QuantumCircuit(4)
        self.circuit.h(0)
        self.circuit.cx(0, 1)
        self.circuit.h(0)
        self.circuit.cp(1.0, 0, 1)
        self.circuit.ccx(0, 1, 2)
        self.circuit.ccx(1, 2, 3)
        self.circuit.x(0)
        self.circuit.y(0)
        self.circuit.z(0)
        self.circuit.cx(0, 1)
        self.circuit.h(0)
        self.circuit.s(0)
        self.circuit.sdg(0)
        self.circuit.t(0)
        self.circuit.tdg(0)
        self.circuit.rx(1.0, 0)
        self.circuit.ry(1.0, 0)
        self.circuit.rz(1.0, 0)
        self.circuit.cz(0, 1)
        self.circuit.cy(0, 2)
        self.circuit.ch(0, 3)
        self.circuit.ccx(0, 1, 2)
        self.circuit.crz(1.0, 0, 1)
        self.circuit.crx(1.0, 0, 1)
        self.circuit.cry(1.0, 0, 1)
        self.circuit.cp(1.0, 0, 1)
        self.circuit.cu(1.0, 2.0, 3.0, 0.0, 0, 1)
        self.circuit.measure_all()

    def test_configuration(self):
        """Test backend.configuration()."""
        pass

    def test_properties(self):
        """Test backend.properties()."""
        pass

    @online_test
    def test_provider(self):
        """Test backend.provider()."""
        Quantinuum.load_account()
        backend = Quantinuum.get_backend(self.backend_name)
        provider = backend.provider()
        self.assertEqual(provider, self.provider_cls())

    @online_test
    def test_status(self):
        """Test backend.status()."""
        Quantinuum.load_account()
        backend = Quantinuum.get_backend(self.backend_name)
        status = backend.status()
        self.assertIsInstance(status, BackendStatus)

    @online_test
    def test_name(self):
        """Test backend.name()."""
        Quantinuum.load_account()
        backend = Quantinuum.get_backend(self.backend_name)
        name = backend.name()
        self.assertEqual(name, self.backend_name)

    @online_test
    def _submit_job(self):
        """Helper method to submit job and return job instance"""
        Quantinuum.load_account()
        backend = Quantinuum.get_backend(self.backend_name)
        return execute(self.circuit, backend)

    @online_test
    def test_submit_job(self):
        """Test running a single circuit."""
        Quantinuum.load_account()
        job = self._submit_job()
        self.assertIsInstance(job, QuantinuumJob)

    @online_test
    def test_get_job_result(self):
        """Test get result of job"""
        Quantinuum.load_account()
        job = self._submit_job()
        result = job.result()
        self.assertEqual(result.success, True)
        return result

    @online_test
    def test_get_job_status(self):
        """Test get status of job"""
        job = self._submit_job()
        Quantinuum.load_account()
        status = job.status()
        self.assertIsInstance(status, JobStatus)

    def test_get_job_error_message(self):
        """Test get error message of job"""
        pass

    @online_test
    def test_get_creation_date(self):
        """Test get creation date of job"""
        Quantinuum.load_account()
        job = self._submit_job()
        creation_date = job.creation_date()
        self.assertIsNotNone(creation_date)

    @online_test
    def test_get_job_id(self):
        """Test get id of job"""
        Quantinuum.load_account()
        job = self._submit_job()
        job_id = job.job_id()
        self.assertIsNotNone(job_id)

    @online_test
    def test_job_with_id(self):
        """Test creating a job with an id."""
        Quantinuum.load_account()
        backend = Quantinuum.get_backend(self.backend_name)
        job = self._submit_job()
        job_id = job.job_id()
        credentials = backend.provider().credentials
        job_created_with_id = QuantinuumJob(backend, job_id, self.api_cls(credentials))
        result = job_created_with_id.result()
        self.assertEqual(result.success, True)
        return result
