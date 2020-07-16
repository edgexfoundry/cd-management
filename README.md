
# dockerhub-audit

## Summary

This script will audit the EdgeX Foundry dockerhub account for stale or outdated docker images, tags and versions. It uses the public docker hub REST API and does not require authentication.

### `dockerhub-audit`

```Script
usage: dockerhub-audit [-h] [--docker-user DOCKER_USER]
                       [--dockerhub-host-api DOCKERHUB_HOST_API] [--csv]
                       [--noop] [--procs PROCESSES] [--screen]

A Python script scrapes the hub.docker.com REST API to determine which images
are "stale" from the edgexfoundry organization.

optional arguments:
  -h, --help            show this help message and exit
  --docker-user DOCKER_USER
                        Docker User
  --dockerhub-host-api DOCKERHUB_HOST_API
                        hub.docker.com host API
  --csv                 write jobs to CSV file
  --noop                execute in NOOP mode (DRY RUN)
  --procs PROCESSES     number of concurrent processes to execute
  --screen              visualize script execution using a curses screen
```

### Build Docker

Build docker image:

```bash
docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t dockerhub-audit:latest .
```

Execute docker container:

```bash
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
 -e TERM='xterm-256color' \
dockerhub-audit:latest \
/bin/sh
```

#### Example

```dockerhub-audit --docker-user edgexfoundry --csv```
