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

"""Module for interfacing with a Quantinuum Backend."""

import logging
import warnings

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV1
from qiskit.providers.models import BackendStatus
from qiskit.providers import Options
from qiskit.utils import deprecate_arguments
from qiskit import qobj as qobj_mod
from qiskit import pulse

from qiskit_quantinuum.exceptions import QiskitError
from .quantinuumjob import QuantinuumJob

logger = logging.getLogger(__name__)


class QuantinuumBackend(BackendV1):
    """Backend class interfacing with a Quantinuum backend."""

    def __init__(self, name, configuration, provider, api):
        """Initialize remote backend for Quantinuum Quantum Computer.

        Args:
            name (String): name of backend.
            configuration (BackendConfiguration): backend configuration
            provider (QuantinuumProvider): provider.
            api (QuantinuumClient): API client instance to use for backend
                communication
        """

        super().__init__(configuration=configuration, provider=provider)

        self._api = api
        self._name = name

    @classmethod
    def _default_options(cls):
        return Options(shots=1024, priority='normal')

    @deprecate_arguments({'qobj': 'run_input'})
    def run(self, run_input, **kwargs):
        """Run a circuit on the backend.

        Args:
            run_input (QuantumCircuit|list): A QuantumCircuit or a list of
                QuantumCircuit objects to run on the backend

        Returns:
            HoneywelJob: a handle to the async execution of the circuit(s) on
                the backend
        Raises:
            QiskitError: If a pulse schedule is passed in for ``run_input``
        """
        if isinstance(run_input, qobj_mod.QasmQobj):
            warnings.warn("Passing in a QASMQobj object to run() is "
                          "deprecated and will be removed in a future "
                          "release", DeprecationWarning)
            job = QuantinuumJob(self, None, self._api, circuits=run_input)
        elif isinstance(run_input, (qobj_mod.PulseQobj, pulse.Schedule)):
            raise QiskitError("Pulse jobs are not accepted")
        else:
            if isinstance(run_input, QuantumCircuit):
                run_input = [run_input]
            job_config = {}
            for kwarg in kwargs:
                if not hasattr(self.options, kwarg):
                    warnings.warn(
                        "Option %s is not used by this backend" % kwarg,
                        UserWarning, stacklevel=2)
                else:
                    job_config[kwarg] = kwargs[kwarg]
            if 'shots' not in job_config:
                job_config['shots'] = self.options.shots
                job_config['priority'] = self.options.priority
            job = QuantinuumJob(self, None, self._api, circuits=run_input,
                                job_config=job_config)
        job.submit()
        return job

    def retrieve_job(self, job_id):
        """ Returns the job associated with the given job_id """
        job = QuantinuumJob(self, job_id, self._api)
        return job

    def retrieve_jobs(self, job_ids):
        """ Returns a list of jobs associated with the given job_ids """
        return [QuantinuumJob(self, job_id, self._api) for job_id in job_ids]

    def status(self):
        """Return the online backend status.

        Returns:
            BackendStatus: The status of the backend.

        Raises:
            LookupError: If status for the backend can't be found.
            QuantinuumBackendError: If the status can't be formatted properly.
        """
        api_status = self._api.backend_status(self.name())

        try:
            return BackendStatus.from_dict(api_status)
        except QiskitError as ex:
            raise LookupError(
                "Couldn't get backend status: {0}".format(ex)
            )

    def name(self):
        return self._name
