# cd-management
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr-raw/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/pulls) [![GitHub Contributors](https://img.shields.io/github/contributors/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/contributors) [![GitHub Committers](https://img.shields.io/badge/team-committers-green)](https://github.com/orgs/edgexfoundry/teams/devops-core-team/members) [![GitHub Commit Activity](https://img.shields.io/github/commit-activity/m/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/commits)

Periodic Jenkins job to automatically generate CHANGELOG.md files each EdgeX Foundry repository.

- Iterates through **non-archived** repositories
- Clones each repository in parallel.
- Copies CHANGELOG.tpl.md and config.yml to each repository (If one already exists in the target repository it will not overwrite it).
- Locally deletes `dev` tags.
- Generates and archives the CHANGELOG.md for each repository.

Contributing community members can download this changelog for their repository and use it as a basis for a PR to update the changelog prior to release.

This job utilizes [git-chglog](https://github.com/git-chglog/git-chglog) for CHANGELOG.md generation.
