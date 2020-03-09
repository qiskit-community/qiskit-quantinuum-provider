# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=missing-class-docstring, missing-function-docstring

"""Test credentials."""

from unittest import mock

from qiskit.providers.honeywell import credentials

from qiskit.test import QiskitTestCase


class TestCredentials(QiskitTestCase):

    @mock.patch.object(credentials, 'read_creds_from_qiskitrc',
                       return_value=None)
    @mock.patch.object(credentials, 'read_creds_from_environ',
                       return_value=None)
    def test_discover_credentials_no_creds(self, environ_mock, qiskitrc_mock):
        self.assertEqual(None,
                         credentials.discover_credentials())
        qiskitrc_mock.assert_called_once_with(
            filename=credentials.DEFAULT_QISKITRC_FILE)
        environ_mock.assert_called_once_with()
