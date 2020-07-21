
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

from prunetags.api import match_keys
from prunetags.api import is_connection_error
from prunetags.api import is_ratelimit_error
from prunetags import GitHubAPI

from datetime import datetime
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

    def setUp(self):

        self.items = [
            {
                'name': 'name1-mid-last1',
                'key1': 'value1',
                'key2': 'value2',
                'key3': 'value3'
            }, {
                'name': 'name2-mid-last2',
                'key1': 'value1',
                'key2': 'value2',
                'key3': 'value3.2'
            }, {
                'name': 'name3-med-last3',
                'key1': 'value1',
                'key2': 'value2',
                'key3': 'value3'
            }, {
                'name': 'name4-mid-last4',
                'key1': 'value1',
                'key2': 'value2',
                'key3': 'value3'
            }
        ]

    def tearDown(self):

        pass

    def test__match_keys_Should_Return_Items_When_NoAttributes(self, *patches):
        result = match_keys(self.items, None)
        self.assertEqual(result, self.items)

    def test__match_keys_Should_ReturnExpected_When_Called(self, *patches):
        result = match_keys(self.items, ['name', 'key1'])
        expected_result = [
            {
                'name': 'name1-mid-last1',
                'key1': 'value1'
            }, {
                'name': 'name2-mid-last2',
                'key1': 'value1'
            }, {
                'name': 'name3-med-last3',
                'key1': 'value1'
            }, {
                'name': 'name4-mid-last4',
                'key1': 'value1'
            }
        ]
        self.assertEqual(result, expected_result)

    @patch('prunetags.api.logger')
    def test__log_ratelimit_Should_NotLog_When_NoHeader(self, logger_patch, *patches):
        GitHubAPI.log_ratelimit({})
        logger_patch.debug.assert_not_called()

    @patch('prunetags.api.datetime')
    @patch('prunetags.api.logger')
    def test__log_ratelimit_Should_LogExpected_When_Header(self, logger_patch, datetime_patch, *patches):
        datetime_patch.now.return_value = datetime(2020, 5, 6, 18, 22, 45, 12065)
        datetime_patch.fromtimestamp.return_value = datetime(2020, 5, 6, 19, 20, 51)
        header = {
            'X-RateLimit-Reset': '1588792851',
            'X-RateLimit-Remaining': '4999',
            'X-RateLimit-Limit': '5000'
        }
        GitHubAPI.log_ratelimit(header)
        logger_patch.debug.assert_called_with('4999/5000 resets in 58 min')

    def test__is_connection_error_Should_Return_False_When_NoMatch(self, *patches):

        self.assertFalse(is_connection_error(Exception('test')))

    def test__is_connection_error_Should_Return_True_When_SSLError(self, *patches):

        self.assertTrue(is_connection_error(SSLError('test')))

    def test__is_connection_error_Should_Return_True_When_ProxyError(self, *patches):

        self.assertTrue(is_connection_error(ProxyError('test')))

    def test__is_connection_error_Should_Return_True_When_ConnectionError(self, *patches):

        self.assertTrue(is_connection_error(ConnectionError('test')))

    def test__is_ratelimit_error_Should_Return_False_When_NoMatch(self, *patches):

        self.assertFalse(is_ratelimit_error(Exception('test')))

    def test__is_ratelimit_error_Should_Return_True_When_Match(self, *patches):
        response_mock = Mock(status_code=403)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        self.assertTrue(is_ratelimit_error(http_error_mock))

    def test__init__Should_RaiseValueError_When_NoBearerToken(self, *patches):
        with self.assertRaises(ValueError):
            GitHubAPI('api.github.com')

    @patch('prunetags.api.GitHubAPI.log_ratelimit')
    def test__get_response_Should_CallExpected_When_Called(self, log_ratelimit_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        response_mock = Mock(headers={'key': 'value'})
        client.get_response(response_mock)
        log_ratelimit_patch.assert_called_once_with(response_mock.headers)

    def test__get_headers_Should_SetAcceptHeader_When_Called(self, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.get_headers()
        self.assertEqual(result['Accept'], 'application/vnd.github.v3+json')

    def test__get_next_endpoint_Should_ReturnNone_When_NoLinkHeader(self, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        self.assertIsNone(client.get_next_endpoint(None))

    def test__get_next_endpoint_Should_ReturnExpected_When_CalledWithNextEndpoint(self, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        link_header = '<https://api.github.com/organizations/27781926/repos?page=2>; rel="prev", <https://api.github.com/organizations/27781926/repos?page=4>; rel="next", <https://api.github.com/organizations/27781926/repos?page=4>; rel="last", <https://api.github.com/organizations/27781926/repos?page=1>; rel="first"'
        result = client.get_next_endpoint(link_header)
        expected_result = '/organizations/27781926/repos?page=4'
        self.assertEqual(result, expected_result)

    def test__get_next_endpoint_Should_ReturnNone_When_NoNextEndpoint(self, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        link_header = '<https://api.github.com/organizations/27781926/repos?page=3>; rel="prev", <https://api.github.com/organizations/27781926/repos?page=1>; rel="first"'
        result = client.get_next_endpoint(link_header)
        self.assertIsNone(result)

    @patch('prunetags.GitHubAPI.get_next_endpoint')
    @patch('prunetags.GitHubAPI.ratelimit_request')
    def test__read_all_Should_ReturnExpected_When_GetReturnsList(self, ratelimit_request_patch, get_next_endpoint_patch, *patches):
        response_mock1 = Mock()
        response_mock1.json.return_value = ['item1', 'item2']
        response_mock2 = Mock()
        response_mock2.json.return_value = ['item3', 'item4']
        ratelimit_request_patch.side_effect = [
            response_mock1,
            response_mock2
        ]
        get_next_endpoint_patch.side_effect = [
            {'Link': 'link-header-value'},
            {}
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.read_all('/repos/edgexfoundry/cd-management/milestones')
        expected_result = ['item1', 'item2', 'item3', 'item4']
        self.assertEqual(result, expected_result)

    @patch('prunetags.GitHubAPI.get_next_endpoint')
    @patch('prunetags.GitHubAPI.ratelimit_request')
    def test__read_all_Should_ReturnExpected_When_GetReturnsDict(self, ratelimit_request_patch, get_next_endpoint_patch, *patches):
        response_mock1 = Mock()
        response_mock1.json.return_value = {'key1': 'value1'}
        response_mock2 = Mock()
        response_mock2.json.return_value = {'key2': 'value2'}
        ratelimit_request_patch.side_effect = [
            response_mock1,
            response_mock2
        ]
        get_next_endpoint_patch.side_effect = [
            {'Link': 'link-header-value'},
            {}
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.read_all('/repos/edgexfoundry/cd-management/milestones')
        expected_result = [{'key1': 'value1'}, {'key2': 'value2'}]
        self.assertEqual(result, expected_result)

    @patch('prunetags.api.match_keys')
    @patch('prunetags.GitHubAPI.read_all')
    def test__read_Should_CallExpected_When_Called(self, read_all_patch, match_keys_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones'
        attributes = ['key1', 'key2']
        result = client.read(endpoint, attributes=attributes)
        read_all_patch.assert_called_once_with(endpoint)
        match_keys_patch.assert_called_once_with(read_all_patch.return_value, attributes)
        self.assertEqual(result, match_keys_patch.return_value)

    @patch('prunetags.GitHubAPI.get_next_endpoint')
    @patch('prunetags.GitHubAPI.ratelimit_request')
    def test__read_page_Should_ReturnExpected_When_Called(self, ratelimit_request_patch, get_next_endpoint_patch, *patches):
        response_mock1 = Mock()
        response_mock1.json.return_value = [
            'page1',
            'page2'
        ]
        response_mock2 = Mock()
        response_mock2.json.return_value = [
            'page3',
            'page4'
        ]
        ratelimit_request_patch.side_effect = [
            response_mock1,
            response_mock2
        ]
        get_next_endpoint_patch.return_value = [
            'next-endpoint',
            'next-endpoint'
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.read_page('endpoint')
        self.assertEqual(next(result), 'page1')
        self.assertEqual(next(result), 'page2')
        self.assertEqual(next(result), 'page3')
        self.assertEqual(next(result), 'page4')
        with self.assertRaises(StopIteration):
            next(result)

    @patch('prunetags.GitHubAPI.get_next_endpoint')
    @patch('prunetags.GitHubAPI.ratelimit_request')
    def test__read_page_Should_ReturnExpected_When_NoEndpoint(self, ratelimit_request_patch, get_next_endpoint_patch, *patches):
        response_mock1 = Mock()
        response_mock1.json.return_value = [
            'page1',
            'page2'
        ]
        ratelimit_request_patch.side_effect = [
            response_mock1
        ]
        get_next_endpoint_patch.side_effect = [
            None
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.read_page('endpoint')
        self.assertEqual(next(result), 'page1')
        self.assertEqual(next(result), 'page2')
        with self.assertRaises(StopIteration):
            next(result)

    @patch('prunetags.GitHubAPI.match_repos')
    @patch('prunetags.GitHubAPI.read_all')
    def test__get_repos_Should_CallAndReturnExpected_When_UserRegexAttributes(self, read_all_patch, match_repos_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.get_repos(user='soda480', include=r'^test_repo.*$', archived=False, disabled=False)
        read_all_patch.assert_called_once_with('/users/soda480/repos')
        match_repos_patch.assert_called_once_with(
            repos=read_all_patch.return_value,
            owner='soda480',
            include='^test_repo.*$',
            exclude=None,
            archived=False,
            disabled=False)
        self.assertEqual(result, match_repos_patch.return_value)

    @patch('prunetags.GitHubAPI.match_repos')
    @patch('prunetags.GitHubAPI.read_all')
    def test__get_repos_Should_CallAndReturnExpected_When_OrganizationExcludeAttributes(self, read_all_patch, match_repos_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.get_repos(organization='org1', exclude=['repo1', 'repo2'], archived=False, disabled=False)
        read_all_patch.assert_called_once_with('/orgs/org1/repos')
        match_repos_patch.assert_called_once_with(
            repos=read_all_patch.return_value,
            owner='org1',
            include=None,
            exclude=['repo1', 'repo2'],
            archived=False,
            disabled=False)
        self.assertEqual(result, match_repos_patch.return_value)

    @patch('prunetags.GitHubAPI.get_version')
    @patch('prunetags.GitHubAPI.lookup_tag')
    @patch('prunetags.GitHubAPI.read_page')
    def test__get_latest_version_Should_CallAndReturnExpected_When_Called(self, read_page_patch, lookup_tag_patch, get_version_patch, *patches):
        read_page_patch.return_value = [
            {'sha': '-sha1-'},
            {'sha': '-sha2-'},
            {'sha': '-sha3-'}
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        tags = ['tag1', 'tag2']
        result = client.get_latest_version(repo='soda480/repo1', tags=tags)
        self.assertEqual(result, (get_version_patch.return_value, '-sha1-'))
        read_page_patch.assert_called_once_with('/repos/soda480/repo1/commits?sha=master')
        lookup_tag_patch.assert_called_with(tags=tags, sha='-sha1-')

    @patch('prunetags.GitHubAPI.get_version')
    @patch('prunetags.GitHubAPI.lookup_tag')
    @patch('prunetags.GitHubAPI.read_page')
    def test__get_latest_version_Should_ReturnExpected_When_NoTagFound(self, read_page_patch, lookup_tag_patch, get_version_patch, *patches):
        read_page_patch.return_value = [
            {'sha': '-sha1-'},
            {'sha': '-sha2-'},
            {'sha': '-sha3-'}
        ]
        lookup_tag_patch.side_effect = [
            None,
            None,
            None
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        tags = ['tag1', 'tag2']
        result = client.get_latest_version(repo='soda480/repo1', tags=tags)
        self.assertEqual(result, (None, None))

    @patch('prunetags.GitHubAPI.get_latest_version')
    @patch('prunetags.GitHubAPI.read_all')
    def test__get_prerelease_tags_Should_Return_When_NoTags(self, read_all_patch, get_latest_version_patch, *patches):
        read_all_patch.return_value = []
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        client.get_prerelease_tags(repo='org1/repo1', branch='master')
        get_latest_version_patch.assert_not_called()

    @patch('prunetags.GitHubAPI.read_all')
    @patch('prunetags.GitHubAPI.filter_prerelease_tags')
    @patch('prunetags.GitHubAPI.get_latest_version')
    def test__get_prerelease_tags_Should_Return_When_NoLatestTagVersion(self, get_latest_version_patch, filter_prerelease_tags_patch, *patches):
        get_latest_version_patch.return_value = (None, None)
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        client.get_prerelease_tags(repo='org1/repo1', branch='master')
        filter_prerelease_tags_patch.assert_not_called()

    @patch('prunetags.GitHubAPI.read_all')
    @patch('prunetags.GitHubAPI.filter_prerelease_tags')
    @patch('prunetags.GitHubAPI.get_latest_version')
    def test__get_prerelease_tags_Should_CallAndReturnExpected_When_Called(self, get_latest_version_patch, filter_prerelease_tags_patch, *patches):
        get_latest_version_patch.return_value = Version('1.2.3-dev.1'), 'sha0'
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.get_prerelease_tags(repo='org1/repo1', branch='master')
        expected_result = (filter_prerelease_tags_patch.return_value, Version('1.2.3-dev.1'), 'sha0')
        self.assertEqual(result, expected_result)

    @patch('prunetags.GitHubAPI.generate_preprelease_report')
    @patch('prunetags.GitHubAPI.get_prerelease_tags')
    def test__get_prerelease_tags_report_Should_ReturnExpected_When_Called(self, get_prerelease_tags_patch, generate_preprelease_report_patch, *patches):
        get_prerelease_tags_patch.side_effect = [
            ('-tags-', '-latest-version-', '-latest-version-sha-'),
            None,
            ('-tags-', '-latest-version-', '-latest-version-sha-'),
        ]
        generate_preprelease_report_patch.side_effect = [
            {'repo1': {}},
            {'repo3': {}}
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        repos = [
            'repo1',
            'repo2',
            'repo3'
        ]
        result = client.get_prerelease_tags_report(repos=repos)
        expected_result = {
            'repo1': {},
            'repo2': {},
            'repo3': {}
        }
        self.assertEqual(result, expected_result)

    def test__generate_prerelease_report_Should_ReturnExpected_When_Called(self, *patches):
        prerelease_tags = [
            ('v1.2.2-dev.1', 'sha1'),
            ('v1.2.1-dev.2', 'sha2'),
            ('v1.2.1-dev.1', 'sha3')
        ]
        result = GitHubAPI.generate_preprelease_report(repo='soda480/repo1', prerelease_tags=prerelease_tags, latest_version=Version('1.2.3'), latest_version_sha='sha0')
        expected_result = {
            'soda480/repo1': {
                'latest_version': ('1.2.3', 'sha0'),
                'prerelease_tags': [
                    ('v1.2.2-dev.1', 'sha1'),
                    ('v1.2.1-dev.2', 'sha2'),
                    ('v1.2.1-dev.1', 'sha3')
                ],
                'prerelease_tags_count': 3
            }
        }
        self.assertEqual(result, expected_result)

    @patch('prunetags.GitHubAPI.ratelimit_request')
    @patch('prunetags.GitHubAPI.get_prerelease_tags')
    def test__remove_prerelease_tags_Should_Return_When_NoTags(self, get_prerelease_tags_patch, ratelimit_request_patch, *patches):
        get_prerelease_tags_patch.return_value = None
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        client.remove_prerelease_tags(repo='org1/repo1', branch='master', noop=False)
        ratelimit_request_patch.assert_not_called()

    @patch('prunetags.api.sleep')
    @patch('prunetags.GitHubAPI.ratelimit_request')
    @patch('prunetags.GitHubAPI.get_prerelease_tags')
    def test__remove_prerelease_tags_Should_CallExpected_When_Called(self, get_prerelease_tags_patch, ratelimit_request_patch, *patches):
        get_prerelease_tags_patch.return_value = (
            [('tag1', 'sha1'), ('tag2', 'sha2')], '-latest-version-', '-latest-version-sha-'
        )
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        client.remove_prerelease_tags(repo='org1/repo1', branch='master', noop=True)
        ratelimit_request_patch.assert_called_with(client.delete, '/repos/org1/repo1/git/refs/tags/tag2', noop=True)

    @patch('prunetags.api.sleep')
    @patch('prunetags.api.logger')
    @patch('prunetags.GitHubAPI.ratelimit_request')
    @patch('prunetags.GitHubAPI.get_prerelease_tags')
    def test__remove_prerelease_tags_Should_LogErrorAndContinue_When_Exception(self, get_prerelease_tags_patch, ratelimit_request_patch, logger_patch, *patches):
        get_prerelease_tags_patch.return_value = (
            [('tag1', 'sha1'), ('tag2', 'sha2')], '-latest-version-', '-latest-version-sha-'
        )
        ratelimit_request_patch.side_effect = [
            Exception('request error'),
            None
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        client.remove_prerelease_tags(repo='org1/repo1', branch='master', noop=True)
        ratelimit_request_patch.assert_called_with(client.delete, '/repos/org1/repo1/git/refs/tags/tag2', noop=True)
        logger_patch.error.assert_called_with('error occurred removing tag tag1 from repo org1/repo1: request error')

    def test__match_repos_Should_ReturnExpected_When_Called(self, *patches):
        repos = [
            {'name': 'repo1'},
            {'name': 'test_repo1', 'key1': 'value1'},
            {'name': 'repo2'},
            {'name': 'test_repo2', 'key1': 'value1', 'key2': 'value2'}
        ]
        result = GitHubAPI.match_repos(repos=repos, owner='soda480', include=r'^test_repo.*$', exclude='test_repo2', key1='value1')
        expected_result = [
            'soda480/test_repo1'
        ]
        self.assertEqual(result, expected_result)

    def test__match_repos_Should_ReturnExpected_When_NoRegexNoExclude(self, *patches):
        repos = [
            {'name': 'repo1'},
            {'name': 'test_repo1', 'key1': 'value1'},
            {'name': 'repo2', 'key1': 'value2'},
            {'name': 'test_repo2', 'key1': 'value1', 'key2': 'value2'}
        ]
        result = GitHubAPI.match_repos(repos=repos, owner='soda480', include=None, exclude=None, key1='value1')
        expected_result = [
            'soda480/repo1',
            'soda480/test_repo1',
            'soda480/test_repo2'
        ]
        self.assertEqual(result, expected_result)

    def test__lookup_tag_Should_ReturnExpected_When_Called(self, *patches):
        tags = [
            {'commit': {'sha': 'sha2'}},
            {'commit': {'sha': 'sha3'}},
            {'commit': {'sha': 'sha1'}}
        ]
        result = GitHubAPI.lookup_tag(tags=tags, sha='sha1')
        expected_result = {'commit': {'sha': 'sha1'}}
        self.assertEqual(result, expected_result)

    def test__filter_prerelease_tags_Should_Return_Expected_When_Called(self, *patches):
        tags = [
            {'name': 'v1.2.3-dev.2', 'commit': {'sha': 'sha1'}},
            {'name': 'v1.2.3-dev.1', 'commit': {'sha': 'sha2'}},
            {'name': 'v1.2.2', 'commit': {'sha': 'sha3'}},
            {'name': 'v1.2.1', 'commit': {'sha': 'sha4'}},
            {'name': 'v1.2.0-dev.1', 'commit': {'sha': 'sha5'}},
            {'name': 'v1.1.9', 'commit': {'sha': 'sha6'}},
            {'name': 'v1.1.4-dev.1', 'commit': {'sha': 'sha7'}}
        ]
        result = GitHubAPI.filter_prerelease_tags(tags=tags, exclude=Version('1.2.3-dev.2'))
        expected_result = [
            ('v1.2.0-dev.1', 'sha5'),
            ('v1.1.4-dev.1', 'sha7')
        ]
        self.assertEqual(result, expected_result)

    @patch('prunetags.api.validate_version', return_value=False)
    def test__get_version_Should_ReturnExpected_When_Called(self, *patches):
        result = GitHubAPI.get_version(name='enjambre')
        self.assertIsNone(result)

    @patch('prunetags.api.getenv', return_value='token')
    @patch('prunetags.api.GitHubAPI')
    def test__get_client_Should_CallAndReturnExpected_When_Called(self, githubapi_patch, getenv_patch, *patches):
        getenv_patch.side_effect = [
            'url',
            'token'
        ]
        result = GitHubAPI.get_client()
        githubapi_patch.assert_called_once_with('url', bearer_token='token')
        self.assertEqual(result, githubapi_patch.return_value)

    def test__ratelimit_request_Should_CallAndReturnExpected_When_NoRawResponse(self, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        function_mock = Mock()
        result = client.ratelimit_request(function_mock, 'one', 2, True, k1='v1', k2='v2')
        function_mock.assert_called_once_with('one', 2, True, k1='v1', k2='v2')
        self.assertEqual(result, function_mock.return_value)

    def test__ratelimit_request_Should_CallAndReturnExpected_When_RawResponse(self, *patches):
        response_mock = Mock()
        function_mock = Mock()
        function_mock.return_value = response_mock
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.ratelimit_request(function_mock, 'one', 2, True, k1='v1', k2='v2', raw_response=True)
        function_mock.assert_called_once_with('one', 2, True, k1='v1', k2='v2', raw_response=True)
        self.assertEqual(result, function_mock.return_value)
        response_mock.raise_for_status.assert_called_once_with()
