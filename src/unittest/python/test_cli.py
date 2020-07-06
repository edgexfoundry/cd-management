
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

from prunetags.cli import MissingArgumentError
from prunetags.cli import get_parser
from prunetags.cli import validate
from prunetags.cli import get_client
from prunetags.cli import get_screen_layout
from prunetags.cli import remove_prerelease_tags
from prunetags.cli import get_prerelease_tags_report
from prunetags.cli import check_result
from prunetags.cli import initiate_multiprocess
from prunetags.cli import set_logging
from prunetags.cli import get_repos
from prunetags.cli import prune_prerelease_tags
from prunetags.cli import write_json_file
from prunetags.cli import write_report
from prunetags.cli import main

from argparse import Namespace
from datetime import datetime


class TestCli(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        pass

    @patch('prunetags.cli.ArgumentParser')
    def test__get_parser_Should_ReturnExpected_When_Called(self, *patches):
        # not much to unit test here
        get_parser()

    def test__validate_Should_RaiseMissingArgumentError_When_NoOrgAndNoUser(self, *patches):
        args = Namespace(org=None, user=None)
        with self.assertRaises(MissingArgumentError):
            validate(args)

    def test__validate_Should_RaiseMissingArgumentError_When_OrgAndUser(self, *patches):
        args = Namespace(org='org1', user='user1')
        with self.assertRaises(MissingArgumentError):
            validate(args)

    @patch('prunetags.cli.getenv', return_value='True')
    def test__validate_Should_RaiseValueError_When_DryRunEnvTrueAndExecute(self, *patches):
        args = Namespace(org='org1', user=None, execute=True, screen=None)
        with self.assertRaises(ValueError):
            validate(args)

    def test__validate_Should_SetNoop_When_NotExecute(self, *patches):
        args = Namespace(org='org1', user=None, execute=False, screen=None)
        validate(args)
        self.assertTrue(args.noop)

    def test__validate_Should_SetNoop_When_Execute(self, *patches):
        args = Namespace(org='org1', user=None, execute=True, screen=None)
        validate(args)
        self.assertFalse(args.noop)

    def test__validate_Should_SetProcesses_When_ScreenAndNoProcesses(self, *patches):
        args = Namespace(org='org1', user=None, execute=True, screen=True, processes=None)
        validate(args)
        self.assertEqual(args.processes, 10)

    @patch('prunetags.cli.GitHubAPI')
    def test__get_client_Should_CallExpected_When_Called(self, githubapi_patch, *patches):
        get_client()
        githubapi_patch.get_client.assert_called_once_with()

    def test__get_screen_layout_Should_ReturnExpected_When_Called(self, *patches):
        # not much to test here
        get_screen_layout()

    def test__remove_prerelease_tags_Should_CallExpected_When_Called(self, *patches):
        data = {
            'repo': 'org1/repo1'
        }
        client_mock = Mock()
        shared_data = {
            'client': client_mock,
            'noop': False
        }
        remove_prerelease_tags(data, shared_data)
        client_mock.remove_prerelease_tags.assert_called_once_with(repo='org1/repo1', noop=False)

    def test__get_prerelease_tags_report_Should_CallExpected_When_Called(self, *patches):
        data = {
            'repo': 'org1/repo1'
        }
        client_mock = Mock()
        shared_data = {
            'client': client_mock
        }
        get_prerelease_tags_report(data, shared_data)
        client_mock.get_prerelease_tags_report.assert_called_once_with(repos=['org1/repo1'])

    def test__check_result_Should_RaiseException_When_ProcessResultException(self, *patches):
        process_data = [
            {}, {}, {}, {'result': ValueError('error')}
        ]
        with self.assertRaises(Exception):
            check_result(process_data)

    @patch('prunetags.cli.check_result')
    @patch('prunetags.cli.datetime')
    @patch('prunetags.cli.execute')
    @patch('prunetags.cli.get_screen_layout')
    def test__initiate_multiprocess_Should_CallExpected_When_Called(self, get_screen_layout_patch, execute_patch, datetime_patch, *patches):
        datetime_patch.now.return_value = datetime(2020, 5, 6, 18, 22, 45, 12065)
        client_mock = Mock()
        function_mock = Mock()
        args = Namespace(org='org1', user=None, execute=True, screen=True, processes=3, include_repos='test_repo', exclude_repos=None, noop=False)

        initiate_multiprocess(client_mock, function_mock, args, 'org1', ['org1/repo1'])
        execute_patch.assert_called_once_with(
            function=function_mock,
            process_data=[
                {'repo': 'org1/repo1'}
            ],
            shared_data={
                'client': client_mock,
                'owner': 'org1',
                'noop': False
            },
            number_of_processes=1,
            init_messages=[
                "'include_repos' is 'test_repo'",
                "'exclude_repos' is '-'",
                'retrieved total of 1 repos',
                "Started:05/06/2020 18:22:45"
            ],
            screen_layout=get_screen_layout_patch.return_value)

    @patch('prunetags.cli.getenv')
    @patch('prunetags.cli.logging')
    def test__set_logging_Should_CallExpected_When_Called(self, logging_patch, *patches):
        root_logger_mock = Mock()
        logging_patch.getLogger.return_value = root_logger_mock
        args_mock = Namespace(processes=None, screen=None, report=None, debug=True)
        # not much to test here
        set_logging(args_mock)

    def test__get_repos_Should_CallAndReturnExpected_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.get_repos.return_value = ['user1/repo1']
        args = Namespace(org=None, user='user1', execute=True, screen=True, processes=3, include_repos='test_repo', exclude_repos=None, noop=False)
        result = get_repos(client_mock, args)
        client_mock.get_repos.assert_called_once_with(
            organization=None,
            user='user1',
            include='test_repo',
            exclude=None,
            archived=False,
            disabled=False)
        self.assertEqual(result[0], 'user1')
        self.assertEqual(result[1], client_mock.get_repos.return_value)

    def test__prune_prerelease_tags_Should_CallExpected_When_Called(self, *pathes):
        args = Namespace(noop=False)
        client_mock = Mock()
        prune_prerelease_tags(client_mock, ['repo1', 'repo2'], args)
        call1 = call(repo='repo1', noop=False)
        self.assertTrue(call1 in client_mock.remove_prerelease_tags.mock_calls)

    @patch('prunetags.cli.open', create=False)
    @patch('prunetags.cli.json')
    def test__write_json_file_Should_CallExpected_When_Called(self, json_patch, *patches):
        write_json_file('report', 'owner')
        json_patch.dump.assert_called()

    @patch('prunetags.cli.write_json_file')
    def test__write_report_Should_CallExpected_When_Called(self, write_json_file_patch, *patches):
        result = [
            {'result': {'repo1': 'result1'}}
        ]
        write_report(result, 'org1')
        write_json_file_patch.assert_called_once_with({'repo1': 'result1'}, 'org1')

    @patch('prunetags.cli.logger')
    @patch('prunetags.cli.get_parser')
    def test__main_Should_PrintUsage_When_MissingArgumentError(self, get_parser_patch, logger_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.side_effect = [MissingArgumentError('error')]
        get_parser_patch.return_value = parser_mock
        main()
        parser_mock.print_usage.assert_called_once_with()
        logger_patch.error.assert_called()

    @patch('prunetags.cli.sys')
    @patch('prunetags.cli.logger')
    @patch('prunetags.cli.get_parser')
    def test__main_Should_Exit_When_Exception(self, get_parser_patch, logger_patch, sys_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.side_effect = [Exception('error')]
        get_parser_patch.return_value = parser_mock
        main()
        logger_patch.error.assert_called()
        sys_patch.exit.assert_called_once_with(-1)

    @patch('prunetags.cli.set_logging')
    @patch('prunetags.cli.validate')
    @patch('prunetags.cli.get_repos', return_value=('org1', ['repo1']))
    @patch('prunetags.cli.get_parser')
    @patch('prunetags.cli.get_client')
    @patch('prunetags.cli.prune_prerelease_tags')
    def test__main_Should_CallExpected_When_NoReportNoProcesses(self, prune_prerelease_tags_patch, get_client_patch, get_parser_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.return_value = Namespace(report=None, processes=None)
        get_parser_patch.return_value = parser_mock
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        main()
        prune_prerelease_tags_patch.assert_called_once_with(client_mock, ['repo1'], parser_mock.parse_args.return_value)

    @patch('prunetags.cli.set_logging')
    @patch('prunetags.cli.validate')
    @patch('prunetags.cli.get_repos', return_value=('org1', ['repo1']))
    @patch('prunetags.cli.write_report')
    @patch('prunetags.cli.get_parser')
    @patch('prunetags.cli.get_client')
    @patch('prunetags.cli.initiate_multiprocess')
    def test__main_Should_CallExpected_When_ReportNoProcesses(self, initiate_multiprocess_patch, get_client_patch, get_parser_patch, write_report_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.return_value = Namespace(report=True, processes=None)
        get_parser_patch.return_value = parser_mock
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        main()
        write_report_patch.assert_called_once()

    @patch('prunetags.cli.set_logging')
    @patch('prunetags.cli.validate')
    @patch('prunetags.cli.get_repos', return_value=('org1', ['repo1']))
    @patch('prunetags.cli.write_report')
    @patch('prunetags.cli.get_parser')
    @patch('prunetags.cli.get_client')
    @patch('prunetags.cli.initiate_multiprocess')
    def test__main_Should_CallExpected_When_NoReportAndProcesses(self, initiate_multiprocess_patch, get_client_patch, get_parser_patch, write_report_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.return_value = Namespace(report=False, processes=2)
        get_parser_patch.return_value = parser_mock
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        main()
        write_report_patch.assert_not_called()

    @patch('prunetags.cli.set_logging')
    @patch('prunetags.cli.validate')
    @patch('prunetags.cli.get_repos', return_value=('org1', []))
    @patch('prunetags.cli.get_parser')
    @patch('prunetags.cli.get_client')
    @patch('prunetags.cli.prune_prerelease_tags')
    def test__main_Should_CallExpected_When_NoRepos(self, prune_prerelease_tags_patch, get_client_patch, get_parser_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.return_value = Namespace(report=None, processes=None)
        get_parser_patch.return_value = parser_mock
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        main()
        prune_prerelease_tags_patch.assert_not_called()
