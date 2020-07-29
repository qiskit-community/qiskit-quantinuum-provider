# This code is part of Qiskit
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

import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'nest-asyncio>=1.2.0',
    'qiskit-terra>=0.10',
    'requests>=2.19',
    'websockets>=7'
]

version_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'qiskit', 'providers', 'honeywell',
    'VERSION.txt'))

with open(version_path, 'r') as fd:
    version_str = fd.read().rstrip()

setuptools.setup(
    name="qiskit-honeywell-provider",
    version=version_str,
    author="Honeywell",
    author_email="dominic.lucchetti@honeywell.com",
    license="Apache 2.0",
    description="Qiskit provider for accessing the quantum devices at Honeywell",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/qiskit-community/qiskit-honeywell-provider",
    packages=setuptools.find_namespace_packages(include=['qiskit.*']),
    install_requires=requirements,
    python_requires=">=3.5",
    include_package_data=True,
    keywords="qiskit quantum",
    project_urls={
        "Bug Tracker": "https://github.com/qiskit-community/qiskit-honeywell-provider/issues",
        "Documentation": "https://qiskit.org/documentation/",
        "Source Code": "https://github.com/qiskit-community/qiskit-honeywell-provider"
    },
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering"
    ],
    zip_safe=False,
)
