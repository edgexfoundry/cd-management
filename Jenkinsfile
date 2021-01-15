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

@Library("edgex-global-pipelines@experimental") _

def parallelSteps = [:]
def releaseData = []

pipeline {
    agent { label 'centos7-docker-4c-2g' }
    options {
        timestamps()
        timeout(360)
    }
    environment {
        DRY_RUN = false
        DRY_RUN_PULL_DOCKER_IMAGES = true
        RELEASE_DOCKER_SETTINGS = 'cd-management-settings'
    }
    stages {
        stage('Lint YAML files') {
            agent {
                docker {
                    image 'edgex-devops/yamllint:latest'
                    registryUrl 'https://nexus3.edgexfoundry.org:10003'
                    reuseNode true
                    args '--entrypoint="'
                }
            }
            steps {
                sh 'yamllint -v .'
            }
        }

        stage('Prepare Release YAML') {
            steps {
                script {
                    releaseData = edgeXRelease.collectReleaseYamlFiles('release/*.yaml', 'origin/release')
                    parallelSteps = edgeXRelease.parallelStepFactory(releaseData)

                    // Print out the arrays created from the yaml files for manual validation
                    println "parallelSteps: ${parallelSteps}"
                    println "releaseData: ${releaseData}"
                }
            }
        }

        stage('Run Release') {
            steps {
                script {
                    parallel(parallelSteps)
                }
            }
        }
    }
}

def shouldDoDryRun() {
    env.GIT_BRANCH != 'release' ? true : false
}