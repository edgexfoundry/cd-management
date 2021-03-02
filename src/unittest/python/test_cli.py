
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

from synclabels.cli import MissingArgumentError
from synclabels.cli import get_parser
from synclabels.cli import get_exclude_repos
from synclabels.cli import get_process_data
from synclabels.cli import validate
from synclabels.cli import get_client
from synclabels.cli import get_screen_layout
from synclabels.cli import synchronize
from synclabels.cli import check_result
from synclabels.cli import initiate_multiprocess
from synclabels.cli import set_logging
from synclabels.cli import main

from argparse import Namespace


class TestCli(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        pass

    @patch('synclabels.cli.ArgumentParser')
    def test__get_parser_Should_ReturnExpected_When_Called(self, *patches):
        # not much to unit test here
        get_parser()

    def test__get_exclude_repos_Should_ReturnExpected_When_SourceInOrg(self, *patches):
        result = get_exclude_repos(' repo1, repo2,  repo3  ', 'org1/repo0', 'org1')
        expected_result = ['repo0', 'repo1', 'repo2', 'repo3']
        self.assertEqual(result, expected_result)

    def test__get_exclude_repos_Should_ReturnExpected_When_SourceNotInOrg(self, *patches):
        result = get_exclude_repos(' repo1, repo2,  repo3  ', 'org2/repo0', 'org1')
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

    @patch('synclabels.API.get_gmt_time')
    def test__validate_Should_CallExpected_When_ModifiedSince(self, get_gmt_time_patch, *patches):
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since='1d', no_screen=None, execute=True)
        validate(args)
        get_gmt_time_patch.assert_called_once_with('1d')

    @patch('synclabels.cli.getenv', return_value='True')
    def test__validate_Should_RaiseValueError_When_DryRunEnvTrueAndExecute(self, *patches):
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since=None, screen=None, execute=True)
        with self.assertRaises(ValueError):
            validate(args)

    def test__validate_Should_SetNoop_When_NotExecute(self, *patches):
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since=None, screen=None, execute=False)
        validate(args)
        self.assertTrue(args.noop)

    def test__validate_Should_SetNoop_When_Execute(self, *patches):
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since=None, screen=None, execute=True)
        validate(args)
        self.assertFalse(args.noop)

    @patch('synclabels.cli.getenv', return_value='token')
    @patch('synclabels.cli.API')
    def test__get_client_Should_CallExpected_When_Called(self, githubapi_patch, *patches):
        get_client()
        githubapi_patch.assert_called_once_with(bearer_token='token')

    def test__get_screen_layout_Should_ReturnExpected_When_Called(self, *patches):
        # not much to test here
        get_screen_layout()

    @patch('synclabels.cli.get_client')
    def test__synchronize_Should_CallExpected_When_Called(self, get_client_patch, *patches):
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        data = {
            'repo': 'repo1'
        }
        shared_data = {
            'owner': 'owner',
            'labels': ['label1', 'label2'],
            'milestones': ['milestone1', 'milestone2'],
            'source_repo': 'source-repo',
            'modified_since': 'modified-since',
            'noop': False
        }
        synchronize(data, shared_data)
        client_mock.sync_labels.assert_called_once_with(
            'owner/repo1',
            ['label1', 'label2'],
            'source-repo',
            modified_since='modified-since',
            noop=False)

    @patch('synclabels.cli.check_result')
    @patch('synclabels.cli.get_screen_layout')
    @patch('synclabels.cli.MPcurses')
    def test__initiate_multiprocess_Should_CallExpected_When_Called(self, mpcurses_patch, *patches):
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since='1d', execute=True, screen=True, processes=4, noop=False)
        exclude_repos = ['repo2', 'repo3']
        initiate_multiprocess(args, exclude_repos)
        mpcurses_patch.assert_called()

    @patch('synclabels.cli.check_result')
    @patch('synclabels.cli.get_process_data')
    @patch('synclabels.cli.MPcurses')
    def test__initiate_multiprocess_Should_CallExpected_When_NoScreen(self, mpcurses_patch, get_process_data_patch, *patches):
        get_process_data_patch.return_value = ([{'node': 1}, {'node': 2}], {'key1': 'value1'})
        args = Namespace(target_org='target-org', source_repo='source-repo', modified_since='1d', execute=True, screen=False, processes=4, noop=False)
        exclude_repos = ['repo2', 'repo3']
        initiate_multiprocess(args, exclude_repos)
        mpcurses_patch.assert_called()

    def test__check_result_Should_RaiseException_When_ProcessResultException(self, *patches):
        process_data = [
            {}, {}, {}, {'result': ValueError('error')}
        ]
        with self.assertRaises(Exception):
            check_result(process_data)

    @patch('synclabels.cli.getenv')
    @patch('synclabels.cli.logging')
    def test__set_logging_Should_CallExpected_When_Called(self, logging_patch, *patches):
        root_logger_mock = Mock()
        logging_patch.getLogger.return_value = root_logger_mock
        args_mock = Namespace(processes=None, screen=False, debug=True)
        # not much to test here
        set_logging(args_mock)

    @patch('synclabels.cli.logger')
    @patch('synclabels.cli.get_parser')
    def test__main_Should_PrintUsage_When_MissingArgumentError(self, get_parser_patch, logger_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.side_effect = [MissingArgumentError('error')]
        get_parser_patch.return_value = parser_mock
        main()
        parser_mock.print_usage.assert_called_once_with()
        logger_patch.error.assert_called()

    @patch('synclabels.cli.sys')
    @patch('synclabels.cli.logger')
    @patch('synclabels.cli.get_parser')
    def test__main_Should_Exit_When_Exception(self, get_parser_patch, logger_patch, sys_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.side_effect = [Exception('error')]
        get_parser_patch.return_value = parser_mock
        main()
        logger_patch.error.assert_called()
        sys_patch.exit.assert_called_once_with(-1)

    @patch('synclabels.cli.get_exclude_repos')
    @patch('synclabels.cli.set_logging')
    @patch('synclabels.cli.validate')
    @patch('synclabels.cli.initiate_multiprocess')
    @patch('synclabels.cli.get_parser')
    @patch('synclabels.cli.get_client')
    def test__main_Should_CallExpected_When_Multiprocess(self, get_client_patch, get_parser_patch, initiate_multiprocess_patch, *patches):
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        parser_mock = Mock()
        parser_mock.parse_args.return_value = Namespace(source_repo='source-repo', target_org='target-org', processes=4, modified_since=None, exclude_repos=None, execute=True, screen=None, noop=False)
        get_parser_patch.return_value = parser_mock
        main()
        initiate_multiprocess_patch.assert_called()

    @patch('synclabels.cli.get_client')
    def test__get_process_data_Should_ReturnExpected_When_Repos(self, get_client_patch, *patches):
        client_mock = Mock()
        client_mock.get_repos.return_value = ['repo2', 'repo3']
        client_mock.get_labels.return_value = ['label1', 'label2']
        client_mock.get_milestones.return_value = ['milestone1', 'milestone2']
        get_client_patch.return_value = client_mock
        result = get_process_data(owner='org1', source_repo='repo1', exclude_repos='repo1')
        shared_data = {'owner': 'org1', 'source_repo': 'repo1', 'exclude_repos': 'repo1', 'repos': ['repo2', 'repo3'], 'labels': ['label1', 'label2'], 'milestones': ['milestone1', 'milestone2']}
        expected_result = ([{'repo': 'repo2'}, {'repo': 'repo3'}], shared_data)
        self.assertEqual(result, expected_result)

    @patch('synclabels.cli.get_client')
    def test__get_process_data_Should_ReturnExpected_When_NoRepos(self, get_client_patch, *patches):
        client_mock = Mock()
        client_mock.get_repos.return_value = []
        get_client_patch.return_value = client_mock
        result = get_process_data(owner='org1', source_repo='repo1', exclude_repos='repo1')
        shared_data = {'owner': 'org1', 'source_repo': 'repo1', 'exclude_repos': 'repo1'}
        expected_result = ([], shared_data)
        self.assertEqual(result, expected_result)
