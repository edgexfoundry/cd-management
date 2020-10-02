
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

from githubsync.api import match_key_values
from githubsync.api import match_keys
from githubsync.api import log_ratelimit
from githubsync.api import is_connection_error
from githubsync.api import is_ratelimit_error
from githubsync.api import get_resource_id
from githubsync.api import get_resource
from githubsync.api import get_owner_repo
from githubsync.api import get_gmt_time
from githubsync import GitHubAPI

from datetime import datetime
from requests.exceptions import SSLError
from requests.exceptions import HTTPError
from requests.exceptions import ProxyError

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

    def test__match_key_values_Should_ReturnExpected_When_Called(self, *patches):
        regex = r'^.*-mid-.*$'
        result = match_key_values(self.items, regex, key1='value1', key3='value3')
        expected_result = [
            {
                'name': 'name1-mid-last1',
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
        self.assertEqual(result, expected_result)

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

    @patch('githubsync.api.logger')
    def test__log_ratelimit_Should_NotLog_When_NoHeader(self, logger_patch, *patches):
        log_ratelimit({})
        logger_patch.debug.assert_not_called()

    @patch('githubsync.api.datetime')
    @patch('githubsync.api.logger')
    def test__log_ratelimit_Should_LogExpected_When_Header(self, logger_patch, datetime_patch, *patches):
        datetime_patch.now.return_value = datetime(2020, 5, 6, 18, 22, 45, 12065)
        datetime_patch.fromtimestamp.return_value = datetime(2020, 5, 6, 19, 20, 51)
        header = {
            'X-RateLimit-Reset': '1588792851',
            'X-RateLimit-Remaining': '4999',
            'X-RateLimit-Limit': '5000'
        }
        log_ratelimit(header)
        logger_patch.info.assert_called_with('4999/5000 resets in 58 min')

    def test__is_connection_error_Should_Return_False_When_NoMatch(self, *patches):
        response_mock = Mock(status_code=404)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        self.assertFalse(is_connection_error(http_error_mock))

    def test__is_connection_error_Should_Return_True_When_SSLError(self, *patches):

        self.assertTrue(is_connection_error(SSLError('test')))

    def test__is_connection_error_Should_Return_True_When_ProxyError(self, *patches):

        self.assertTrue(is_connection_error(ProxyError('test')))

    def test__is_ratelimit_error_Should_Return_False_When_NoMatch(self, *patches):
        response_mock = Mock(status_code=404)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        self.assertFalse(is_ratelimit_error(http_error_mock))

    def test__is_ratelimit_error_Should_Return_True_When_Match(self, *patches):
        response_mock = Mock(status_code=403)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        self.assertTrue(is_ratelimit_error(http_error_mock))

    def test__get_resource_id_Should_ReturnExpected_When_Called(self, *patches):
        endpoint = '/repos/:owner/:repo/labels/label1'
        result = get_resource_id(endpoint)
        self.assertEqual(result, 'label1')

    def test__get_resource_Should_ReturnExpected_When_Called(self, *patches):
        endpoint = '/repos/:owner/:repo/labels/label1'
        result = get_resource(endpoint)
        self.assertEqual(result, 'label')

    def test__get_resource_Should_ReturnExpected_When_CalledWithIndex(self, *patches):
        endpoint = '/repos/:owner/:repo/labels'
        result = get_resource(endpoint, index=-1)
        self.assertEqual(result, 'label')

    def test__get_owner_repo_Should_ReturnExpected_When_Called(self, *patches):
        endpoint = '/repos/:owner/:repo/labels/label1'
        result = get_owner_repo(endpoint)
        self.assertEqual(result, ':owner/:repo')

    def test__get_gmt_time_Should_ReturnNone_When_NoDelta(self, *patches):

        self.assertIsNone(get_gmt_time(None))

    def test__get_gmt_time_Should_RaiseValueError_When_NoMatch(self, *patches):
        with self.assertRaises(ValueError):
            get_gmt_time('200 days')

    @patch('githubsync.api.datetime')
    def test__get_gmt_time_Should_ReturnExpected_When_CalledWithDays(self, datetime_patch, *patches):
        datetime_patch.now.return_value = datetime(2020, 5, 6, 18, 22, 45, 12065)
        result = get_gmt_time('1d')
        expected_result = 'Tue, 05 May 2020 18:22:45 '
        self.assertEqual(result, expected_result)

    @patch('githubsync.api.datetime')
    def test__get_gmt_time_Should_ReturnExpected_When_CalledWithHours(self, datetime_patch, *patches):
        datetime_patch.now.return_value = datetime(2020, 5, 6, 18, 22, 45, 12065)
        result = get_gmt_time('1h')
        expected_result = 'Wed, 06 May 2020 17:22:45 '
        self.assertEqual(result, expected_result)

    @patch('githubsync.api.datetime')
    def test__get_gmt_time_Should_ReturnExpected_When_CalledWithMinutes(self, datetime_patch, *patches):
        datetime_patch.now.return_value = datetime(2020, 5, 6, 18, 22, 45, 12065)
        result = get_gmt_time('1m')
        expected_result = 'Wed, 06 May 2020 18:21:45 '
        self.assertEqual(result, expected_result)

    def test__init__Should_RaiseValueError_When_NoBearerToken(self, *patches):
        with self.assertRaises(ValueError):
            GitHubAPI('api.github.com')

    @patch('githubsync.api.log_ratelimit')
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

    @patch('githubsync.GitHubAPI.get_next_endpoint')
    @patch('githubsync.GitHubAPI.ratelimit_request')
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

    @patch('githubsync.GitHubAPI.get_next_endpoint')
    @patch('githubsync.GitHubAPI.ratelimit_request')
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

    @patch('githubsync.api.match_keys')
    @patch('githubsync.GitHubAPI.read_all')
    def test__read_Should_CallExpected_When_Called(self, read_all_patch, match_keys_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones'
        attributes = ['key1', 'key2']
        result = client.read(endpoint, attributes=attributes)
        read_all_patch.assert_called_once_with(endpoint)
        match_keys_patch.assert_called_once_with(read_all_patch.return_value, attributes)
        self.assertEqual(result, match_keys_patch.return_value)

    @patch('githubsync.GitHubAPI.read_all')
    def test__get_repos_Should_ReturnRepos_When_UserAndNoRegexAndAttributes(self, read_all_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.get_repos(user='soda480')
        read_all_patch.assert_called_once_with('/users/soda480/repos')
        self.assertEqual(result, read_all_patch.return_value)

    @patch('githubsync.api.match_key_values')
    @patch('githubsync.GitHubAPI.read_all')
    def test__get_repos_Should_ReturnRepos_When_OrganizationAndRegexAndAttributesAndBlackList(self, read_all_patch, match_key_values_patch, *patches):
        match_key_values_patch.return_value = [
            {'name': 'repo1', 'key': 'value'},
            {'name': 'repo2', 'key': 'value'},
            {'name': 'repo3', 'key': 'value'},
            {'name': 'repo4', 'key': 'value'}
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.get_repos(organization='edgexfoundry', regex=r'^test_us6379-.*$', archived=False, disabled=False, blacklist_repos=['repo2', 'repo4'])
        read_all_patch.assert_called_once_with('/orgs/edgexfoundry/repos')
        expected_result = ['repo1', 'repo3']
        self.assertEqual(result, expected_result)

    @patch('githubsync.GitHubAPI.read')
    def test__get_labels_Should_CallExpected_When_Called(self, read_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.get_labels('edgexfoundry/cd-management')
        read_patch.assert_called_once_with(
            '/repos/edgexfoundry/cd-management/labels',
            attributes=[
                'name',
                'description',
                'color'
            ])
        self.assertEqual(result, read_patch.return_value)

    @patch('githubsync.GitHubAPI.read')
    def test__get_milestones_Should_CallExpected_When_Called(self, read_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.get_milestones('edgexfoundry/cd-management')
        read_patch.assert_called_once_with(
            '/repos/edgexfoundry/cd-management/milestones',
            attributes=[
                'number',
                'title',
                'state',
                'description',
                'due_on'
            ])
        self.assertEqual(result, read_patch.return_value)

    @patch('githubsync.GitHubAPI.ratelimit_request')
    def test__exists_Should_CallExpected_When_Called(self, ratelimit_request_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones/1'
        client.exists(endpoint)
        ratelimit_request_patch.assert_called_once_with(client.get, endpoint, raw_response=True)

    @patch('githubsync.GitHubAPI.ratelimit_request')
    def test__exists_Should_ReturnTrue_When_Exists(self, ratelimit_request_patch, *patches):
        ratelimit_request_patch.return_value = Mock()
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones/1'
        result = client.exists(endpoint)
        self.assertTrue(result)

    @patch('githubsync.GitHubAPI.ratelimit_request')
    def test__exists_Should_ReturnFalse_When_ExceptionStatusCodeIs404(self, ratelimit_request_patch, *patches):
        response_mock = Mock(status_code=404)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        ratelimit_request_patch.side_effect = http_error_mock
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones/1'
        result = client.exists(endpoint)
        self.assertFalse(result)

    @patch('githubsync.GitHubAPI.ratelimit_request')
    def test__exists_Should_RaiseError_When_ExceptionStatusCodeIsNot404(self, ratelimit_request_patch, *patches):
        response_mock = Mock(status_code=401)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        ratelimit_request_patch.side_effect = http_error_mock
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones/1'
        with self.assertRaises(HTTPError):
            client.exists(endpoint)

    @patch('githubsync.GitHubAPI.ratelimit_request')
    def test__modify_Should_CallExpected_When_Called(self, ratelimit_request_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        endpoint = '/repos/soda480/testrepo1/milestones/1'
        payload = {'key': 'value'}
        client.modify(endpoint, payload, noop=False)
        ratelimit_request_patch.assert_called_once_with(client.patch, endpoint, json=payload, noop=False)

    @patch('githubsync.GitHubAPI.ratelimit_request')
    def test__create_Should_CallExpected_When_Called(self, ratelimit_request_patch, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        endpoint = '/repos/soda480/testrepo1/milestones/1'
        payload = {'key': 'value'}
        client.create(endpoint, payload, resource_id='key', noop=False)
        ratelimit_request_patch.assert_called_once_with(client.post, endpoint, json=payload, noop=False)

    @patch('githubsync.GitHubAPI.create')
    @patch('githubsync.GitHubAPI.modify')
    @patch('githubsync.GitHubAPI.modified_since')
    @patch('githubsync.GitHubAPI.exists')
    def test__sync_labels_Should_CallExpected_When_Called(self, exists_patch, modified_since_patch, modify_patch, create_patch, *patches):
        exists_patch.side_effect = [
            False,
            True,
            True
        ]
        modified_since_patch.side_effect = [
            True,
            False
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        labels = [
            {'name': 'label1'},
            {'name': 'label2'},
            {'name': 'label3'}
        ]
        client.sync_labels('soda480/repo1', labels, 'edgexfoundry/cd-management', modified_since='Wed, 06 May 2020 18:21:45 GMT', noop=False)
        modify_patch.assert_called_once_with('/repos/soda480/repo1/labels/label2', {'name': 'label2'}, noop=False)
        create_patch.assert_called_once_with('/repos/soda480/repo1/labels', {'name': 'label1'}, 'name', noop=False)

    @patch('githubsync.GitHubAPI.create')
    @patch('githubsync.GitHubAPI.get_milestones')
    def test__sync_milestones_Should_CallCreate_When_MilestoneDoesNotExistOnTarget(self, get_milestones_patch, create_patch, *patches):
        get_milestones_patch.return_value = [
            {'title': 'California', 'number': 1, 'description': 'California description'},
            {'title': 'Delhi', 'number': 2, 'description': 'Delhi description'},
            {'title': 'Geneva', 'number': 3, 'description': 'Geneva description'}
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        milestones = [
            {'title': 'Hanoi', 'number': 1, 'description': 'Hanoi description', 'due_on': '2020-10-01T07:00:00Z'},
            {'title': 'Enjambre', 'number': 2, 'description': 'Enjambre description', 'due_on': None}
        ]
        client.sync_milestones('soda480/repo1', milestones, 'edgexfoundry/cd-management', modified_since='Wed, 06 May 2020 18:21:45 GMT', noop=False)
        create_call1 = call(
            '/repos/soda480/repo1/milestones',
            {
                'title': 'Hanoi',
                'description': 'Hanoi description',
                'due_on': '2020-10-01T07:00:00Z'
            },
            'title',
            noop=False)
        create_call2 = call(
            '/repos/soda480/repo1/milestones',
            {
                'title': 'Enjambre',
                'description': 'Enjambre description'
            },
            'title',
            noop=False)
        self.assertTrue(create_call1 in create_patch.mock_calls)
        self.assertTrue(create_call2 in create_patch.mock_calls)

    @patch('githubsync.GitHubAPI.modify')
    @patch('githubsync.GitHubAPI.modified_since')
    @patch('githubsync.GitHubAPI.get_milestones')
    def test__sync_milestones_Should_CallModify_When_MilestoneExistOnTargetAndHasBeenModifiedOnSource(self, get_milestones_patch, modified_since_patch, modify_patch, *patches):
        get_milestones_patch.return_value = [
            {'title': 'California', 'number': 1, 'description': 'California description'},
            {'title': 'Delhi', 'number': 2, 'description': 'Delhi description'},
            {'title': 'Geneva', 'number': 3, 'description': 'Geneva description'},
            {'title': 'Hanoi', 'number': 4, 'description': 'Hanoi description', 'due_on': '2020-10-01T07:00:00Z'},
            {'title': 'Enjambre', 'number': 5, 'description': 'Enjambre description', 'due_on': None}
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        milestones = [
            {'title': 'Hanoi', 'number': 1, 'description': 'Hanoi description', 'due_on': '2020-11-01T00:00:00Z'},
            {'title': 'Enjambre', 'number': 2, 'description': 'Enjambre updated description', 'due_on': None},
            {'title': 'Geneva', 'number': 3, 'description': 'Geneva description'}
        ]
        modified_since_patch.side_effect = [
            True,
            True,
            False
        ]
        client.sync_milestones('soda480/repo1', milestones, 'edgexfoundry/cd-management', modified_since='Wed, 06 May 2020 18:21:45 GMT', noop=False)
        modify_call1 = call(
            '/repos/soda480/repo1/milestones/4',
            {
                'title': 'Hanoi',
                'description': 'Hanoi description',
                'due_on': '2020-11-01T00:00:00Z'
            },
            resource_id='Hanoi',
            noop=False)
        modify_call2 = call(
            '/repos/soda480/repo1/milestones/5',
            {
                'title': 'Enjambre',
                'description': 'Enjambre updated description',
                'due_on': None
            },
            resource_id='Enjambre',
            noop=False)
        self.assertTrue(modify_call1 in modify_patch.mock_calls)
        self.assertTrue(modify_call2 in modify_patch.mock_calls)

    @patch('githubsync.GitHubAPI.sync_milestones')
    @patch('githubsync.GitHubAPI.sync_labels')
    @patch('githubsync.GitHubAPI.get_milestones')
    @patch('githubsync.GitHubAPI.get_labels')
    @patch('githubsync.GitHubAPI.get_repos')
    def test__sync_repos_Should_CallExpected_When_Called(self, get_repos_patch, get_labels_patch, get_milestones_patch, sync_labels_patch, sync_milestones_patch, *patches):
        get_repos_patch.return_value = [
            'repo1',
            'repo2',
            'repo3'
        ]
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        client.sync_repos('edgexfoundry/cd-management', organization='edgexfoundry', regex='some-regex', blacklist_repos=['repo3'], modified_since='modified-since', noop=False)
        sync_labels_call = call('edgexfoundry/repo1', get_labels_patch.return_value, 'edgexfoundry/cd-management', noop=False)
        sync_milestones_call = call('edgexfoundry/repo1', get_milestones_patch.return_value, 'edgexfoundry/cd-management', noop=False)
        self.assertTrue(sync_labels_call in sync_labels_patch.mock_calls)
        self.assertTrue(sync_milestones_call in sync_milestones_patch.mock_calls)

    def test__modified_since_Should_ReturnTrue_When_NoModifiedSince(self, *patches):
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        self.assertTrue(client.modified_since('endpoint', None))

    @patch('githubsync.GitHubAPI.get')
    def test__modified_since_Should_CallAndReturnExpected_When_Called(self, get_patch, *patches):
        get_patch.return_value = Mock(status_code=306)
        client = GitHubAPI('api.github.com', bearer_token='bearer-token')
        result = client.modified_since('endpoint', 'modified-since')
        get_patch.assert_called_once_with('endpoint', raw_response=True, headers={'If-Modified-Since': 'modified-since'})
        self.assertFalse(result)

    @patch('githubsync.api.getenv', return_value='token')
    @patch('githubsync.api.GitHubAPI')
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
