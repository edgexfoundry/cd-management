# cd-management
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr-raw/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/pulls) 
[![GitHub Contributors](https://img.shields.io/github/contributors/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/contributors) 
[![GitHub Committers](https://img.shields.io/badge/team-committers-green)](https://github.com/orgs/edgexfoundry/teams/devops-core-team/members) 
[![GitHub Commit Activity](https://img.shields.io/github/commit-activity/m/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/commits)

Automated GitHub Action to periodically generate a centralized changelog for each EdgeX Foundry repository.

- Iterates through **non-archived** repositories using the GitHub API.
- Clones each repository in parallel.
- Copies `cliff.toml` template to each repository.
- Ignores `dev` tags for changelog generation.
- Generates and archives the changelog for each repository.

Contributing community members can download this changelog for their repository and use it as a basis for a PR to update the changelog prior to release.

This action utilizes [git-cliff](https://github.com/orhun/git-cliff) for changelog generation.

---

**Note**: The previous changelog generation was managed through a Jenkins job. The Jenkinsfile for this job has been deprecated and is no longer in active use. The current workflow for changelog generation is defined in the `.github` directory of this repository.
