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

import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'nest-asyncio>=1.2.0',
    'qiskit-terra>=0.10',
    'requests>=2.19',
    'websockets>=8'
]

version_str = '0.1.0'
if os.environ.get('BRANCH_NAME', '') == 'dev':
    version_str += '.dev' + os.environ.get('BUILD_NUMBER', 9999)

setuptools.setup(
    name="qiskit-honeywell-provider",
    version=version_str,
    author="Honeywell",
    author_email="jack.suen@honeywell.com",
    description="Qiskit provider for accessing the quantum devices at Honeywell",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/Qiskit/qiskit-honeywell-provider",
    packages=setuptools.find_namespace_packages(include='qiskit.*'),
    install_requires=requirements,
    project_urls={
        "Bug Tracker": "https://github.com/Qiskit/qiskit-honeywell-provider/issues",
        "Documentation": "https://qiskit.org/documentation/",
        "Source Code": "https://github.com/Qiskit/qiskit-honeywell-provider"
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering"
    ],
)
