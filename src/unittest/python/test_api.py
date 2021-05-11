
# Copyright (c) 2020 Intel Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from mock import patch
from mock import mock_open
from mock import call
from mock import Mock

from envbuilder import API

from requests.exceptions import SSLError
from requests.exceptions import HTTPError
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError
from semantic_version import Version

import sys
import logging
logger = logging.getLogger(__name__)

consoleHandler = logging.StreamHandler(sys.stdout)
logFormatter = logging.Formatter(
    "%(asctime)s %(threadName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
consoleHandler.setFormatter(logFormatter)
rootLogger = logging.getLogger()
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.DEBUG)


class TestApi(unittest.TestCase):

    def tearDown(self):

        pass

    def test__init__Should_RaiseValueError_When_NoBearerToken(self, *patches):
        with self.assertRaises(ValueError):
            API()

    @patch('envbuilder.API.get')
    def test__get_latest_Should_ReturnExpected_When_UsingCustomOrg(self, get_patch, *patches):
        get_patch.return_value = [
            dict(name='v1.2.0-dev.1'),
            dict(name='v1.2.0-dev.2'),
            dict(name='v1.2.0-dev.3'),
            dict(name='v1.1.0'),
            dict(name='v1.0.0'),
        ]

        client = API(bearer_token='bearer-token')
        result = client.get_latest(repo='mock-repo', org='mock-org')

        get_patch.assert_called_once_with('/repos/mock-org/mock-repo/tags', _get='all')

        self.assertEqual(result, Version('1.1.0'))

    @patch('envbuilder.API.get')
    def test__get_latest_Should_ReturnExpected_When_UsingDefaultOrg(self, get_patch, *patches):
        get_patch.return_value = [
            dict(name='v1.2.0-dev.1'),
            dict(name='v1.2.0-dev.2'),
            dict(name='v1.2.0-dev.3'),
            dict(name='v1.1.0'),
            dict(name='v1.0.0'),
        ]

        client = API(bearer_token='bearer-token')
        result = client.get_latest(repo='mock-repo')

        get_patch.assert_called_once_with(
            '/repos/edgexfoundry/mock-repo/tags', _get='all')

        self.assertEqual(result, Version('1.1.0'))

    @patch('envbuilder.API.get')
    def test__get_latest_Should_ReturnExpected_When_UsingDefaultOrg(self, get_patch, *patches):
        get_patch.return_value = [
            dict(name='v1.2.0-dev.1'),
            dict(name='v1.2.0-dev.2'),
            dict(name='v1.2.0-dev.3'),
        ]

        client = API(bearer_token='bearer-token')
        result = client.get_latest(repo='mock-repo', org='mock-org')

        get_patch.assert_called_once_with('/repos/mock-org/mock-repo/tags', _get='all')

        self.assertEqual(result, None)

    @patch('envbuilder.API.get')
    def test__get_latest_Should_ReturnExpected_When_NoVInVersion(self, get_patch, *patches):
        get_patch.return_value = [
            dict(name='1.2.0'),
            dict(name='1.0.0'),
        ]

        client = API(bearer_token='bearer-token')
        result = client.get_latest(repo='mock-repo', org='mock-org')

        self.assertEqual(result, Version('1.2.0'))


    def test__retry_connection_error_Should_Return_False_When_NoMatch(self, *patches):
        response_mock = Mock(status_code=404)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        self.assertFalse(API.retry_connection_error(http_error_mock))

    def test__retry_connection_error_Should_Return_True_When_SSLError(self, *patches):

        self.assertTrue(API.retry_connection_error(SSLError('test')))

    def test__retry_connection_error_Should_Return_True_When_ProxyError(self, *patches):

        self.assertTrue(API.retry_connection_error(ProxyError('test')))

    def test__retry_connection_error_Should_Return_True_When_ConnectionError(self, *patches):

        self.assertTrue(API.retry_connection_error(ConnectionError('test')))
