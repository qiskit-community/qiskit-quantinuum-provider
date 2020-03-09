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

"""Values used by the API for different values."""

import enum


class ApiJobStatus(enum.Enum):
    """Possible values used by the API for a job status.

    The enum names represent the strings returned by the API verbatim in
    several endpoints (`status()`, websocket information, etc). The general
    flow is:

    `QUEUED -> RUNNING -> COMPLETED`
    """

    QUEUED = 'queued'
    RUNNING = 'running'
    COMPLETED = 'completed'

    CANCELED = 'canceled'
    FAILED = 'failed'


API_JOB_FINAL_STATES = (
    ApiJobStatus.COMPLETED,
    ApiJobStatus.CANCELED,
    ApiJobStatus.FAILED
)
