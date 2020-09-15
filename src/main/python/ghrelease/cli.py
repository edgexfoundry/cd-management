
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

import os
import sys
import logging
from argparse import ArgumentParser

from ghrelease import API

logger = logging.getLogger(__name__)


class MissingArgumentError(Exception):
    """ argument error
    """
    pass


def get_parser():
    """ setup parser and return parsed command line arguments
    """
    parser = ArgumentParser(
        description='A Python script to facilitate creation of GitHub releases with assets')
    parser.add_argument(
        '--repo',
        dest='repo',
        type=str,
        required=True,
        help='GitHub repo where release is to be created')
    parser.add_argument(
        '--tag',
        dest='tag',
        type=str,
        required=True,
        help='The name of the existing tag to associate with the release')
    parser.add_argument(
        '--assets',
        dest='assets',
        type=str,
        required=True,
        help='The name of the directory containing the assets to upload to the release')
    parser.add_argument(
        '--release',
        dest='release',
        type=str,
        required=False,
        help='The name to give the release - if not provided will use name of tag')
    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='display debug messages to stdout')
    return parser


def validate(args):
    """ validate args
    """
    if not os.access(args.assets, os.R_OK):
        raise ValueError(f'the directory {args.assets} is not accessible')


def get_client():
    """ return instance of API
    """
    return API(
        hostname=os.getenv('GH_BASE_URL', 'api.github.com'),
        bearer_token=os.getenv('GH_TOKEN_PSW'))


def set_logging(args):
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)

    logfile = '{}/create-github-release.log'.format(os.getenv('PWD'))
    file_handler = logging.FileHandler(logfile)
    file_formatter = logging.Formatter("%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    formatter = '%(asctime)s %(name)s [%(funcName)s] %(levelname)s %(message)s'
    stream_formatter = logging.Formatter(formatter)
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
    rootLogger.addHandler(stream_handler)


def main():
    """ main function
    """
    parser = get_parser()
    try:
        args = parser.parse_args()
        validate(args)
        set_logging(args)
        client = get_client()
        client.create_release_upload_assets(
            args.repo, args.tag, args.assets, release_name=args.release)

    except MissingArgumentError as exception:
        parser.print_usage()
        logger.error("ERROR: {}".format(str(exception)))

    except Exception as exception:
        logger.error("ERROR: {}".format(str(exception)))
        sys.exit(-1)


if __name__ == '__main__':  # pragma: no cover

    main()
