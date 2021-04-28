from rest3client import RESTclient
import os
import argparse

def get_image_versions(repo, org='library', filter='latest', rollup=True, verbose=True):
    registry = 'hub.docker.com'
    cabundle = os.getenv('REQUESTS_CA_BUNDLE')

    if cabundle:
        client = RESTclient(registry, cabundle=cabundle)
    else:
        client = RESTclient(registry)

    results = client.get(f'/v2/repositories/{org}/{repo}/tags/?page=1&page_size=100')['results']

    v_by_digest = {}
    lookup_digest = None

    if results:
        if rollup:
            for r in results:
                if r['name'] == filter:
                    for image in r['images']:
                        # this is the most common arch
                        if image['architecture'] == 'amd64':
                            d = image['digest']
                            lookup_digest = d
                            v_by_digest[d] = []

            if lookup_digest:
                for r in results:
                    for image in r['images']:
                        if image['digest'] == lookup_digest:
                            v_by_digest[lookup_digest].append(r['name'])

            transpose = {
                filter: []
            }

            for v in v_by_digest[lookup_digest]:
                if v != filter:
                    transpose[filter].append(v)
        else:
            transpose = {
                filter: []
            }

            for r in results:
                if filter in r['name']:
                    transpose[filter].append(r['name'])

        if verbose:
            print(f"{org}/{repo}", transpose)

        return transpose
    else:
        print(f"Could not find image for: {org}/{repo}")

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='docker image tag lookup')

    parser.add_argument('--repo', required=True, default=None,
                        help=('The repo to lookup tags'))

    parser.add_argument('--org', required=False, default='library',
                        help=('The organization to lookup'))

    parser.add_argument('--filter', required=False, default='latest',
                        help=('The version to filter by'))

    parser.add_argument('--no-rollup', required=False, action='store_true',
                        help=('Do not roll up the results to the group'))

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    rollup = False if args.no_rollup else True
    get_image_versions(args.repo, args.org, args.filter, rollup)
