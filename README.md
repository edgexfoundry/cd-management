# cd-management/bump-semver


## Summary

This job will automatically bump the version file in the semver branch for the selected EdgeX Foundry Github repositories.

## Triggers

* The job can be triggered manually on the [EdgeX Jenkins Production Server](https://jenkins.edgexfoundry.org/) .

## Usage

Parameters:
* Version: Target version. Follow the pattern: `^(0|([1-9]\d*))\.(0|([1-9]\d*))\.(0|([1-9]\d*))-dev\.([1-9]\d*)$`. E.g. `4.1.0-dev.1`
* Query: Target EdgeX Foundry Github repositories. Refer to [GitHub API documentation](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories).
* Branch: Target branch to be updated in the semver branch.
