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
    'qiskit-terra==0.8',
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
    url="https://co41-bitbucket.honeywell.lab:4443/projects/HQSSW/repos/qiskit-honeywell-provider/browse",
    packages=['qiskit.providers.honeywell',
              'qiskit.providers.honeywell.api',
              'qiskit.providers.honeywell.api.rest'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
