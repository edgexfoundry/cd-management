[![build-status](https://jenkins.edgexfoundry.org/job/edgexfoundry/job/cd-management/job/git-label-sync/badge/icon)](https://jenkins.edgexfoundry.org/job/edgexfoundry/job/cd-management/job/git-label-sync)

# cd-management/git-label-sync

## Summary

This job will sync **ALL** labels and milestones from a source Organization/Repository to **ALL** repositories under a specified GitHub Organization. A `--exclude-repos` argument can be used to exclude certain repositories within the Source Organization, if the source repo is in the target org than it will automatically be excluded as a target. For example, a user maintains a GitHub repo `edgexfoundry/my-template` where they manage a master list of labels and milestones. They now want to copy ALL the labels and milestones found in `edgexfoundry/my-template` to ALL repositories under the `edgexfoundry` org.

## Jenkins Triggers

* Manual (User initiated)
* Cron (Daily at midnight EST)

## Script Usage

### `sync-github-labels`
```Script
usage: sync-github-labels [-h] [--target-org TARGET_ORG]
                          [--source-repo SOURCE_REPO]
                          [--exclude-repos EXCLUDE_REPOS] [--procs PROCESSES]
                          [--screen] [--modified-since MODIFIED_SINCE]
                          [--debug] [--execute]

A Python script to synchronize GitHub labels and milestones

optional arguments:
  -h, --help            show this help message and exit
  --target-org TARGET_ORG
                        GitHub organization containing repos that serve as the
                        synchronization targets
  --source-repo SOURCE_REPO
                        GitHub repo containing labels and milestones that
                        serve as the synchronization source
  --exclude-repos EXCLUDE_REPOS
                        a comma-delimited list of repos to exclude from
                        synchronization
  --procs PROCESSES     number of concurrent processes to execute
  --screen              visualize script execution using a curses screen
  --modified-since MODIFIED_SINCE
                        choose only sources that have been modified since the
                        duration provided: #[d|h|m] where d=days, h=hours,
                        m=minutes
  --debug               display debug messages to stdout
  --execute             execute processing - not setting is same as running in
                        NOOP mode
```

#### Screen
This is an example of the execution visualization using the `--screen` argument:
![screen](/docs/images/screen.gif)

#### Environment Variables

* `GH_TOKEN_PSW`       (Required) - The GitHub personal access token used to authenticate GitHub Commands
* `GH_BASE_URL`        (Optional) - GitHub API URL. Can be changed to point to a different GitHub API endpoint i.e. GitHub Enterprise
* `GH_TARGET_ORG`      (Optional) - GitHub target organization
* `GH_SOURCE_REPO`     (Optional) - GitHub repo that is source of labels and milestones
* `GH_EXCLUDE_REPOS`   (Optional) - GitHub repos to exclude from synchronization
* `DRY_RUN`            (Optional) - Execute in noop mode - the --noop argument takes precedence

#### Examples

```Script
export GH_TOKEN_PSW=*****************************************
export GH_BASE_URL=api.github.com
export GH_TARGET_ORG=edgexfoundry
export GH_SOURCE_REPO=edgexfoundry/cd-management
```

Start `4` concurrent processes with no screen and exclude the specified repos
```Script
sync-github-labels --procs 4 --exclude-repos 'cd-management,ci-build-images' --execute
```

Start `2` concurrent processes with screen and only include sources that have been modified within the past day and run in NOOP mode
```Script
sync-github-labels --procs 2 --modified-since 1d --screen
```

### Development
Clone the repository:
```
cd
git clone --branch git-label-sync https://github.com/edgexfoundry/cd-management.git sync-github-labels
cd sync-github-labels
```

Build the Docker image:
```
docker image build \
--target build-image \
--build-arg http_proxy \
--build-arg https_proxy \
-t \
synclabels:latest .
```

Run the Docker container:
```
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-v $PWD:/synclabels \
synclabels:latest \
/bin/sh
```

Execute the build:
```
pyb -X
```
NOTE: commands above assume working behind a proxy, if not then the proxy arguments to both the docker build and run commands can be removed.
