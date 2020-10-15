
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

from cr8rel.cli import MissingArgumentError
from cr8rel.cli import get_parser
from cr8rel.cli import validate
from cr8rel.cli import get_client
from cr8rel.cli import set_logging
from cr8rel.cli import main

from argparse import Namespace
from datetime import datetime


class TestCli(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        pass

    @patch('cr8rel.cli.ArgumentParser')
    def test__get_parser_Should_ReturnExpected_When_Called(self, *patches):
        # not much to unit test here
        get_parser()

    @patch('cr8rel.cli.os.access', return_value=False)
    def test__validate_Should_RaiseValueError_When_AssetsAreNotAccessible(self, *patches):
        args = Namespace(repo='org1/repo1', tag='v1.0.0', assets='assets/')
        with self.assertRaises(ValueError):
            validate(args)

    @patch('cr8rel.cli.os.getenv')
    @patch('cr8rel.cli.API')
    def test__get_client_Should_CallExpected_When_Called(self, api_patch, getenv_patch, *patches):
        getenv_patch.side_effect = ['api.github.com', 'token']
        get_client()
        api_patch.assert_called_once_with(hostname='api.github.com', bearer_token='token')

    @patch('cr8rel.cli.os.getenv')
    @patch('cr8rel.cli.logging')
    def test__set_logging_Should_CallExpected_When_Called(self, logging_patch, *patches):
        root_logger_mock = Mock()
        logging_patch.getLogger.return_value = root_logger_mock
        args_mock = Namespace(repo='org1/repo1', tag='v1.0.0', assets='assets/', debug=True)
        # not much to test here
        set_logging(args_mock)

    @patch('cr8rel.cli.logger')
    @patch('cr8rel.cli.get_parser')
    def test__main_Should_PrintUsage_When_MissingArgumentError(self, get_parser_patch, logger_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.side_effect = [MissingArgumentError('error')]
        get_parser_patch.return_value = parser_mock
        main()
        parser_mock.print_usage.assert_called_once_with()
        logger_patch.error.assert_called()

    @patch('cr8rel.cli.sys')
    @patch('cr8rel.cli.logger')
    @patch('cr8rel.cli.get_parser')
    def test__main_Should_Exit_When_Exception(self, get_parser_patch, logger_patch, sys_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.side_effect = [Exception('error')]
        get_parser_patch.return_value = parser_mock
        main()
        logger_patch.error.assert_called()
        sys_patch.exit.assert_called_once_with(-1)

    @patch('cr8rel.cli.set_logging')
    @patch('cr8rel.cli.validate')
    @patch('cr8rel.cli.get_parser')
    @patch('cr8rel.cli.get_client')
    def test__main_Should_CallExpected_When_Called(self, get_client_patch, get_parser_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.return_value = Namespace(repo='org1/repo1', tag='v1.0.0', assets='assets/', release=None)
        get_parser_patch.return_value = parser_mock
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        main()
        client_mock.create_release_upload_assets.assert_called_once_with(
            'org1/repo1', 'v1.0.0', 'assets/', release_name=None)
