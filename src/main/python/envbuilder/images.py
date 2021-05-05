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

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os

from rest3client import RESTclient


class DockerImageSearch(RESTclient):
    def __init__(self, registry='hub.docker.com', **kwargs):
        cabundle = os.getenv('REQUESTS_CA_BUNDLE')

        if cabundle:
            super(DockerImageSearch, self).__init__(registry, cabundle=cabundle, **kwargs)
        else:
            super(DockerImageSearch, self).__init__(registry, **kwargs)

    def get_image_versions(self, repo, org='library', filter='latest', verbose=True):
        results = self.get(
            f'/v2/repositories/{org}/{repo}/tags/?page=1&page_size=100')['results']

        if results:
            lookup_digest = None
            v_by_digest = {}

            transpose = {
                filter: []
            }

            # create a lookup dict by sha --> tag name
            for r in results:
                if r['name'] == filter:
                    for image in r['images']:
                        # this is the most common arch
                        if image['architecture'] == 'amd64':
                            d = image['digest']
                            lookup_digest = d
                            v_by_digest[d] = []

            # if tags were found by that name filter then add them to that sha
            if len(v_by_digest) > 0:
                if lookup_digest:
                    for r in results:
                        for image in r['images']:
                            if image['digest'] == lookup_digest:
                                v_by_digest[lookup_digest].append(r['name'])

                for v in v_by_digest[lookup_digest]:
                    if v != filter:
                        transpose[filter].append(v)

            # otherwise just filter all matching
            else:
                for r in results:
                    if filter in r['name']:
                        transpose[filter].append(r['name'])

            if verbose:
                print(f"{org}/{repo}", transpose)

            return transpose
        else:
            print(f"Could not find image for: {org}/{repo}")


def parse_args():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='docker image tag lookup')

    parser.add_argument('--repo', required=True, default=None,
                        help=('The repo to lookup tags'))

    parser.add_argument('--org', required=False, default='library',
                        help=('The organization to lookup'))

    parser.add_argument('--filter', required=False, default='latest',
                        help=('The version to filter by'))

    return parser.parse_args()


def main():
    args = parse_args()
    d = DockerImageSearch()
    d.get_image_versions(args.repo, args.org, args.filter)


if __name__ == "__main__":
    main()
