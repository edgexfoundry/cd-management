
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

from githubsync.cli import MissingArgumentError
from githubsync.cli import get_parser
from githubsync.cli import get_blacklist_repos
from githubsync.cli import validate
from githubsync.cli import get_client
from githubsync.cli import get_screen_layout
from githubsync.cli import synchronize
from githubsync.cli import check_result
from githubsync.cli import initiate_multiprocess
from githubsync.cli import set_logging
from githubsync.cli import main

from argparse import Namespace


class TestCli(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        pass

    @patch('githubsync.cli.ArgumentParser')
    def test__get_parser_Should_ReturnExpected_When_Called(self, *patches):
        # not much to unit test here
        get_parser()

    def test__get_blacklist_repos_Should_ReturnExpected_When_Called(self, *patches):
        result = get_blacklist_repos(' repo1, repo2,  repo3  ')
        expected_result = ['repo1', 'repo2', 'repo3']
        self.assertEqual(result, expected_result)

    def test__validate_Should_RaiseMissArgumentError_When_NoTargetOrg(self, *patches):
        args = Namespace(target_org=None, source_repo='source-repo')
        with self.assertRaises(MissingArgumentError):
            validate(args)

    def test__validate_Should_RaiseMissArgumentError_When_NoSourceRepo(self, *patches):
        args = Namespace(target_org='target-org', source_repo=None)
        with self.assertRaises(MissingArgumentError):
            validate(args)

    @patch('githubsync.cli.get_gmt_time')
    def test__validate_Should_CallExpected_When_ModifiedSince(self, get_gmt_time_patch, *patches):
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since='1d', no_screen=None, noop=None)
        validate(args)
        get_gmt_time_patch.assert_called_once_with('1d')

    @patch('githubsync.cli.getenv', return_value='True')
    @patch('githubsync.cli.get_gmt_time')
    def test__validate_Should_SetNoop_When_DryRunTrue(self, *patches):
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since='1d', no_screen=None, noop=None)
        validate(args)
        self.assertTrue(args.noop)

    @patch('githubsync.cli.getenv', return_value='False')
    @patch('githubsync.cli.get_gmt_time')
    def test__validate_Should_NotSetNoop_When_DryRunFalse(self, *patches):
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since='1d', no_screen=None, noop=None)
        validate(args)
        self.assertFalse(args.noop)

    @patch('githubsync.cli.getenv', return_value='False')
    @patch('githubsync.cli.get_gmt_time')
    def test__validate_Should_NotSetNoop_When_DryRunFalseAndNoopTrue(self, *patches):
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since='1d', no_screen=None, noop=True)
        validate(args)
        self.assertTrue(args.noop)

    @patch('githubsync.cli.GitHubAPI')
    def test__get_client_Should_CallExpected_When_Called(self, githubapi_patch, *patches):
        get_client()
        githubapi_patch.get_client.assert_called_once_with()

    def test__get_screen_layout_Should_ReturnExpected_When_Called(self, *patches):
        # not much to test here
        get_screen_layout()

    def test__synchronize_Should_CallExpected_When_Called(self, *patches):
        client_mock = Mock()
        data = {
            'repo': 'repo1'
        }
        shared_data = {
            'owner': 'owner',
            'labels': ['label1', 'label2'],
            'milestones': ['milestone1', 'milestone2'],
            'source_repo': 'source-repo',
            'modified_since': 'modified-since',
            'noop': False,
            'client': client_mock
        }
        synchronize(data, shared_data)
        client_mock.sync_labels.assert_called_once_with(
            'owner/repo1',
            ['label1', 'label2'],
            'source-repo',
            modified_since='modified-since',
            noop=False)
        # client_mock.sync_milestones.assert_called_once_with(
        #     'owner/repo1',
        #     ['milestone1', 'milestone2'],
        #     'source-repo',
        #     modified_since='modified-since',
        #     noop=False)

    @patch('githubsync.cli.execute')
    def test__initiate_multiprocess_Should_CallExpected_When_Called(self, execute_patch, *patches):
        client_mock = Mock()
        client_mock.get_repos.return_value = ['repo1']
        client_mock.get_labels.return_value = ['label1', 'label2']
        client_mock.get_milestones.return_value = ['milestone1', 'milestone2']
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since='1d', noop=False, screen=True, processes=4)
        blacklist_repos = ['repo2', 'repo3']
        initiate_multiprocess(client_mock, args, blacklist_repos)
        execute_patch.assert_called()

    @patch('githubsync.cli.execute')
    def test__initiate_multiprocess_Should_Return_When_NoRepos(self, execute_patch, *patches):
        client_mock = Mock()
        client_mock.get_repos.return_value = []
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since='1d', noop=False, screen=True, processes=4)
        blacklist_repos = ['repo2', 'repo3']
        initiate_multiprocess(client_mock, args, blacklist_repos)
        execute_patch.assert_not_called()

    def test__check_result_Should_RaiseException_When_ProcessResultException(self, *patches):
        process_data = [
            {}, {}, {}, {'result': ValueError('error')}
        ]
        with self.assertRaises(Exception):
            check_result(process_data)

    @patch('githubsync.cli.getenv')
    @patch('githubsync.cli.logging')
    def test__set_logging_Should_CallExpected_When_Called(self, logging_patch, *patches):
        root_logger_mock = Mock()
        logging_patch.getLogger.return_value = root_logger_mock
        args_mock = Namespace(processes=None, screen=False, debug=True)
        # not much to test here
        set_logging(args_mock)

    @patch('githubsync.cli.logger')
    @patch('githubsync.cli.get_parser')
    def test__main_Should_PrintUsage_When_MissingArgumentError(self, get_parser_patch, logger_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.side_effect = [MissingArgumentError('error')]
        get_parser_patch.return_value = parser_mock
        main()
        parser_mock.print_usage.assert_called_once_with()
        logger_patch.error.assert_called()

    @patch('githubsync.cli.sys')
    @patch('githubsync.cli.logger')
    @patch('githubsync.cli.get_parser')
    def test__main_Should_Exit_When_Exception(self, get_parser_patch, logger_patch, sys_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.side_effect = [Exception('error')]
        get_parser_patch.return_value = parser_mock
        main()
        logger_patch.error.assert_called()
        sys_patch.exit.assert_called_once_with(-1)

    @patch('githubsync.cli.get_blacklist_repos')
    @patch('githubsync.cli.set_logging')
    @patch('githubsync.cli.validate')
    @patch('githubsync.cli.get_parser')
    @patch('githubsync.cli.get_client')
    def test__main__Should_CallExpected_When_NoMultiprocesses(self, get_client_patch, get_parser_patch, *patches):
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        parser_mock = Mock()
        parser_mock.parse_args.return_value = Namespace(source_repo='source-repo', target_org='target-org', processes=None, modified_since=None, blacklist_repos=None, noop=False, no_screen=None, debug=None)
        get_parser_patch.return_value = parser_mock
        main()
        client_mock.sync_repos.assert_called()

    @patch('githubsync.cli.get_blacklist_repos')
    @patch('githubsync.cli.set_logging')
    @patch('githubsync.cli.validate')
    @patch('githubsync.cli.initiate_multiprocess')
    @patch('githubsync.cli.get_parser')
    @patch('githubsync.cli.get_client')
    def test__main_Should_CallExpected_When_Multiprocess(self, get_client_patch, get_parser_patch, initiate_multiprocess_patch, *patches):
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        parser_mock = Mock()
        parser_mock.parse_args.return_value = Namespace(source_repo='source-repo', target_org='target-org', processes=4, modified_since=None, blacklist_repos=None, noop=False, no_screen=None)
        get_parser_patch.return_value = parser_mock
        main()
        initiate_multiprocess_patch.assert_called()
