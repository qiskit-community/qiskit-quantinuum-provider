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

"""Backends provided by Honeywell."""

import warnings

from .version import __version__

from .honeywellprovider import HoneywellProvider
from .honeywellbackend import HoneywellBackend
from .honeywelljob import HoneywellJob

# Setting future warning for package name change
warnings.warn("This is the final release of qiskit-honeywell-provider. "
              "It will be replaced by the qiskit-quantinuum-provider package in the future.",
              FutureWarning)

# Global instance to be used as the entry point for convenience.
Honeywell = HoneywellProvider()  # pylint: disable=invalid-name
