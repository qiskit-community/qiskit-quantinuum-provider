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

"""Root REST adapter for the Honeywell Api."""

from .base import RestAdapterBase
from .backend import Backend
from .job import Job


class Api(RestAdapterBase):
    """Rest adapter for general endpoints."""

    URL_MAP = {
        'backends': '/machine?config=true',
        'job': '/job'
    }

    def backend(self, backend_name):
        """Return an adapter for a specific backend.

        Args:
            backend_name (str): name of the backend.

        Returns:
            Backend: the backend adapter.
        """
        return Backend(self.session, backend_name)

    def job(self, job_id):
        """Return a adapter for a specific job.

        Args:
            job_id (str): id of the job.

        Returns:
            Job: the backend adapter.
        """
        return Job(self.session, job_id)

    def backends(self):
        """Return the list of backends."""
        url = self.get_url('backends')
        return self.session.get(url).json()

    def submit_job(self, backend_name, qobj_config, qasm, name=None):
        """Submit a job for executing.

        Args:
            backend_name (str): the name of the backend.
            qobj_config (dict): the Qobj to be executed, as a dictionary.
            qasm (str): The qasm str to submit
            name (str): An optional name for the job

        Returns:
            dict: json response.
        """
        url = self.get_url('job')

        # TODO: Add compiler options to the payload
        payload = {
            'machine': backend_name,
            'count': qobj_config.get('shots', 1),
            'language': 'OPENQASM 2.0',
            'program': qasm,
            'priority': qobj_config.get('priority', 'normal')
        }
        if name:
            payload['name'] = name

        return self.session.post(url, json=payload).json()
