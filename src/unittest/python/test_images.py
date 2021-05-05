
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
import os
import json
from mock import patch
from mock import mock_open
from mock import call
from mock import Mock

from envbuilder import DockerImageSearch
from envbuilder.images import parse_args

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


class TestImages(unittest.TestCase):

    def setUp(self):
        # it is easier to use json dumps from DockerHub
        # rather than fabricate data here
        self.image_data = {}

        resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources')
        for filename in os.listdir(resources_dir):
            if filename.endswith('.json'):
                key = filename.replace('.json', '')
                with open(f'{resources_dir}/{filename}') as f:
                    data = json.load(f)
                    self.image_data[key] = data

    def tearDown(self):

        pass

    @patch('envbuilder.images.ArgumentParser')
    def test__parse_args_Should_ReturnExpected_When_Called(self, *patches):
        # not much to unit test here
        parse_args()

    @patch('envbuilder.images.DockerImageSearch.get')
    def test__get_image_versions_Should_ReturnExpected_When_NoImageGroupingIsUsed(self, get_patch, *patches):
        get_patch.return_value = self.image_data['mock1']

        search = DockerImageSearch()
        result = search.get_image_versions(repo='mock-repo', org='mock-org', filter='alpine')

        get_patch.assert_called_once_with(
            f'/v2/repositories/mock-org/mock-repo/tags/?page=1&page_size=100')

        expected = {'alpine': ['1.1.2-alpine', '1.1.1-alpine', '1.1.0-alpine', '1.0.2-alpine', '1.0.1-alpine', '1.0.0-alpine',
                               '0.9.1-alpine', '0.9.0-alpine', '0.5.1-alpine', '0.5.0-alpine', '0.4.2-alpine', '0.4.1-alpine', '0.4.0-alpine']}

        self.assertEqual(result, expected)

    @patch('envbuilder.images.DockerImageSearch.get')
    def test__get_image_versions_Should_ReturnExpected_When_ImagesAreGroupedByFilter(self, get_patch, *patches):
        get_patch.return_value = self.image_data['mock2']

        search = DockerImageSearch()
        result = search.get_image_versions(repo='mock-repo', filter='latest')

        get_patch.assert_called_once_with(
            f'/v2/repositories/library/mock-repo/tags/?page=1&page_size=100')

        expected = {'latest': ['focal-20210416', 'focal', '20.04']}

        self.assertEqual(result, expected)

    @patch('envbuilder.images.DockerImageSearch.get')
    def test__get_image_versions_Should_ReturnEmpty_When_ImageFilterDoesNotMatch(self, get_patch, *patches):
        get_patch.return_value = self.image_data['mock2']

        search = DockerImageSearch()
        result = search.get_image_versions(repo='mock-repo', filter='alpine')

        get_patch.assert_called_once_with(
            f'/v2/repositories/library/mock-repo/tags/?page=1&page_size=100')

        expected = {'alpine': []}

        self.assertEqual(result, expected)
