# prune-github-tags

## Summary

This script queries repos from a specified GitHub organization and by default removes all old pre-release tags found in the repos. The majority of the repos in the EdgeXFoundry org leverage a semantic versioning tagging convention, over time the need has risen to prune (i.e. remove) older pre-release tags in order to maintain a sanitized set of tags for each repo. For more information regarding semantic versioning refer to the following: https://semver.org/. Optional functionality also exists to remove specific version ranges following standard semantic versioning rules. e.g. `>=1.0.20,<1.0.50`

### `prune-github-tags`
```bash
usage: prune-github-tags [-h] [--org ORG] [--user USER]
                         [--exclude-repos EXCLUDE_REPOS]
                         [--include-repos INCLUDE_REPOS] [--report]
                         [--procs PROCESSES] [--screen] [--debug] [--execute]
                         [--remove-version EXPRESSION]

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
  --remove-version      version expression to remove specific version(s)
                        *including* pre-release tags.
```

#### Reference
For `--remove-version` option syntax refer to [SimpleSpec Syntax Reference](https://python-semanticversion.readthedocs.io/en/latest/reference.html#semantic_version.SimpleSpec)

#### Pseudo-code
```Script
get-latest-version-tag
  read commits for repo a page at a time
    if commit has an associated tag
      if tag is semantic version
        return latest-version-tag

get-pre-release-tags
  get-latest-version-tag
  iterate over all tags
    if tag is semantic version
      if tag is pre-release
        if tag is not same release as latest-version-tag
          add tag to pre-release-tags

for pre-release-tag in pre-release-tags
  delete pre-release tag
```

#### Environment Variables

* `GH_TOKEN_PSW`  (Required) - The GitHub personal access token used to authenticate GitHub Commands
* `GH_BASE_URL`   (Optional) - GitHub API URL. Can be changed to point to a different GitHub API endpoint i.e. GitHub Enterprise
* `GH_ORG`        (Optional) - GitHub organization to process
* `GH_EXCLUDE`    (Optional) - GitHub repos to exclude from processing
* `DRY_RUN`       (Optional) - Execute in noop mode - the --execute argument takes precedence

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
