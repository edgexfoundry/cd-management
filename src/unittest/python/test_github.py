
import unittest
from mock import patch
from mock import call
from mock import Mock
from mock import MagicMock

from prepbadge.github import create_working_dir
from prepbadge.github import remove_clone_dir


import sys
import logging
logger = logging.getLogger(__name__)


class TestGitHub(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('prepbadge.github.getenv', return_value='/path')
    @patch('prepbadge.github.execute_command')
    def test__create_working_dir_Should_CallAndReturnExpected_When_Called(self, execute_command_patch, *badges):
        result = create_working_dir('repo1')
        expected_result = '/path/github.com'
        self.assertEqual(result, expected_result)
        execute_command_patch.assert_called_once_with('mkdir -p /path/github.com', shell=True)

    @patch('prepbadge.github.execute_command')
    def test__remove_clone_dir_Should_CallExpected_When_Called(self, execute_command_patch, *patches):
        remove_clone_dir('/path/github.com', 'repo1')
        execute_command_patch.assert_called_once_with('rm -rf /path/github.com/repo1', shell=True)
