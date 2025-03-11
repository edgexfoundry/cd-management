
# Copyright (c) 2020 Intel Corporation
# Copyright (c) 2025 IOTech Ltd

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
        self.assertEqual(len(builder.repo_map), 20)
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
        self.assertEqual(len(lines), 59)

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
        mock_api.get_latest.assert_any_call('app-rfid-llrp-inventory', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('app-record-replay', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('edgex-ui-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-bacnet-c', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-modbus-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-mqtt-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-rest-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-snmp-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-virtual-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-rfid-llrp-go', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-coap-c', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-gpio', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-uart', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-onvif-camera', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-usb-camera', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-s7', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-opc-ua', 'edgexfoundry')
        mock_api.get_latest.assert_any_call('device-can', 'edgexfoundry')

        self.assertEqual(builder.compose_env_vars['CORE_EDGEX_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['APP_SERVICE_CONFIG_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['APP_LLRP_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['APP_RECORD_REPLAY_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['EDGEX_UI_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_BACNET_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_MODBUS_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_MQTT_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_REST_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_SNMP_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_VIRTUAL_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_LLRP_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_COAP_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_GPIO_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_UART_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_ONVIFCAM_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_USBCAM_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_S7_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_OPCUA_VERSION'], '1.0.0')
        self.assertEqual(builder.compose_env_vars['DEVICE_CAN_VERSION'], '1.0.0')

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
        updated_versions = builder.lookup_dependencies('bao postgres kuiper mosquitto nanomq nats nginx')

        self.assertEqual(updated_versions['BAO_VERSION'], '2.1.1 --> 1.0.0')
        self.assertEqual(updated_versions['POSTGRES_VERSION'], '12.3-alpine --> 1.0.0-alpine')
        self.assertEqual(updated_versions['KUIPER_VERSION'], '1.1.2-alpine --> 1.0.0-alpine')
        self.assertEqual(updated_versions['MOSQUITTO_VERSION'], '1.6.3 --> 1.0.0')
        self.assertEqual(updated_versions['NANOMQ_VERSION'], '0.18.2 --> 1.0.0')
        self.assertEqual(updated_versions['NATS_VERSION'], '2.9.25-alpine --> 1.0.0-alpine')
        self.assertEqual(updated_versions['NGINX_VERSION'], '1.25.5-alpine-slim --> 1.0.0-alpine')


    def test__env_to_dict__Should_ProperlyConvertEnvToDict(self, *patches):
        path = self.mock_env
        lines = EnvBuilder.read_env_file(path)
        dict = EnvBuilder.env_to_dict(lines)
        self.assertEqual(len(dict), 35)
        self.assertEqual(dict['REPOSITORY'], 'mock-repository')
        self.assertEqual(dict['CORE_EDGEX_VERSION'], 'latest')
        self.assertEqual(dict['APP_SERVICE_CONFIG_VERSION'], 'latest')
        self.assertEqual(dict['APP_LLRP_VERSION'], 'latest')
        self.assertEqual(dict['APP_RECORD_REPLAY_VERSION'], 'latest')
        self.assertEqual(dict['EDGEX_UI_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_BACNET_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_MODBUS_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_MQTT_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_REST_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_SNMP_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_VIRTUAL_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_LLRP_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_COAP_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_GPIO_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_UART_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_ONVIFCAM_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_USBCAM_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_S7_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_OPCUA_VERSION'], 'latest')
        self.assertEqual(dict['DEVICE_CAN_VERSION'], 'latest')
