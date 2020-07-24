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
from mock import Mock
from mock import MagicMock
from datetime import datetime


from dha.cli import get_parser
from dha.cli import configure_logging
from dha.cli import write_csv
from dha.cli import get_image_count
from dha.cli import get_all_images
from dha.cli import filter_image_list
from dha.cli import filter_tag_list
from dha.cli import get_all_tags
from dha.cli import get_tags
from argparse import ArgumentParser


class TestCLI(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('dha.cli.ArgumentParser.add_argument')
    @patch('dha.cli.ArgumentParser.parse_args')
    def test__get_args_Should_ReturnExpected_When_Called(
            self,
            parse_args_patch,
            *patches):
        parse_args_patch.return_value = 'parsed args'
        result = get_parser()
        self.assertIsInstance(result, ArgumentParser)

    @patch('dha.cli.logging')
    def test__configure_logging_Should_CallExpected_When_Called(
            self,
            logging_patch,
            *patches):
        args = Mock()
        root_logger_mock = Mock()
        logging_patch.getLogger.return_value = root_logger_mock
        configure_logging(args)
        root_logger_mock.addHandler.assert_called_once()

    @patch('dha.cli.logging')
    def test__configure_logging_Should_CallExpected_When_Called_With_Args(
            self,
            logging_patch,
            *patches):
        args = Mock()
        args.screen = None
        args.processes = 10
        root_logger_mock = Mock()
        logging_patch.getLogger.return_value = root_logger_mock
        configure_logging(args)
        self.assertEqual(root_logger_mock.addHandler.call_count, 2)

    @patch('dha.cli.datetime')
    @patch('dha.cli.open', create=True)
    def test__write_csv_Should_CallExpected_When_Called(
            self,
            open_patch,
            datetime_patch,
            *patches):
        datetime_patch.utcnow.return_value = datetime(2020, 7, 20, 11, 12, 13)
        name = "tags"
        images = [{"test1": "val1", "test2": "val2"}]
        write_csv(name=name, images=images)
        open_patch.assert_called_once_with('dockerhub-tags-07.20.2020-11.12.13.csv', 'w')

    @patch('dha.cli.logger')
    def test__get_image_count_Should_CallExpected_When_Called_(
            self,
            logger_patch,
            *patches):
        args = Mock()
        args.screen = None
        args.processes = 10
        args.docker_user = "edgexfoundry1"
        client = Mock()
        client.get.return_value = {"count": "mock_return"}
        get_image_count(args, client)
        logger_patch.debug.assert_called_once()

    @patch('dha.cli.logger')
    def test__get_all_images_Should_CallExpected_When_Called_(
            self,
            logger_patch,
            *patches):
        args = Mock()
        args.screen = None
        args.processes = 10
        args.docker_user = "edgexfoundry1"
        client = Mock()
        client.get.return_value = {"results": "mock_return"}
        get_all_images(args, client)
        client.get.assert_called_once()

    def test__filter_image_list_Should_CallExpected_When_Called_(self,
                                                                 *patches):
        images = [{'test': 'val1', 'is_migrated': 'false', 'pull_count': "33"},
                  {'test': 'val2', 'is_migrated': 'true', 'pull_count': "44"}]
        expected = [{'test': 'val1', 'pull_count': 33},
                    {'test': 'val2', 'pull_count': 44}]
        result = filter_image_list(images)
        self.assertEqual(result, expected)

    @patch('dha.cli.datetime')
    def test__filter_tag_list_Should_CallExpected_When_Called_(
            self,
            datetime_patch,
            *patches):
        datetime_patch.utcnow.return_value = datetime(2020, 7, 23, 11, 12, 13)
        images = [{'test': 'val1', 'result': [{'creator': 'bob',
                                               'a': "here",
                                               'images': [{"architecture":
                                                           "amd64",
                                                           "os": "Linux"}],
                                               'name': "image1",
                                               'full_size': 47623330,
                                               'last_updated': '2017-10-24T12:07:02.964046Z'
                                               }],
                   },
                  {'test': 'val2', 'result': [{'repository': 'go',
                                               'b': "far",
                                               'images': [{"architecture":
                                                           "arm64",
                                                           "os": "Windows"}],
                                               'name': "image2",
                                               'full_size': 26727650,
                                               'last_updated': '2017-10-22T12:07:02.964046Z'
                                               }],
                   }]
        expected = [{'a': 'here',
                     'architecture': "amd64",
                     'os': "Linux",
                     'tag_name': 'image1',
                     'size_in_MB': 45.42,
                     'last_updated': '2017-10-24T12:07:02.964046Z',
                     'days_since_update': 1002
                     },
                    {'b': 'far',
                     'architecture': "arm64",
                     'os': "Windows",
                     'tag_name': 'image2',
                     'size_in_MB': 25.49,
                     'days_since_update': 1004,
                     'last_updated': '2017-10-22T12:07:02.964046Z'
                     }
                    ]
        result = filter_tag_list(images)
        self.maxDiff = None
        print(result)
        print("***")
        print(expected)
        self.assertEqual(result, expected)

    @patch('dha.cli.check_result')
    @patch('dha.cli.execute')
    def test__get_all_tags_Should_CallExpected_When_Called_Mp(
            self,
            execute_patch,
            check_result_patch,
            *patches):
        dockerhub_client = Mock()
        get_tags_mock = Mock()
        args = Mock()
        args.processes = 10
        image_dict_list = MagicMock()
        image_dict_list.len.return_value = 5
        get_all_tags(dockerhub_client, get_tags_mock, args, image_dict_list)
        check_result_patch.assert_called_once()

    @patch('dha.cli.check_result')
    @patch('dha.cli.execute')
    def test__get_all_tags_Should_CallExpected_When_Called_Sp(
            self,
            execute_patch,
            check_result_patch,
            *patches):
        dockerhub_client = Mock()
        get_tags_mock = Mock()
        args = Mock()
        args.processes = 1
        image_dict_list = MagicMock()
        image_dict_list.len.return_value = 5
        get_all_tags(dockerhub_client, get_tags_mock, args, image_dict_list)
        assert not check_result_patch.b.called

    @patch('dha.cli.logger')
    def test__get_tags_Should_CallExpected_When_Called_(
            self,
            logger_patch,
            *patches):
        get_return = {
            "count": "mock_return",
            "results": [{
                "a": "b",
                "star_count": 5,
                "pull_count": 4
            }]
        }
        image = {
            "name": "image1",
            "star_count": 44,
            "pull_count": 55
        }
        shared_data = {}
        shared_data['client'] = Mock()
        shared_data['args'] = Mock()
        shared_data['image_tags_dict_list'] = Mock()
        shared_data['client'].get.return_value = get_return
        get_tags(image, shared_data)
        self.assertEqual(logger_patch.debug.call_count, 2)
