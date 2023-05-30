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

import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'nest-asyncio>=1.2.0',
    'qiskit-terra>=0.16.0',
    'requests>=2.19',
    'websockets>=7',
    'pyjwt>=2.4.0',
    'keyring>=10.6.0',
    'pytket>=0.3.0',
    'pytket-quantinuum>=0.9.0'
]

version_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'qiskit_quantinuum',
    'VERSION.txt'))

with open(version_path, 'r') as fd:
    version_str = fd.read().rstrip()

setuptools.setup(
    name="qiskit-quantinuum-provider",
    version=version_str,
    author="Quantinuum",
    author_email="dominic.lucchetti@quantinuum.com",
    license="Apache 2.0",
    description="Qiskit provider for accessing the quantum devices at Quantinuum",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/qiskit-community/qiskit-quantinuum-provider",
    packages=setuptools.find_namespace_packages(include=['qiskit_quantinuum*']),
    install_requires=requirements,
    python_requires=">=3.8",
    include_package_data=True,
    keywords="qiskit quantum",
    project_urls={
        "Bug Tracker": "https://github.com/qiskit-community/qiskit-quantinuum-provider/issues",
        "Documentation": "https://qiskit.org/documentation/",
        "Source Code": "https://github.com/qiskit-community/qiskit-quantinuum-provider"
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering"
    ],
    zip_safe=False,
)
