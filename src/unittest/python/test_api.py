
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

from prunetags import API

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

    def test__init__Should_RaiseValueError_When_NoBearerToken(self, *patches):
        with self.assertRaises(ValueError):
            API()

    @patch('prunetags.API.match_repos')
    @patch('prunetags.API.get')
    def test__get_repos_Should_CallAndReturnExpected_When_UserRegexAttributes(self, get_patch, match_repos_patch, *patches):
        client = API(bearer_token='bearer-token')
        result = client.get_repos(user='soda480', include=r'^test_repo.*$', archived=False, disabled=False)
        get_patch.assert_called_once_with('/users/soda480/repos', _get='all')
        match_repos_patch.assert_called_once_with(
            repos=get_patch.return_value,
            owner='soda480',
            include='^test_repo.*$',
            exclude=None,
            archived=False,
            disabled=False)
        self.assertEqual(result, match_repos_patch.return_value)

    @patch('prunetags.API.match_repos')
    @patch('prunetags.API.get')
    def test__get_repos_Should_CallAndReturnExpected_When_OrganizationExcludeAttributes(self, get_patch, match_repos_patch, *patches):
        client = API(bearer_token='bearer-token')
        result = client.get_repos(organization='org1', exclude=['repo1', 'repo2'], archived=False, disabled=False)
        get_patch.assert_called_once_with('/orgs/org1/repos', _get='all')
        match_repos_patch.assert_called_once_with(
            repos=get_patch.return_value,
            owner='org1',
            include=None,
            exclude=['repo1', 'repo2'],
            archived=False,
            disabled=False)
        self.assertEqual(result, match_repos_patch.return_value)

    @patch('prunetags.API.get_version')
    @patch('prunetags.API.lookup_tag')
    @patch('prunetags.API.get')
    def test__get_latest_version_Should_CallAndReturnExpected_When_Called(self, get_patch, lookup_tag_patch, get_version_patch, *patches):
        get_patch.return_value = [
            [{'sha': '-sha1-'}, {'sha': '-sha2-'}, {'sha': '-sha3-'}]
        ]
        client = API(bearer_token='bearer-token')
        tags = ['tag1', 'tag2']
        result = client.get_latest_version(repo='soda480/repo1', tags=tags)
        self.assertEqual(result, (get_version_patch.return_value, '-sha1-'))
        get_patch.assert_called_once_with('/repos/soda480/repo1/commits?sha=main', _get='page')
        lookup_tag_patch.assert_called_with(tags=tags, sha='-sha1-')

    @patch('prunetags.API.get_version')
    @patch('prunetags.API.lookup_tag')
    @patch('prunetags.API.get')
    def test__get_latest_version_Should_ReturnExpected_When_NoTagFound(self, get_patch, lookup_tag_patch, get_version_patch, *patches):
        get_patch.return_value = [
            [{'sha': '-sha1-'}, {'sha': '-sha2-'}, {'sha': '-sha3-'}]
        ]
        lookup_tag_patch.side_effect = [
            None,
            None,
            None
        ]
        client = API(bearer_token='bearer-token')
        tags = ['tag1', 'tag2']
        result = client.get_latest_version(repo='soda480/repo1', tags=tags)
        self.assertEqual(result, (None, None))

    @patch('prunetags.API.get_latest_version')
    @patch('prunetags.API.get')
    def test__get_prerelease_tags_Should_Return_When_NoTags(self, get_patch, get_latest_version_patch, *patches):
        get_patch.return_value = []
        client = API(bearer_token='bearer-token')
        client.get_prerelease_tags(repo='org1/repo1', branch='master')
        get_latest_version_patch.assert_not_called()

    @patch('prunetags.API.get')
    @patch('prunetags.API.filter_prerelease_tags')
    @patch('prunetags.API.get_latest_version')
    def test__get_prerelease_tags_Should_Return_When_NoLatestTagVersion(self, get_latest_version_patch, filter_prerelease_tags_patch, *patches):
        get_latest_version_patch.return_value = (None, None)
        client = API(bearer_token='bearer-token')
        client.get_prerelease_tags(repo='org1/repo1', branch='master')
        filter_prerelease_tags_patch.assert_not_called()

    @patch('prunetags.API.get')
    @patch('prunetags.API.filter_prerelease_tags')
    @patch('prunetags.API.get_latest_version')
    def test__get_prerelease_tags_Should_CallAndReturnExpected_When_Called(self, get_latest_version_patch, filter_prerelease_tags_patch, *patches):
        get_latest_version_patch.return_value = Version('1.2.3-dev.1'), 'sha0'
        client = API(bearer_token='bearer-token')
        result = client.get_prerelease_tags(repo='org1/repo1', branch='master')
        expected_result = (filter_prerelease_tags_patch.return_value, Version('1.2.3-dev.1'), 'sha0')
        self.assertEqual(result, expected_result)

    @patch('prunetags.API.generate_preprelease_report')
    @patch('prunetags.API.get_prerelease_tags')
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
        client = API(bearer_token='bearer-token')
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
        result = API.generate_preprelease_report(repo='soda480/repo1', prerelease_tags=prerelease_tags, latest_version=Version('1.2.3'), latest_version_sha='sha0')
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

    def test__generate_version_report_Should_ReturnExpected_When_Called(self, *patches):
        tags = [
            ('v1.2.4', 'sha3'),
            ('v1.2.3', 'sha2'),
            ('v1.2.2', 'sha1')
        ]
        result = API.generate_version_report(repo='repo1', version_tags=tags, latest_version=Version('1.2.4'), latest_version_sha='sha0')
        expected_result = {
            'repo1': {
                'latest_version': ('1.2.4', 'sha0'),
                'version_tags': [
                    ('v1.2.4', 'sha3'),
                    ('v1.2.3', 'sha2'),
                    ('v1.2.2', 'sha1')
                ],
                'version_tags_count': 3
            }
        }
        self.assertEqual(result, expected_result)

    @patch('prunetags.API.delete')
    @patch('prunetags.API.get_prerelease_tags')
    def test__remove_prerelease_tags_Should_Return_When_NoTags(self, get_prerelease_tags_patch, delete_patch, *patches):
        get_prerelease_tags_patch.return_value = None
        client = API(bearer_token='bearer-token')
        client.remove_prerelease_tags(repo='org1/repo1', branch='master', noop=False)
        delete_patch.assert_not_called()

    @patch('prunetags.api.sleep')
    @patch('prunetags.API.delete')
    @patch('prunetags.API.get_prerelease_tags')
    def test__remove_prerelease_tags_Should_CallExpected_When_Called(self, get_prerelease_tags_patch, delete_patch, *patches):
        get_prerelease_tags_patch.return_value = (
            [('tag1', 'sha1'), ('tag2', 'sha2')], '-latest-version-', '-latest-version-sha-'
        )
        client = API(bearer_token='bearer-token')
        client.remove_prerelease_tags(repo='org1/repo1', branch='master', noop=True)
        delete_patch.assert_called_with('/repos/org1/repo1/git/refs/tags/tag2', noop=True)

    @patch('prunetags.api.sleep')
    @patch('prunetags.api.logger')
    @patch('prunetags.API.delete')
    @patch('prunetags.API.get_prerelease_tags')
    def test__remove_prerelease_tags_Should_LogErrorAndContinue_When_Exception(self, get_prerelease_tags_patch, delete_patch, logger_patch, *patches):
        get_prerelease_tags_patch.return_value = (
            [('tag1', 'sha1'), ('tag2', 'sha2')], '-latest-version-', '-latest-version-sha-'
        )
        delete_patch.side_effect = [
            Exception('request error'),
            None
        ]
        client = API(bearer_token='bearer-token')
        client.remove_prerelease_tags(repo='org1/repo1', branch='master', noop=True)
        delete_patch.assert_called_with('/repos/org1/repo1/git/refs/tags/tag2', noop=True)
        logger_patch.error.assert_called_with('error occurred removing tag tag1 from repo org1/repo1: request error')

    def test__match_repos_Should_ReturnExpected_When_Called(self, *patches):
        repos = [
            {'name': 'repo1'},
            {'name': 'test_repo1', 'key1': 'value1'},
            {'name': 'repo2'},
            {'name': 'test_repo2', 'key1': 'value1', 'key2': 'value2'}
        ]
        result = API.match_repos(repos=repos, owner='soda480', include=r'^test_repo.*$', exclude='test_repo2', key1='value1')
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
        result = API.match_repos(repos=repos, owner='soda480', include=None, exclude=None, key1='value1')
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
        result = API.lookup_tag(tags=tags, sha='sha1')
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
        result = API.filter_prerelease_tags(tags=tags, exclude=Version('1.2.2'))
        expected_result = [
            ('v1.2.0-dev.1', 'sha5'),
            ('v1.1.4-dev.1', 'sha7')
        ]
        self.assertEqual(result, expected_result)

    def test__filter_version_tags_Should_Return_Expected_When_Called(self, *patches):
        tags = [
            {'name': 'v1.2.4', 'commit': {'sha': 'sha1'}},
            {'name': 'v1.2.3-dev.1', 'commit': {'sha': 'sha2'}},
            {'name': 'v1.2.2', 'commit': {'sha': 'sha3'}},
            {'name': 'v1.2.1', 'commit': {'sha': 'sha4'}},
            {'name': 'v1.2.0-dev.1', 'commit': {'sha': 'sha5'}},
            {'name': 'v1.1.9', 'commit': {'sha': 'sha6'}},
            {'name': 'v1.1.4-dev.1', 'commit': {'sha': 'sha7'}}
        ]
        result = API.filter_version_tags(
            tags=tags,
            exclude=None,
            expression='<=1.2.1')
        expected_result = [
            ('v1.2.1', 'sha4'),
            ('v1.2.0-dev.1', 'sha5'),
            ('v1.1.9', 'sha6'),
            ('v1.1.4-dev.1', 'sha7')
        ]
        self.assertEqual(result, expected_result)

    def test__filter_version_tags_Should_Return_Expected_When_Called_With_Range(self, *patches):
        tags = [
            {'name': 'v1.2.4', 'commit': {'sha': 'sha1'}},
            {'name': 'v1.2.3-dev.1', 'commit': {'sha': 'sha2'}},
            {'name': 'v1.2.2', 'commit': {'sha': 'sha3'}},
            {'name': 'v1.2.1', 'commit': {'sha': 'sha4'}},
            {'name': 'v1.2.0-dev.1', 'commit': {'sha': 'sha5'}},
            {'name': 'v1.1.9', 'commit': {'sha': 'sha6'}},
            {'name': 'v1.1.4-dev.1', 'commit': {'sha': 'sha7'}}
        ]
        result = API.filter_version_tags(
            tags=tags,
            exclude=Version('1.2.3-dev.2'),
            expression='<1.2.4,>1.1.4')
        expected_result = [
            ('v1.2.3-dev.1', 'sha2'),
            ('v1.2.2', 'sha3'),
            ('v1.2.1', 'sha4'),
            ('v1.2.0-dev.1', 'sha5'),
            ('v1.1.9', 'sha6')
        ]
        self.assertEqual(result, expected_result)

    @patch('prunetags.api.validate_version', return_value=False)
    def test__get_version_Should_ReturnExpected_When_Called(self, *patches):
        result = API.get_version(name='enjambre')
        self.assertIsNone(result)

    @patch('prunetags.API.delete')
    @patch('prunetags.API.get_version_tags')
    def test__remove_version_tags_Should_Return_When_NoTags(self, get_version_tags_patch, delete_patch, *patches):
        get_version_tags_patch.return_value = None
        client = API(bearer_token='bearer-token')
        client.remove_version_tags(repo='org1/repo1', branch='master', noop=False)
        delete_patch.assert_not_called()

    @patch('prunetags.api.sleep')
    @patch('prunetags.API.delete')
    @patch('prunetags.API.get_version_tags')
    def test__remove_version_tags_Should_CallExpected_When_Called(self, get_version_tags_patch, delete_patch, *patches):
        get_version_tags_patch.return_value = (
            [('tag1', 'sha1'), ('tag2', 'sha2')], '-latest-version-', '-latest-version-sha-'
        )
        client = API(bearer_token='bearer-token')
        client.remove_version_tags(repo='org1/repo1', branch='master', noop=True)
        delete_patch.assert_called_with('/repos/org1/repo1/git/refs/tags/tag2', noop=True)

    @patch('prunetags.api.sleep')
    @patch('prunetags.api.logger')
    @patch('prunetags.API.delete')
    @patch('prunetags.API.get_version_tags')
    def test__remove_version_tags_Should_LogErrorAndContinue_When_Exception(self, get_version_tags_patch, delete_patch, logger_patch, *patches):
        get_version_tags_patch.return_value = (
            [('tag1', 'sha1'), ('tag2', 'sha2')], '-latest-version-', '-latest-version-sha-'
        )
        delete_patch.side_effect = [
            Exception('request error'),
            None
        ]
        client = API(bearer_token='bearer-token')
        client.remove_version_tags(repo='org1/repo1', branch='master', noop=True)
        delete_patch.assert_called_with('/repos/org1/repo1/git/refs/tags/tag2', noop=True)
        logger_patch.error.assert_called_with('error occurred removing tag tag1 from repo org1/repo1: request error')

    @patch('prunetags.API.get_latest_version')
    @patch('prunetags.API.get')
    def test__get_version_tags_Should_Return_When_NoTags(self, get_patch, get_latest_version_patch, *patches):
        get_patch.return_value = []
        client = API(bearer_token='bearer-token')
        client.get_version_tags(repo='org1/repo1', branch='master')
        get_latest_version_patch.assert_not_called()

    @patch('prunetags.API.get')
    @patch('prunetags.API.filter_prerelease_tags')
    @patch('prunetags.API.get_latest_version')
    def test__get_version_tags_Should_Return_When_NoLatestTagVersion(self, get_latest_version_patch, filter_version_tags_patch, *patches):
        get_latest_version_patch.return_value = (None, None)
        client = API(bearer_token='bearer-token')
        client.get_version_tags(repo='org1/repo1', branch='master')
        filter_version_tags_patch.assert_not_called()

    @patch('prunetags.API.get')
    @patch('prunetags.API.filter_version_tags')
    @patch('prunetags.API.get_latest_version')
    def test__get_version_tags_Should_CallAndReturnExpected_When_Called(self, get_latest_version_patch, filter_version_tags_patch, *patches):
        get_latest_version_patch.return_value = Version('1.2.3-dev.1'), 'sha0'
        client = API(bearer_token='bearer-token')
        result = client.get_version_tags(repo='org1/repo1', branch='master')
        expected_result = (filter_version_tags_patch.return_value, Version('1.2.3-dev.1'), 'sha0')
        self.assertEqual(result, expected_result)

    @patch('prunetags.API.generate_version_report')
    @patch('prunetags.API.get_version_tags')
    def test__get_version_tags_report_Should_ReturnExpected_When_Called(self, get_version_tags_patch, generate_version_report, *patches):
        get_version_tags_patch.side_effect = [
            ('-tags-', '-latest-version-', '-latest-version-sha-'),
            None,
            ('-tags-', '-latest-version-', '-latest-version-sha-'),
        ]
        generate_version_report.side_effect = [
            {'repo1': {}},
            {'repo3': {}}
        ]
        client = API(bearer_token='bearer-token')
        repos = [
            'repo1',
            'repo2',
            'repo3'
        ]
        expression = '<=1.1.1'
        result = client.get_version_tags_report(repos=repos, expression=expression)
        expected_result = {
            'repo1': {},
            'repo2': {},
            'repo3': {}
        }
        self.assertEqual(result, expected_result)

    @patch('prunetags.api.logger')
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

    def test__retry_connection_error_Should_Return_True_When_ConnectionError(self, *patches):

        self.assertTrue(API.retry_connection_error(ConnectionError('test')))
