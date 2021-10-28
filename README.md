# cd-management/dockerhub-audit
[![build-status](https://jenkins.edgexfoundry.org/job/edgexfoundry/job/cd-management/job/dockerhub-audit/badge/icon)](https://jenkins.edgexfoundry.org/job/edgexfoundry/job/cd-management/job/dockerhub-audit)
[![coverage](https://img.shields.io/badge/coverage-80.0%25-yellow)](https://pybuilder.io/)
[![complexity](https://img.shields.io/badge/complexity-Simple:%204-brightgreen)](https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![python](https://img.shields.io/badge/python-3.9-teal)](https://www.python.org/downloads/)

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
  --procs PROCESSES     number of concurrent processes to execute
  --screen              visualize script execution using a curses screen
```

#### Example

```dockerhub-audit --docker-user edgexfoundry --csv```

### Development ###

Ensure the latest version of Docker is installed on your development server and clone the repository.

Clone the repository:
```
cd
git clone --branch dockerhub-audit https://github.com/edgexfoundry/cd-management.git dockerhub-audit
cd dockerhub-audit
```

Build the Docker image:
```sh
docker image build \
--target build-image \
--build-arg http_proxy \
--build-arg https_proxy \
-t dockerhub-audit:latest .
```

Run the Docker container:
```sh
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-v $PWD:/code \
dockerhub-audit:latest \
/bin/bash
```

Execute the build:
```sh
pyb -X
```

NOTE: commands above assume working behind a proxy, if not then the proxy arguments to both the docker build and run commands can be removed.
