# prepbadge
[![complexity](https://img.shields.io/badge/complexity-Stable:%208-olive)](https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-green)](https://pypi.org/project/bandit/)
[![python](https://img.shields.io/badge/python-3.6-teal)](https://www.python.org/downloads/)


A Python script that creates multiple pull request workflows to update an organization's repos with badges. The script also creates a markdown file containing a preview of the badges that will be applied to each repo: [badge preview](prepbadge.md). The script was used specifically for [EdgeXFoundry](https://github.com/edgexfoundry) but can be adapted to apply changes (via PR workflows) for other repos in any other organization.

### Data Collection
The script pulls information from multiple sources to determine the relevant badges to apply to each repository:

* Get data from GitHub for all non-archived and non-disabled repos in the `edgexfoundry` organization
  * Note repos that contain tags
  * Note repos that contain a license
  * Note repos that are Go-based
  * Note team members for each repo
  * Note `$default_branch` for each repo
* Get data from codecov.io for all `edgexfoundry` repos that have code coverage data
  * Note the location of the codecov badge
* Get data from Jenkins for all `edgexfoundry` repos that have build data
  * Note build data for the `$default_branch`, i.e. master or main
* Coalesce all data and determine the relevant badges to apply for each repo
* Create a markdown file containing a preview of the badges to be applied for each repo

### GitHub Pull Requests
The script creates GitHub pull request workflows for each of the target repos in the organization; the workflow is comprised of the following tasks:

* if an open pull request OR merged pull request exists for the repo with the matching criteria below then no new pull request will be created
  * base=`$default_branch` and head=`$user`:`$local_branch`
* fork repo (if not already forked)
  * will be forked for the authenticated user (i.e. owner of the `GH_TOKEN_PSW`)
* create working directory
* clone repo
  * will be cloned to the working directory
* add upstream to the remote repo
* rebase `$default_branch` with upstream
* create `$local_branch` from `$default_branch`
* update readme with the relevant **badges**
* commit change and sign
* push `$local_branch` to the forked repo
* create draft pull request
  * base=`$default_branch` and head=`$user`:`$local_branch`
* verify pull request
  * ensures that only the readme file was changed
* update pull request with reviewers, labels, assignee and milestone

At this point a manual review of the draft pull request is performed, apply any changes to the pull request if needed, afterwards mark the draft pull request as `ready to review`. **Note** if a manual review step is not necessary then update the create pull request workflow step above and set `draft: False` to create a PR that is ready for review.

## `prepbadge`
```
usage: prepbadge [-h] [--org ORG] [--repos REPOS_REGEX]
                 [--branch LOCAL_BRANCH] [--execute]

A Python script that creates multiple pull request workflows to update a
target organization repos with badges

optional arguments:
  -h, --help            show this help message and exit
  --org ORG             GitHub organization containing repos to process
  --repos REPOS_REGEX   a regex to match name of repos to include for
                        processing, if not specified then all non-archived,
                        non-disabled repos in org will be processed
  --branch LOCAL_BRANCH
                        the name of the local branch to create in your fork
                        that will contain your changes
  --execute             execute processing - not setting is same as running in
                        NOOP mode
```

Build the Docker image:
```bash
docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t prepbadge:latest .
```

Run the Docker container:
```bash
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-v $HOME/.gitconfig:/etc/gitconfig \
-v $HOME/.gnupg:/root/.gnupg \
-v $PWD:/prepbadge \
prepbadge:latest /bin/sh
```

Set the required enviornment variables:
```bash
export GH_TOKEN_PSW=--github-token--
export JN_TOKEN_USR=--jenkins-username--
export JN_TOKEN_PSW=--jenkins-username-token--
export CC_TOKEN_PSW=--codecov.io-token--
```

Execute the Python script:
```bash
prepbadge --org edgexfoundry --branch US149 --repos 'ci-|cd-|edgex-global-pipelines|sample-service'
```

Execution of data collection:
![preview](https://raw.githubusercontent.com/soda480/prepbadge/master/docs/images/data-collection.gif)

Script will generate the markdown containing the [badge preview](prepbadge.md)

Execution of pull request workflows:
![preview](https://raw.githubusercontent.com/soda480/prepbadge/master/docs/images/prepbadge.gif)

To build the script:
```bash
pyb -X
```