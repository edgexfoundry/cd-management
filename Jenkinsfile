//
// Copyright (c) 2021 Intel Corporation
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
        label 'ubuntu18.04-docker-8c-8g'
    }
    parameters {
        string(
            name: 'Execute',
            defaultValue: '',
            description: 'Specify --execute to run script in execute mode, leave it blank to run script in NOOP mode.')
        string(
            name: 'Name',
            defaultValue: '--name docker-sample-service',
            description: 'Specify \'--name <regex>\' to match name of images to include in processing. Leaving this argument \
                blank will target all overviews in the specified overviews folder.')
        booleanParam(
            name: 'Legacy',
            defaultValue: false,
            description: 'Update legacy descriptions and overviews')
    }
    environment {
        OVERVIEWS_FOLDER = getOverviewsPath()
        DESCRIPTIONS_PATH = getDescriptionPath()
        RELEASE_DOCKER_SETTINGS = 'cd-management-settings'
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
                    when { triggeredBy 'UserIdCause' }
                    steps {
                        configFileProvider([configFile(fileId: env.RELEASE_DOCKER_SETTINGS, variable: 'SETTINGS_FILE')]) {
                            sh "python deploy-overviews.py --user edgexfoundry ${params.Name} ${params.Execute}"
                        }
                    }
                }

                post {
                    always { archiveArtifacts artifacts: 'deploy-overviews.log', allowEmptyArchive: true }
                }
            }
        }
    }
    post {
        always {
            edgeXInfraPublish()
        }
    }
}

def getOverviewsPath() {
    "generated-overviews/${params.Legacy ? 'legacy' : 'new'}-names"
}

def getDescriptionPath() {
    "descriptions/${params.Legacy ? 'legacy_' : ''}image_descriptions.txt"
}