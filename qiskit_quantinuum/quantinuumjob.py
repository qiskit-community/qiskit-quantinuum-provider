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

# pylint: disable=arguments-differ

"""QuantinuumJob module

This module is used for creating asynchronous job objects for Quantinuum.
"""
import asyncio
import json
import logging
from collections import Counter
from datetime import datetime, timezone
from time import sleep
import nest_asyncio
import websockets
from qiskit.assembler.disassemble import disassemble
from qiskit.providers import JobV1, JobError
from qiskit.providers.jobstatus import JOB_FINAL_STATES, JobStatus
from qiskit import qobj as qobj_mod
from qiskit.result import Result

from .apiconstants import ApiJobStatus

from .api import QuantinuumClient

logger = logging.getLogger(__name__)

# Because Qiskit is often used with the Jupyter notebook who runs its own asyncio event loop
# (via Tornado), we must be able to apply our own event loop. This is something that is done
# in the IBMQ provider as well
nest_asyncio.apply()


class QuantinuumJob(JobV1):
    """Representation of a job that will be execute on a Quantinuum backend.

    Represent the jobs that will be executed on Quantinuum devices. Jobs are
    intended to be created calling ``run()`` on a particular backend.

    Currently jobs that are created using a qobj can only have one experiment
    in the qobj. If more that one experiment exists in the qobj only the first
    experiment will be run and the rest will be ignored.

    Creating a ``Job`` instance does not imply running it. You need to do it in
    separate steps::

        job = QuantinuumJob(...)
        job.submit()

    An error while submitting a job will cause the next call to ``status()`` to
    raise. If submitting the job successes, you can inspect the job's status by
    using ``status()``. Status can be one of ``JobStatus`` members::

        from qiskit.backends.jobstatus import JobStatus

        job = QuantinuumJob(...)
        job.submit()

        try:
            job_status = job.status() # It will query the backend API.
            if job_status is JobStatus.RUNNING:
                print('The job is still running')

        except JobError as ex:
            print("Something wrong happened!: {}".format(ex))

    A call to ``status()`` can raise if something happens at the API level that
    prevents Qiskit from determining the status of the job. An example of this
    is a temporary connection lose or a network failure.

    ``Job`` instances also have `id()` and ``result()`` methods which will
    block::

        job = QuantinuumJob(...)
        job.submit()

        try:
            job_id = job.id()
            print('The job {} was successfully submitted'.format(job_id))

            job_result = job.result() # It will block until finishing.
            print('The job finished with result {}'.format(job_result))

        except JobError as ex:
            print("Something wrong happened!: {}".format(ex))

    Both methods can raise if something at the API level happens that prevent
    Qiskit from determining the status of the job.

    Note:
        When querying the API for getting the status, two kinds of errors are
        possible. The most severe is the one preventing Qiskit from getting a
        response from the backend. This can be caused by a network failure or a
        temporary system break. In these cases, calling ``status()`` will raise.

        If Qiskit successfully retrieves the status of a job, it could be it
        finished with errors. In that case, ``status()`` will simply return
        ``JobStatus.ERROR`` and you can call ``error_message()`` to get more
        info.
    """
    def __init__(self, backend, job_id, api=None, circuits=None, job_config=None):
        """QuantinuumJob init function.

        We can instantiate jobs from two sources: A circuit, and an already
        submitted job returned by the API servers.

        Args:
            backend (QuantinuumBackend): The backend instance used to run this job.
            job_id (str or None): The job ID of an already submitted job.
                Pass `None` if you are creating a new job.
            api (QuantinuumClient): Quantinuum api client.
            circuits (list): A list of quantum circuit objects to run. Can also
                be a ``QasmQobj`` object, but this is deprecated (and won't raise a
                warning (since it's raised by ``backend.run()``). See notes below
            job_config (dict): A dictionary for the job configuration options

        Notes:
            It is mandatory to pass either ``circuits`` or ``job_id``. Passing a ``circuits``
            will ignore ``job_id`` and will create an instance to be submitted to the
            API server for job creation. Passing only a `job_id` will create an instance
            representing an already-created job retrieved from the API server.
        """
        super().__init__(backend, job_id)

        if api:
            self._api = api
        else:
            self._api = QuantinuumClient(backend.provider().credentials)
        self._creation_date = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

        # Properties used for caching.
        self._cancelled = False
        self._api_error_msg = None
        self._result = None
        self._job_ids = []
        self._experiment_results = []

        self._qobj_payload = {}
        self._circuits_job = False
        if circuits:
            if isinstance(circuits, qobj_mod.QasmQobj):
                self._qobj_payload = circuits.to_dict()
                # Extract individual experiments
                #  if we want user qobj headers, the third argument contains it
                self._experiments, self._job_config, _ = disassemble(circuits)
                self._status = JobStatus.INITIALIZING
            else:
                self._experiments = circuits
                self._job_config = job_config
                self._circuits_job = True
        else:
            self._status = JobStatus.INITIALIZING
            self._job_ids.append(job_id)
            self._job_config = {}

    def submit(self):
        """Submit the job to the backend."""
        backend_name = self.backend().name()

        for exp in self._experiments:
            submit_info = self._api.job_submit(backend_name, self._job_config, exp.qasm())
            # Error in job after submission:
            # Transition to the `ERROR` final state.
            if 'error' in submit_info:
                self._status = JobStatus.ERROR
                self._api_error_msg = str(submit_info['error'])
                # Don't continue
                return
            self._job_ids.append(submit_info['job'])

        # Take the last submitted job's info
        self._creation_date = submit_info.get('submit-date')
        self._status = submit_info.get('status')
        self._job_id = submit_info.get('job')

    def result(self, timeout=300):
        """Return the result of the job.

        Args:
           timeout (float): number of seconds to wait for job

        Returns:
            qiskit.Result: Result object

        Raises:
            JobError: if attempted to recover a result on a failed job.

        Notes:
            Currently when calling get_counts() on a result returned by a Quantinuum
            backend, since Quantinuum backends currently support only running one
            experiment per job, do not supply an argument to the get_counts() function.
            Doing so may raise an exception.
        """
        if self._result:
            return self._result

        # Wait for results sequentially
        for job_id in self._job_ids:
            self._experiment_results.append(
                asyncio.get_event_loop().run_until_complete(self._get_status(job_id, timeout))
                )

        # Process results
        self._result = self._process_results()

        if not (self._status is JobStatus.DONE or self._status is JobStatus.CANCELLED):
            raise JobError('Invalid job state. The job should be DONE or CANCELLED but '
                           'it is {}'.format(str(self._status)))

        if not self._result:
            raise JobError('Server did not return result')

        return self._result

    def cancel(self):
        """Attempt to cancel job."""
        pass

    async def _get_status(self, job_id, timeout=300):
        """Query the API to update the status.

        Returns:
            qiskit.providers.JobStatus: The api response including the job status

        Raises:
            JobError: if there was an exception in the future being executed
                          or the server sent an unknown answer.
        """
        if job_id is None or self._status in JOB_FINAL_STATES:
            return self._status

        try:
            api_response = self._api.job_status(job_id)
            if 'websocket' in api_response:
                task_token = api_response['websocket']['task_token']
                execution_arn = api_response['websocket']['executionArn']
                credentials = self.backend().provider().credentials
                websocket_uri = credentials.url.replace('https://', 'wss://ws.')
                async with websockets.connect(
                        websocket_uri, extra_headers={
                            'Authorization': credentials.access_token}) as websocket:

                    body = {
                        "action": "OpenConnection",
                        "task_token": task_token,
                        "executionArn": execution_arn
                    }
                    await websocket.send(json.dumps(body))
                    api_response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                    api_response = json.loads(api_response)
            else:
                logger.warning('Websockets via proxy not supported.  Falling-back to polling.')
                residual_delay = timeout/1000  # convert us -> s
                request_delay = min(1.0, residual_delay)
                while api_response['status'] not in ['failed', 'completed', 'canceled']:
                    sleep(request_delay)
                    api_response = self._api.job_status(job_id)

                    residual_delay = residual_delay - request_delay
                    if residual_delay <= 0:
                        # break if we have exceeded timeout
                        break

                    # Max-out at 10 second delay
                    request_delay = min(min(request_delay*1.5, 10), residual_delay)
        except Exception as err:
            raise JobError(str(err))

        return api_response

    def status(self, timeout=300):
        """Query the API to update the status.

        Returns:
            qiskit.providers.JobStatus: The status of the job, once updated.

        Raises:
            JobError: if there was an exception in the future being executed
                          or the server sent an unknown answer.
        """
        # Wait for results sequentially
        for job_id in self._job_ids:
            self._experiment_results.append(
                asyncio.get_event_loop().run_until_complete(self._get_status(job_id, timeout))
                )

        # Process results
        self._result = self._process_results()

        return self._status

    def error_message(self):
        """Provide details about the reason of failure.

        Returns:
            str: An error report if the job errored or ``None`` otherwise.
        """
        for job_id in self._job_ids:
            if self.status(job_id) is not JobStatus.ERROR:
                return None

        if not self._api_error_msg:
            self._api_error_msg = 'An unknown error occurred.'

        return self._api_error_msg

    def _process_results(self):
        """Convert Quantinuum job result to qiskit.Result"""
        results = []
        self._status = JobStatus.DONE
        for i, res_resp in enumerate(self._experiment_results):
            status = res_resp.get('status', 'failed')
            if status == 'failed':
                self._status = JobStatus.ERROR
            res = res_resp['results']
            counts = dict(Counter(hex(int("".join(r), 2)) for r in [*zip(*list(res.values()))]))

            experiment_result = {
                'shots': self._job_config.get('shots', 1),
                'success': ApiJobStatus(status) is ApiJobStatus.COMPLETED,
                'data': {'counts': counts},
                'job_id': self._job_ids[i]
            }
            if self._circuits_job:
                if self._experiments[i].metadata is None:
                    metadata = {}
                else:
                    metadata = self._experiments[i].metadata
                experiment_result['header'] = metadata
            else:
                experiment_result['header'] = self._qobj_payload[
                    'experiments'][i]['header'] if self._qobj_payload else {}
            results.append(experiment_result)

        result = {
            'success': self._status is JobStatus.DONE,
            'job_id': self._job_id,
            'results': results,
            'backend_name': self._backend.name(),
            'backend_version': self._backend.status().backend_version,
            'qobj_id': self._job_id
        }
        return Result.from_dict(result)

    def creation_date(self):
        """Return creation date."""
        return self._creation_date

    def job_ids(self):
        """ Return all the job_ids associated with this experiment """
        return self._job_ids
