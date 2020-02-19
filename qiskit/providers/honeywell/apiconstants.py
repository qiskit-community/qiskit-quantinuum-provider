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
