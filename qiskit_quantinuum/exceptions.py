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

"""Exception for the Quantinuum module."""

from qiskit.exceptions import QiskitError


class QuantinuumError(QiskitError):
    """Base class for errors raised by the Quantinuum provider module."""
    pass


class QuantinuumAccountError(QuantinuumError):
    """Base class for errors raised by account management."""
    pass


class QuantinuumCredentialsNotFound(QuantinuumError):
    """ Base class for errors found without credentials."""
    pass


class QuantinuumBackendError(QuantinuumError):
    """QuantinuumBackend Errors"""
    pass


class QuantinuumBackendValueError(QuantinuumError, ValueError):
    """Value errors thrown within QuantinuumBackend """
    pass
