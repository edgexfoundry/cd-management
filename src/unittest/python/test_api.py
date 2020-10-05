
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

from synclabels import API

from datetime import datetime
from requests.exceptions import SSLError
from requests.exceptions import HTTPError
from requests.exceptions import ProxyError

import sys
import logging
logger = logging.getLogger(__name__)

consoleHandler = logging.StreamHandler(sys.stdout)
logFormatter = logging.Formatter("%(asctime)s %(threadName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
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
        result = API.match_key_values(self.items, regex, key1='value1', key3='value3')
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

    @patch('synclabels.api.logger')
    def test__log_ratelimit_Should_LogExpected_When_Header(self, logger_patch, *patches):
        ratelimit = {
            'minutes': '32',
            'remaining': '4999',
            'limit': '5000'
        }
        API.log_ratelimit(ratelimit)
        logger_patch.info.assert_called_with('4999/5000 resets in 32 min')

    def test__retry_connection_error_Should_Return_False_When_NoMatch(self, *patches):
        response_mock = Mock(status_code=404)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        self.assertFalse(API.retry_connection_error(http_error_mock))

    def test__retry_connection_error_Should_Return_True_When_SSLError(self, *patches):

        self.assertTrue(API.retry_connection_error(SSLError('test')))

    def test__retry_connection_error_Should_Return_True_When_ProxyError(self, *patches):

        self.assertTrue(API.retry_connection_error(ProxyError('test')))

    def test__get_resource_id_Should_ReturnExpected_When_Called(self, *patches):
        endpoint = '/repos/:owner/:repo/labels/label1'
        result = API.get_resource_id(endpoint)
        self.assertEqual(result, 'label1')

    def test__get_resource_Should_ReturnExpected_When_Called(self, *patches):
        endpoint = '/repos/:owner/:repo/labels/label1'
        result = API.get_resource(endpoint)
        self.assertEqual(result, 'label')

    def test__get_resource_Should_ReturnExpected_When_CalledWithIndex(self, *patches):
        endpoint = '/repos/:owner/:repo/labels'
        result = API.get_resource(endpoint, index=-1)
        self.assertEqual(result, 'label')

    def test__get_owner_repo_Should_ReturnExpected_When_Called(self, *patches):
        endpoint = '/repos/:owner/:repo/labels/label1'
        result = API.get_owner_repo(endpoint)
        self.assertEqual(result, ':owner/:repo')

    def test__get_gmt_time_Should_ReturnNone_When_NoDelta(self, *patches):

        self.assertIsNone(API.get_gmt_time(None))

    def test__get_gmt_time_Should_RaiseValueError_When_NoMatch(self, *patches):
        with self.assertRaises(ValueError):
            API.get_gmt_time('200 days')

    @patch('synclabels.api.datetime')
    def test__get_gmt_time_Should_ReturnExpected_When_CalledWithDays(self, datetime_patch, *patches):
        datetime_patch.now.return_value = datetime(2020, 5, 6, 18, 22, 45, 12065)
        result = API.get_gmt_time('1d')
        expected_result = 'Tue, 05 May 2020 18:22:45 '
        self.assertEqual(result, expected_result)

    @patch('synclabels.api.datetime')
    def test__get_gmt_time_Should_ReturnExpected_When_CalledWithHours(self, datetime_patch, *patches):
        datetime_patch.now.return_value = datetime(2020, 5, 6, 18, 22, 45, 12065)
        result = API.get_gmt_time('1h')
        expected_result = 'Wed, 06 May 2020 17:22:45 '
        self.assertEqual(result, expected_result)

    @patch('synclabels.api.datetime')
    def test__get_gmt_time_Should_ReturnExpected_When_CalledWithMinutes(self, datetime_patch, *patches):
        datetime_patch.now.return_value = datetime(2020, 5, 6, 18, 22, 45, 12065)
        result = API.get_gmt_time('1m')
        expected_result = 'Wed, 06 May 2020 18:21:45 '
        self.assertEqual(result, expected_result)

    def test__init__Should_RaiseValueError_When_NoBearerToken(self, *patches):
        with self.assertRaises(ValueError):
            API()

    @patch('synclabels.API.get')
    def test__get_repos_Should_ReturnRepos_When_UserAndNoRegexAndAttributes(self, get_patch, *patches):
        client = API(bearer_token='bearer-token')
        result = client.get_repos(user='soda480')
        get_patch.assert_called_once_with('/users/soda480/repos', _get='all')
        self.assertEqual(result, get_patch.return_value)

    @patch('synclabels.API.match_key_values')
    @patch('synclabels.API.get')
    def test__get_repos_Should_ReturnRepos_When_OrganizationAndRegexAndAttributesAndBlackList(self, get_patch, match_key_values_patch, *patches):
        match_key_values_patch.return_value = [
            {'name': 'repo1', 'key': 'value'},
            {'name': 'repo2', 'key': 'value'},
            {'name': 'repo3', 'key': 'value'},
            {'name': 'repo4', 'key': 'value'}
        ]
        client = API(bearer_token='bearer-token')
        result = client.get_repos(organization='edgexfoundry', regex=r'^test_us6379-.*$', archived=False, disabled=False, exclude_repos=['repo2', 'repo4'])
        get_patch.assert_called_once_with('/orgs/edgexfoundry/repos', _get='all')
        expected_result = ['repo1', 'repo3']
        self.assertEqual(result, expected_result)

    @patch('synclabels.API.get')
    def test__get_labels_Should_CallExpected_When_Called(self, get_patch, *patches):
        client = API(bearer_token='bearer-token')
        result = client.get_labels('edgexfoundry/cd-management')
        get_patch.assert_called_once_with(
            '/repos/edgexfoundry/cd-management/labels',
            _get='all',
            _attributes=[
                'name',
                'description',
                'color'
            ])
        self.assertEqual(result, get_patch.return_value)

    @patch('synclabels.API.get')
    def test__get_milestones_Should_CallExpected_When_Called(self, get_patch, *patches):
        client = API(bearer_token='bearer-token')
        result = client.get_milestones('edgexfoundry/cd-management')
        get_patch.assert_called_once_with(
            '/repos/edgexfoundry/cd-management/milestones',
            _get='all',
            _attributes=[
                'number',
                'title',
                'state',
                'description',
                'due_on'
            ])
        self.assertEqual(result, get_patch.return_value)

    @patch('synclabels.API.get')
    def test__exists_Should_CallExpected_When_Called(self, get_patch, *patches):
        client = API(bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones/1'
        client.exists(endpoint)
        get_patch.assert_called_once_with(endpoint, raw_response=True)

    @patch('synclabels.API.get')
    def test__exists_Should_ReturnTrue_When_Exists(self, get_patch, *patches):
        get_patch.return_value = Mock()
        client = API(bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones/1'
        result = client.exists(endpoint)
        self.assertTrue(result)

    @patch('synclabels.API.get')
    def test__exists_Should_ReturnFalse_When_ExceptionStatusCodeIs404(self, get_patch, *patches):
        response_mock = Mock(status_code=404)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        get_patch.side_effect = http_error_mock
        client = API(bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones/1'
        result = client.exists(endpoint)
        self.assertFalse(result)

    @patch('synclabels.API.get')
    def test__exists_Should_RaiseError_When_ExceptionStatusCodeIsNot404(self, get_patch, *patches):
        response_mock = Mock(status_code=401)
        http_error_mock = HTTPError(Mock())
        http_error_mock.response = response_mock
        get_patch.side_effect = http_error_mock
        client = API(bearer_token='bearer-token')
        endpoint = '/repos/edgexfoundry/cd-management/milestones/1'
        with self.assertRaises(HTTPError):
            client.exists(endpoint)

    @patch('synclabels.API.patch')
    def test__modify_Should_CallExpected_When_Called(self, patch_patch, *patches):
        client = API(bearer_token='bearer-token')
        endpoint = '/repos/soda480/testrepo1/milestones/1'
        payload = {'key': 'value'}
        client.modify(endpoint, payload, noop=False)
        patch_patch.assert_called_once_with(endpoint, json=payload, noop=False)

    @patch('synclabels.API.post')
    def test__create_Should_CallExpected_When_Called(self, post_patch, *patches):
        client = API(bearer_token='bearer-token')
        endpoint = '/repos/soda480/testrepo1/milestones/1'
        payload = {'key': 'value'}
        client.create(endpoint, payload, resource_id='key', noop=False)
        post_patch.assert_called_once_with(endpoint, json=payload, noop=False)

    @patch('synclabels.API.create')
    @patch('synclabels.API.modify')
    @patch('synclabels.API.modified_since')
    @patch('synclabels.API.exists')
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
        client = API(bearer_token='bearer-token')
        labels = [
            {'name': 'label1'},
            {'name': 'label2'},
            {'name': 'label3'}
        ]
        client.sync_labels('soda480/repo1', labels, 'edgexfoundry/cd-management', modified_since='Wed, 06 May 2020 18:21:45 GMT', noop=False)
        modify_patch.assert_called_once_with('/repos/soda480/repo1/labels/label2', {'name': 'label2'}, noop=False)
        create_patch.assert_called_once_with('/repos/soda480/repo1/labels', {'name': 'label1'}, 'name', noop=False)

    @patch('synclabels.API.create')
    @patch('synclabels.API.get_milestones')
    def test__sync_milestones_Should_CallCreate_When_MilestoneDoesNotExistOnTarget(self, get_milestones_patch, create_patch, *patches):
        get_milestones_patch.return_value = [
            {'title': 'California', 'number': 1, 'description': 'California description'},
            {'title': 'Delhi', 'number': 2, 'description': 'Delhi description'},
            {'title': 'Geneva', 'number': 3, 'description': 'Geneva description'}
        ]
        client = API(bearer_token='bearer-token')
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

    @patch('synclabels.API.modify')
    @patch('synclabels.API.modified_since')
    @patch('synclabels.API.get_milestones')
    def test__sync_milestones_Should_CallModify_When_MilestoneExistOnTargetAndHasBeenModifiedOnSource(self, get_milestones_patch, modified_since_patch, modify_patch, *patches):
        get_milestones_patch.return_value = [
            {'title': 'California', 'number': 1, 'description': 'California description'},
            {'title': 'Delhi', 'number': 2, 'description': 'Delhi description'},
            {'title': 'Geneva', 'number': 3, 'description': 'Geneva description'},
            {'title': 'Hanoi', 'number': 4, 'description': 'Hanoi description', 'due_on': '2020-10-01T07:00:00Z'},
            {'title': 'Enjambre', 'number': 5, 'description': 'Enjambre description', 'due_on': None}
        ]
        client = API(bearer_token='bearer-token')
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

    @patch('synclabels.API.sync_milestones')
    @patch('synclabels.API.sync_labels')
    @patch('synclabels.API.get_milestones')
    @patch('synclabels.API.get_labels')
    @patch('synclabels.API.get_repos')
    def test__sync_repos_Should_CallExpected_When_Called(self, get_repos_patch, get_labels_patch, get_milestones_patch, sync_labels_patch, sync_milestones_patch, *patches):
        get_repos_patch.return_value = [
            'repo1',
            'repo2',
            'repo3'
        ]
        client = API(bearer_token='bearer-token')
        client.sync_repos('edgexfoundry/cd-management', organization='edgexfoundry', regex='some-regex', exclude_repos=['repo3'], modified_since='modified-since', noop=False)
        sync_labels_call = call('edgexfoundry/repo1', get_labels_patch.return_value, 'edgexfoundry/cd-management', noop=False)
        sync_milestones_call = call('edgexfoundry/repo1', get_milestones_patch.return_value, 'edgexfoundry/cd-management', noop=False)
        self.assertTrue(sync_labels_call in sync_labels_patch.mock_calls)
        self.assertTrue(sync_milestones_call in sync_milestones_patch.mock_calls)

    def test__modified_since_Should_ReturnTrue_When_NoModifiedSince(self, *patches):
        client = API(bearer_token='bearer-token')
        self.assertTrue(client.modified_since('endpoint', None))

    @patch('synclabels.API.get')
    def test__modified_since_Should_CallAndReturnExpected_When_Called(self, get_patch, *patches):
        get_patch.return_value = Mock(status_code=306)
        client = API(bearer_token='bearer-token')
        result = client.modified_since('endpoint', 'modified-since')
        get_patch.assert_called_once_with('endpoint', raw_response=True, headers={'If-Modified-Since': 'modified-since'})
        self.assertFalse(result)

    def test__search_Should_ReturnNone_When_NotFound(self, *patches):
        items = [{'name': 'zoe'}, {'name': 'enjambre'}]
        result = API.search(items, 'name', 'reyes')
        self.assertIsNone(result)

    def test__search_Should_ReturnExpected_When_Found(self, *patches):
        items = [{'name': 'zoe'}, {'name': 'enjambre'}]
        result = API.search(items, 'name', 'zoe')
        expected_result = {'name': 'zoe'}
        self.assertEqual(result, expected_result)

    def test__get_retries_Should_ReturnExpected_When_Called(self, *patches):
        client = API(bearer_token='bearer-token')
        expected_retries = [
            {
                'retry_on_exception': client.retry_connection_error,
                'wait_random_min': 10000,
                'wait_random_max': 20000,
                'stop_max_attempt_number': 6  
            }, {
                'retry_on_exception': client.retry_ratelimit_error,
                'stop_max_attempt_number': 60,
                'wait_fixed': 60000
            }
        ]
        print(client.retries)
        self.assertEqual(client.retries, expected_retries)
