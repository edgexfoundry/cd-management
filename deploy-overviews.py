#
# Copyright (c) 2021 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import sys
import requests
import logging
from os import getenv
from argparse import ArgumentParser
from xml.dom import minidom

from rest3client import RESTclient


logger = logging.getLogger(__name__)
logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)

DOCKERHUB_API = 'hub.docker.com/v2'
DESCRIPTION_MAX_CHARS = 100


def get_args():
    """ setup parser and return parsed command line arguments
    """
    parser = ArgumentParser(
        description='A Python script that updates descriptions of DockerHub images using a folder containing associated markdown files')
    parser.add_argument(
        '--overviews',
        dest='overviews_path',
        type=str,
        default=getenv('OVERVIEWS_FOLDER'),
        required=False,
        help='folder path containing Docker image overviews in md format')
    parser.add_argument(
        '--descriptions',
        dest='descriptions_path',
        type=str,
        default=getenv('DESCRIPTIONS_PATH'),
        required=False,
        help='path to file containing Docker image descriptions')
    parser.add_argument(
        '--user',
        dest='user',
        type=str,
        default=getenv('DOCKERHUB_USR'),
        required=False,
        help='DockerHub user containing the Docker images to update')
    parser.add_argument(
        '--name',
        dest='name',
        type=str,
        default='',
        required=False,
        help='a regex to match name of images to include in processing')
    parser.add_argument(
        '--execute',
        dest='execute',
        action='store_true',
        help='execute processing - not setting is same as running in NOOP mode')
    return parser.parse_args()


def get_node(nodes, node_id, node_value):
    """ return DOM node with matching node id and node value
    """
    for node in nodes:
        for child_node in node.childNodes:
            if child_node.nodeName == node_id and child_node.firstChild.nodeValue == node_value:
                return node


def get_node_value(node, name):
    """ return DOM node value with matching name
    """
    for child_node in node.childNodes:
        if child_node.nodeName == name:
            return child_node.firstChild.nodeValue


def get_credentials():
    """ return username password tuple for DockerHub API

        assumes MAVEN settings format:
        https://maven.apache.org/settings.html#servers
    """
    logger.info('getting DockerHub credentials')
    settings_file = getenv('SETTINGS_FILE')
    if not settings_file:
        raise ValueError('SETTINGS_FILE environment variable is not set')
    settings = minidom.parse(settings_file)
    servers = settings.getElementsByTagName('server')
    if not servers:
        raise ValueError('server config not found in settings')
    server = get_node(servers, 'id', 'docker.io')
    if not server:
        raise ValueError('docker.io server config not found in settings')
    username = get_node_value(server, 'username')
    if not username:
        raise ValueError('username not found in docker.io server config')
    password = get_node_value(server, 'password')
    if not password:
        raise ValueError('password not found in docker.io server config')
    return username, password


def get_token(username, password):
    """ return JWToken for DockerHub API access
    """
    logger.info('getting token for DockerHub API access')
    response = requests.post(
        f'https://{DOCKERHUB_API}/users/login/',
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        json={
            'username': username,
            'password': password
        },
        verify=RESTclient.cabundle)
    return response.json()['token']


def get_client(token):
    """ return instance of RESTclient for DockerHub API
    """
    return RESTclient(DOCKERHUB_API, jwt=token)


def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)

    pwd = getenv('PWD')
    logfile = f'{pwd}/deploy-overviews.log'
    file_handler = logging.FileHandler(logfile)
    formatter = logging.Formatter("%(asctime)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    rootLogger.addHandler(stream_handler)


def get_overviews(folder, name):
    """ return list of overviews found in folder that match name
    """
    if name:
        logger.info(f"getting all image overviews in '{folder}' folder that match name '{name}'")
    else:
        logger.info(f"getting all image overviews in '{folder}'")

    overviews = []
    filenames = os.listdir(folder)
    for filename in filenames:
        image = os.path.splitext(filename)[0]
        match = re.match(name, image)
        if match:
            overviews.append(f'{folder}/{filename}')
    logger.info(f"discovered {len(overviews)} matching overviews in '{folder}' folder")
    return overviews


def get_descriptions(descriptions_path):
    """ return dictionary containing contents of file read from descriptions_path
        where image is key and description is value
    """
    logger.info(f"reading image descriptions from '{descriptions_path}' file")
    descriptions = {}
    with open(descriptions_path, 'r', encoding='utf8') as descriptions_file:
        for line in descriptions_file:
            if line.startswith('#'):
                continue
            if ':' not in line:
                logger.debug(f"image description line {line} does not contain contain ':' - skipping")
                continue
            line_split = line.split(':')
            descriptions[line_split[0]] = line_split[1][0:DESCRIPTION_MAX_CHARS]
    logger.info(f"read {len(descriptions)} image descriptions from '{descriptions_path}' file")
    return descriptions


def get_repository_name(overview_path):
    """ return repository name from overview path
    """
    return os.path.splitext(os.path.basename(overview_path))[0]


def get_overview_content(overview_path):
    """ return overview content from overview_path file
    """
    logger.info(f"reading contents of '{overview_path}' file")
    with open(overview_path, 'r', encoding='utf8') as overview_file:
        return overview_file.read()


def update_image(client, repository_name, full_description, description, user, noop):
    """ update DockerHub image
    """
    if noop:
        client.get(f'/repositories/{user}/{repository_name}')

    logger.info(f"updating description of DockerHub image '{repository_name}'")
    client.patch(
        f'/repositories/{user}/{repository_name}/',
        json={
            'full_description': full_description,
            'description': description
        },
        noop=noop)


def update_images(client, overviews, descriptions, user, noop):
    """ update DockerHub images
    """
    failed = False

    for overview in overviews:
        try:
            repository_name = get_repository_name(overview)
            full_description = get_overview_content(overview)
            description = descriptions.get(repository_name)
            if not description:
                raise ValueError(f"image {repository_name} does not have short description")
            update_image(client, repository_name, full_description, description, user, noop)

        except Exception as ex:
            logger.error(f'error occurred updating overview {overview}: {ex}')
            failed = True
            continue

    if failed:
        raise Exception('error occurred updating overviews - check log for details')


def main():
    """ main method
    """
    try:
        args = get_args()
        configure_logging()
        username, password = get_credentials()
        token = get_token(username, password)
        client = get_client(token)
        overviews = get_overviews(args.overviews_path, args.name)
        descriptions = get_descriptions(args.descriptions_path)
        update_images(client, overviews, descriptions, args.user, not args.execute)

    except Exception as ex:
        logger.error(ex)
        sys.exit(-1)


if __name__ == '__main__':  # pragma: no cover

    main()
