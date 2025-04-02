//
// Copyright (c) 2020 Intel Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

pipeline {
    agent {
        label 'centos7-docker-4c-2g'
    }
    parameters {
        string(
            name: 'Execute',
            defaultValue: '',
            description: 'Specify --execute to run script in execute mode, leave it blank to run script in NOOP mode.')
        string(
            name: 'Version',
            defaultValue: '',
            description: 'Specify \'--remove-version <version-range>\' to remove *all* tags within range. Use to remove release tags.\
                See README for syntax. e.g.\"--remove-version \'<1.0.87\'\"')
        string(
            name: 'Include Repositories',
            defaultValue: '--include-repos edgex-global-pipelines',
            description: 'Specify \'--include-repos <repo-name>\' to target specific repositories. For multiple repositories, use <repo-name> as a regex. \
                 Leaving this argument blank will target the edgex-global-pipelines repo within edgexfoundry.')
        string(
            name: 'Branch',
            defaultValue: '--branch main',
            description: 'Specify \'--branch <branch-name>\' to target branch. Set release name to remove the released dev tags.\
                e.g. \"--branch odessa" to remove all 4.0.0-dev.x tags')
    }
    environment {
        GH_TOKEN = credentials('edgex-jenkins-github-personal-access-token')
    }
    stages {
        stage('Build') {
            agent {
                dockerfile {
                    filename 'Dockerfile'
                    reuseNode true
                }
            }
            stages {
                stage('Execute') {
                    when {
                        anyOf {
                            triggeredBy 'UserIdCause'
                        }
                    }
                    steps {
                        sh "prune-github-tags --org edgexfoundry --procs 10 ${params.Execute} ${params.Version} ${params['Include Repositories']} ${params.Branch}"
                    }
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'prune-github-tags.log', allowEmptyArchive: true
            edgeXInfraPublish()
        }
    }
}
