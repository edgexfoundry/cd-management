
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

from cr8rel import API
from cr8rel.api import ReleaseAlreadyExists

from requests.exceptions import SSLError
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError

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

        pass

    def tearDown(self):

        pass

    def test__init_Should_RaiseValueError_When_NoBearerToken(self, *patches):
        with self.assertRaises(ValueError):
            API()

    @patch('cr8rel.api.API.upload_assets')
    @patch('cr8rel.api.API.create_release')
    def test__create_release_upload_assets_Should_CallExpected_When_Called(self, create_release_patch, upload_assets_patch, *patches):
        client = API(bearer_token='token')
        client.create_release_upload_assets('org1/repo1', 'v1.0.0', 'assets/')
        upload_assets_patch.assert_called_once_with('assets/', create_release_patch.return_value)

    @patch('cr8rel.api.API.get')
    def test__validate_release_Should_RaiseReleaseAlreadyExists_When_TagExists(self, get_patch, *patches):
        get_patch.return_value = [
            {'tag_name': 'v1.0.0'}
        ]
        client = API(bearer_token='token')
        with self.assertRaises(ReleaseAlreadyExists):
            client.validate_release('org1/repo1', 'v1.0.0', 'v1.0.0')

    @patch('cr8rel.api.API.get')
    def test__validate_release_Should_RaiseReleaseAlreadyExists_When_ReleaseExists(self, get_patch, *patches):
        get_patch.return_value = [
            {'tag_name': 'v1.0.1', 'name': 'v1.0.1'}
        ]
        client = API(bearer_token='token')
        with self.assertRaises(ReleaseAlreadyExists):
            client.validate_release('org1/repo1', 'v1.0.0', 'v1.0.1')

    @patch('cr8rel.api.API.validate_release')
    @patch('cr8rel.api.API.post')
    def test__create_release_Should_CallExpected_When_Called(self, post_patch, *patches):
        post_patch.return_value = {}
        client = API(bearer_token='token')
        result = client.create_release('org1/repo1', 'v1.0.0')
        post_patch.assert_called_once_with(
            '/repos/org1/repo1/releases',
            json={
                'tag_name': 'v1.0.0',
                'name': 'v1.0.0',
                'body': 'v1.0.0'
            })
        self.assertEqual(result['repo'], 'org1/repo1')

    @patch('cr8rel.api.API.upload_asset')
    @patch('cr8rel.api.API.get_assets')
    def test__upload_assets_Should_CallExpected_When_Called(self, get_assets_patch, upload_asset_patch, *patches):
        get_assets_patch.return_value = ['asset1', 'asset2']
        client = API(bearer_token='token')
        client.upload_assets('assets/', 'v1.0.0')
        upload_asset_call1 = call('asset1', 'v1.0.0')
        upload_asset_call2 = call('asset2', 'v1.0.0')
        self.assertTrue(upload_asset_call1 in upload_asset_patch.mock_calls)
        self.assertTrue(upload_asset_call2 in upload_asset_patch.mock_calls)

    @patch('cr8rel.api.API.get_upload_url')
    @patch('cr8rel.api.API.post')
    def test__upload_asset_Should_CallExpected_When_Called(self, post_patch, get_upload_url_patch, *patches):
        client = API(bearer_token='token')
        asset_mock = {
            'name': 'file.txt',
            'label': None,
            'content-type': 'text/plain',
            'content': 'content'
        }
        client.upload_asset(asset_mock, {'repo': 'org1/repo1', 'name': 'v1.0.0', 'upload_url': 'upload_url'})
        post_patch.assert_called_once_with(
            get_upload_url_patch.return_value,
            headers={'Content-Type': asset_mock['content-type']},
            data=asset_mock['content'])

    @patch('cr8rel.api.API.get_content', return_value='content')
    @patch('cr8rel.api.API.get_content_type', return_value='content-type')
    @patch('cr8rel.api.os.walk')
    def test__get_assets_Should_CallAndReturnExpected_When_Called(self, walk_patch, *patches):
        walk_patch.return_value = [
            ('', '', ['file1', 'file2'])
        ]
        result = API.get_assets('assets/')
        expected_result = [
            {'name': 'file1', 'label': None, 'content': 'content', 'content-type': 'content-type'},
            {'name': 'file2', 'label': None, 'content': 'content', 'content-type': 'content-type'}
        ]
        self.assertEqual(result, expected_result)

    @patch('cr8rel.api.URITemplate')
    def test__get_upload_url_Should_ReturnExpected_When_Called(self, uritemplate_patch, *patches):
        uritemplate_mock = Mock()
        uritemplate_patch.return_value = uritemplate_mock
        result = API.get_upload_url('template', 'name', 'label')
        self.assertEqual(result, uritemplate_mock.expand.return_value)

    @patch("builtins.open", new_callable=mock_open, read_data='data')
    def test__get_content_Should_ReturnExpected_When_Called(self, *patches):
        result = API.get_content('file')
        self.assertEqual(result, 'data')

    @patch('cr8rel.api.Magic')
    def test__get_content_type_Should_ReturnExpected_When_Exception(self, magic_patch, *patches):
        magic_patch.side_effect = Exception('some exception')
        result = API.get_content_type('file')
        expected_result = 'text/plain'
        self.assertEqual(result, expected_result)

    @patch('cr8rel.api.Magic')
    def test__get_content_type_Should_ReturnExpected_When_Called(self, magic_patch, *patches):
        result = API.get_content_type('file')
        self.assertEqual(result, magic_patch.return_value.from_file.return_value)

    def test__is_connection_error_Should_Return_False_When_NoMatch(self, *patches):

        self.assertFalse(API.is_connection_error(Exception('test')))

    def test__is_connection_error_Should_Return_True_When_SSLError(self, *patches):

        self.assertTrue(API.is_connection_error(SSLError('test')))

    def test__is_connection_error_Should_Return_True_When_ProxyError(self, *patches):

        self.assertTrue(API.is_connection_error(ProxyError('test')))

    def test__is_connection_error_Should_Return_True_When_ConnectionError(self, *patches):

        self.assertTrue(API.is_connection_error(ConnectionError('test')))
