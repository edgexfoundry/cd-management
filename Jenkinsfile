//
// Copyright (c) 2023 Intel Corporation
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
            defaultValue: '--execute',
            description: 'Specify --execute to run script in execute mode, leave it blank to run script in NOOP mode.')
        string(
            name: 'Name',
            defaultValue: '',
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
            when {
                expression { env.GIT_BRANCH == 'edgex-docker-hub-documentation' }
            }
            stages {
                stage('Generate Overviews') {
                    when {
                        expression { getCommitMessage() !=~ /^deploy(generated-overviews)/ }
                    }
                    agent {
                        dockerfile {
                            filename 'Dockerfile'
                            reuseNode true
                        }
                    }
                    steps {
                        sh 'python generate-overviews.py --offline'
                    }
                }
                stage('Commit Generated Overviews') {
                    when {
                        expression { getCommitMessage() !=~ /^deploy(generated-overviews)/ }
                    }
                    steps {
                        sshagent(credentials: ['edgex-jenkins-ssh']) {
                            sh '''
                            git checkout edgex-docker-hub-documentation

                            if ! git diff-index --quiet HEAD --; then
                                echo "Found changes in repo committing..."
                                git config --global user.email "jenkins@edgexfoundry.org"
                                git config --global user.name "EdgeX Jenkins"
                                git add .
                                git commit -s -m "deploy(generated-overviews): automated commit of generated overviews"
                                git push origin edgex-docker-hub-documentation
                            else
                                echo "Clean nothing to commit"
                            fi
                            '''
                        }
                    }
                }
                stage('Execute') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile'
                            reuseNode true
                        }
                    }
                    when {
                        expression { edgex.didChange('generated-overviews/.*', 'origin/edgex-docker-hub-documentation') }
                    }
                    steps {
                        configFileProvider([configFile(fileId: env.RELEASE_DOCKER_SETTINGS, variable: 'SETTINGS_FILE')]) {
                            sh "python deploy-overviews.py --user edgexfoundry ${params.Name} ${params.Execute}"
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'deploy-overviews.log', allowEmptyArchive: true
            edgeXInfraPublish()
        }
    }
}

def getCommitMessage() {
    sh(script: "git log --format=format:%B -1 ${env.GIT_COMMIT}", returnStdout: true).trim()
}

def getOverviewsPath() {
    "generated-overviews/${params.Legacy ? 'legacy' : 'new'}-names"
}

def getDescriptionPath() {
    "descriptions/${params.Legacy ? 'legacy_' : ''}image_descriptions.txt"
}