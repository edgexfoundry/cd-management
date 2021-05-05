
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
from mock import Mock

from envbuilder import EnvBuilder
from envbuilder.cli import parse_args
from envbuilder.cli import set_logging

from argparse import Namespace
from semantic_version import Version

import os
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
        resources_dir = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '..', 'resources')
        self.mock_env = f'{resources_dir}/mock-env'
        self.mock_out = f'{resources_dir}/mock-env-out'

    def tearDown(self):

        pass

    @patch('envbuilder.cli.ArgumentParser')
    def test__parse_args_Should_ReturnExpected_When_Called(self, *patches):
        # not much to unit test here
        parse_args()

    @patch('envbuilder.cli.logging')
    def test__set_logging_Should_CallExpected_When_Called(self, logging_patch, *patches):
        root_logger_mock = Mock()
        logging_patch.getLogger.return_value = root_logger_mock
        args_mock = Namespace(verbose=True)
        # not much to test here
        set_logging(args_mock)

    def test__init__Should_RaiseValueError_When_NoBearerToken(self, *patches):
        with self.assertRaises(ValueError):
            args = Namespace(envfile=None, repo=None, org=None, out=None,
                no_lookup=False, verbose=True, no_deps=False, deps=None)
            EnvBuilder(args)

    @patch.dict(os.environ, {"GH_TOKEN_PSW": "mock-token"})
    def test__init__Should_InitializeVariables(self, *patches):
        # it is way easier to mock with an actual env file
        # rather thank try to manually mock each line by line, use the source
        args = Namespace(envfile=self.mock_env, repo=None, org=None, out=self.mock_out,
                         no_lookup=False, verbose=True, no_deps=False, deps=None)
        builder = EnvBuilder(args)

        self.assertNotEqual(builder.image_search, None)
        self.assertNotEqual(builder.api, None)
        self.assertNotEqual(builder.envfile, None)
        self.assertNotEqual(builder.compose_env_vars, None)
        self.assertNotEqual(builder.repo_map, None)
        self.assertEqual(len(builder.repo_map), 12)
        self.assertEqual(builder.docker_repository, 'edgexfoundry')

    @patch.dict(os.environ, {"GH_TOKEN_PSW": "mock-token"})
    def test__get_client__Should_InitializeProperly(self, *patches):
        # it is way easier to mock with an actual env file
        # rather thank try to manually mock each line by line, use the source
        args = Namespace(envfile=self.mock_env)
        builder = EnvBuilder(args)
        client = builder.get_client()

        self.assertNotEqual(client, None)

    @patch('os.access')
    def test__read_env_file__Should_ProperlyParseEnvFile(self, os_patch, *patches):
        path = self.mock_env
        lines = EnvBuilder.read_env_file(path)
        os_patch.assert_called_once_with(path, os.R_OK)
        self.assertEqual(len(lines), 50)

    @patch.dict(os.environ, {"GH_TOKEN_PSW": "mock-token"})
    @patch('envbuilder.cli.EnvBuilder.get_client')
    def test__log_ratelimit_Should_LogExpected_When_Header(self, get_client_patch, *patches):
        mock_api = Mock()
        get_client_patch.return_value = mock_api

        mock_api.get.return_value = {
            'resources': {
                'core': {
                    'minutes': '32',
                    'remaining': '4999',
                    'limit': '5000',
                }
            }
        }
        args = Namespace(envfile=self.mock_env)
        builder = EnvBuilder(args)
        rl = builder.rate_limit()

        mock_api.get.assert_called_once_with('/rate_limit')
        self.assertEqual(rl, {'minutes': '32', 'remaining': '4999', 'limit': '5000'})

    @patch.dict(os.environ, {"GH_TOKEN_PSW": "mock-token"})
    @patch('envbuilder.cli.EnvBuilder.get_client')
    def test__process_tags_Should_Run(self, get_client_patch, *patches):
        mock_api = Mock()
        get_client_patch.return_value = mock_api
        mock_api.get_latest.return_value = Version('1.0.0')

        args = Namespace(envfile=self.mock_env, org=None)
        builder = EnvBuilder(args)
        builder.process_tags()

        mock_api.get_latest.assert_any_call('edgex-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('app-service-configurable', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('edgex-ui-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-bacnet-c', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-camera-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-grove-c', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-modbus-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-mqtt-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-random', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-rest-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-snmp-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-virtual-go', 'edgexfoundry')

        self.assertEqual(builder.compose_env_vars['CORE_EDGEX_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['APP_SERVICE_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['EDGEX_UI_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_BACNET_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_CAMERA_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_GROVE_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_MODBUS_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_MQTT_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_RANDOM_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_REST_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_SNMP_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_VIRTUAL_VERSION'], '1.0.0')

    @patch.dict(os.environ, {"GH_TOKEN_PSW": "mock-token"})
    @patch('envbuilder.DockerImageSearch.get_image_versions')
    def test__lookup_dependencies_Should_Run(self, image_search_patch, *patches):
        def version_mock(image, org, filter, verbose):
            v = f"1.0.0-alpine" if filter == 'alpine' else '1.0.0'
            return {
                filter: [v]
            }

        image_search_patch.side_effect = version_mock

        args = Namespace(envfile=self.mock_env, org=None)
        builder = EnvBuilder(args)
        updated_versions = builder.lookup_dependencies('vault consul redis kong kuiper mosquitto')

        self.assertEqual(updated_versions['VAULT_VERSION'], '1.5.3 --> 1.0.0')
        self.assertEqual(updated_versions['CONSUL_VERSION'], '1.9.1 --> 1.0.0')
        self.assertEqual(updated_versions['REDIS_VERSION'], '6.0.9-alpine --> 1.0.0-alpine')
        self.assertEqual(updated_versions['KONG_VERSION'], '2.3-alpine --> 1.0.0-alpine')
        self.assertEqual(updated_versions['KUIPER_VERSION'], '1.1.2-alpine --> 1.0.0-alpine')
        self.assertEqual(updated_versions['MOSQUITTO_VERSION'], '1.6.3 --> 1.0.0')


    def test__env_to_dict__Should_ProperlyConvertEnvToDict(self, *patches):
        path = self.mock_env
        lines = EnvBuilder.read_env_file(path)
        dict = EnvBuilder.env_to_dict(lines)
        self.assertEqual(len(dict), 27)
        self.assertEqual(dict['REPOSITORY'], 'mock-repository')
        self.assertEqual(dict['CORE_EDGEX_VERSION'], 'master')
        self.assertEqual(dict['APP_SERVICE_VERSION'], 'master')
        self.assertEqual(dict['EDGEX_UI_VERSION'], 'master')
        self.assertEqual(dict['DEVICE_BACNET_VERSION'], 'master')
        self.assertEqual(dict['DEVICE_CAMERA_VERSION'], 'master')
        self.assertEqual(dict['DEVICE_GROVE_VERSION'], 'master')
        self.assertEqual(dict['DEVICE_MODBUS_VERSION'], 'master')
        self.assertEqual(dict['DEVICE_MQTT_VERSION'], 'master')
        self.assertEqual(dict['DEVICE_RANDOM_VERSION'], 'master')
        self.assertEqual(dict['DEVICE_REST_VERSION'], 'master')
        self.assertEqual(dict['DEVICE_SNMP_VERSION'], 'master')
        self.assertEqual(dict['DEVICE_VIRTUAL_VERSION'], 'master')
