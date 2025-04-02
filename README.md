# cd-management/prune-github-tags
[![build-status](https://jenkins.edgexfoundry.org/job/edgexfoundry/job/cd-management/job/prune-github-tags/badge/icon)](https://jenkins.edgexfoundry.org/job/edgexfoundry/job/cd-management/job/prune-github-tags)
[![coverage](https://img.shields.io/badge/coverage-100.0%25-brightgreen)](https://pybuilder.io/)
[![complexity](https://img.shields.io/badge/complexity-Slight:%2012-yellow)](https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![python](https://img.shields.io/badge/python-3.9-teal)](https://www.python.org/downloads/)

## Summary

This script queries repos from a specified GitHub organization and by default removes all old pre-release tags found in the repos. The majority of the repos in the EdgeXFoundry org leverage a semantic versioning tagging convention, over time the need has risen to prune (i.e. remove) older pre-release tags in order to maintain a sanitized set of tags for each repo. For more information regarding semantic versioning refer to the following: https://semver.org/. Optional functionality also exists to remove specific version ranges following standard semantic versioning rules. e.g. `>=1.0.20,<1.0.50`

## Jenkins Triggers

* Manual (User initiated)

## Script Usage

### `prune-github-tags`
```bash
 ____                           ____ _ _   _   _       _
|  _ \ _ __ _   _ _ __   ___   / ___(_) |_| | | |_   _| |__
| |_) | '__| | | | '_ \ / _ \ | |  _| | __| |_| | | | | '_ \
|  __/| |  | |_| | | | |  __/ | |_| | | |_|  _  | |_| | |_) |
|_|   |_|   \__,_|_| |_|\___|  \____|_|\__|_| |_|\__,_|_.__/

 _____
|_   _|_ _  __ _ ___
  | |/ _` |/ _` / __|
  | | (_| | (_| \__ \
  |_|\__,_|\__, |___/
           |___/

usage: prune-github-tags [-h] [--org ORG] [--user USER]
                         [--exclude-repos EXCLUDE_REPOS]
                         [--include-repos INCLUDE_REPOS] [--report]
                         [--procs PROCESSES] [--screen] [--debug] [--execute]
                         [--remove-version VERSION] [--branch BRANCH]

A Python script that removes old prerelease tags from repos in a GitHub org

optional arguments:
  -h, --help            show this help message and exit
  --org ORG             GitHub organization containing repos to process
  --user USER           GitHub user containing repos to process
  --exclude-repos EXCLUDE_REPOS
                        a regex to match name of repos to exclude from
                        processing
  --include-repos INCLUDE_REPOS
                        a regex to match name of repos to include in
                        processing
  --report              generate and save report but do not process
  --procs PROCESSES     number of concurrent processes to execute
  --screen              visualize script execution using a curses screen
  --debug               display debug messages to stdout
  --execute             execute processing - not setting is same as running in
                        NOOP mode
  --remove-version VERSION
                        version expression to remove- e.g. '<1.0.50',
                        '>1.0.87', '<1.1.4,>=1.0.1'
  --branch BRANCH       query commits by branch
```

### Reference
For `--remove-version` option syntax refer to [SimpleSpec Syntax Reference](https://python-semanticversion.readthedocs.io/en/latest/reference.html#semantic_version.SimpleSpec)

#### Screen
This is an example of the execution visualization using the `--screen` argument:
![screen](/docs/images/screen.gif)

#### Environment Variables

* `GH_TOKEN_PSW`      (Required) - The GitHub personal access token used to authenticate GitHub Commands
* `GH_BASE_URL`       (Optional) - GitHub API URL. Can be changed to point to a different GitHub API endpoint i.e. GitHub Enterprise
* `GH_ORG`            (Optional) - GitHub organization to process
* `GH_EXCLUDE_REPOS`  (Optional) - GitHub repos to exclude from processing
* `DRY_RUN`           (Optional) - Execute in noop mode - the --execute argument takes precedence

#### Examples

prune prerelease tags in all edgexfoundry repos - execute in NOOP mode
```bash
prune-github-tags \
--org edgexfoundry
```

prune prerelease tags in all edgexfoundry repos using 10 concurrent processes
```bash
prune-github-tags \
--org edgexfoundry \
--procs 10 \
--execute
```

prune prerelease tags in the edgexfoundry device and go-mod repos exclude the go-mod-bootstrap repo from processing and visualize execution on screen - execute in NOOP mode
```bash
prune-github-tags \
--org edgexfoundry \
--include 'device-|go-mod-' \
--exclude 'go-mod-bootstrap' \
--screen
```

remove *all* (released & pre-released) versions before 1.0.50. execute in NOOP mode.
```bash
prune-github-tags \
--org edgexfoundry \
--include 'edgex-global-pipelines' \
--remove-version '<1.0.50'
```

remove *all* (released & pre-released) versions before 1.0.50 and after (inclusive) 1.0.20. execute in NOOP mode.
```bash
prune-github-tags \
--org edgexfoundry \
--include 'edgex-global-pipelines' \
--remove-version '>=1.0.20,<1.0.50'
```

### Development
Clone the repository:
```
cd
git clone --branch prune-github-tags https://github.com/edgexfoundry/cd-management.git prune-github-tags
cd prune-github-tags
```

Build the Docker image:
```
docker image build \
--target build-image \
--build-arg http_proxy \
--build-arg https_proxy \
-t \
prunetags:latest .
```

Run the Docker container:
```
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-v $PWD:/code \
prunetags:latest \
/bin/bash
```

Execute the build:
```
pyb -X
```
NOTE: commands above assume working behind a proxy, if not then the proxy arguments to both the docker build and run commands can be removed.
