# create-patch-release

This repository contains a job which can be used to easily branch and setup a repository branch with required steps needed to properly branch.

The pipeline does the following:

Branch off selected branch (default: main)
Update the Jenkinsfile to have the go version set appropriate for that release. (user input)
Create the semver file for the branch with appropriate initial version for that release. (user input)
