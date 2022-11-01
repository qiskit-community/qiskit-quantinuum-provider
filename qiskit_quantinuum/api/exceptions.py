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

# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Exceptions related to the Quantinuum Api."""

from qiskit_quantinuum.exceptions import QuantinuumError


class ApiError(QuantinuumError):
    """QuantinuumConnector API error handling base class."""

    def __init__(self, usr_msg=None, dev_msg=None):
        """ApiError.

        Args:
            usr_msg (str): Short user facing message describing error.
            dev_msg (str or None): More detailed message to assist
                developer with resolving issue.
        """
        super().__init__(usr_msg)
        self.usr_msg = usr_msg
        self.dev_msg = dev_msg

    def __repr__(self):
        return repr(self.dev_msg)

    def __str__(self):
        return str(self.usr_msg)


class RequestsApiError(ApiError):
    """Exception re-raising a RequestException."""
    def __init__(self, original_exception, *args, **kwargs):
        self.original_exception = original_exception
        super().__init__(*args, **kwargs)
