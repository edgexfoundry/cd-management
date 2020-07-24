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
    agent any
    
    options{
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '91'))
        timeout(time: 12, unit: 'HOURS')
    }

    environment {
        GO_PROXY = 'https://nexus3.edgexfoundry.org/repository/go-proxy/'
    }

    triggers {
        cron '@daily'
    }

    stages {
        stage('Snap!') {
            parallel {
                stage('amd64'){
                    agent { label 'centos7-docker-4c-2g' }
                    environment {
                        ARCH = 'amd64'
                        SEMVER_BRANCH = 'master'
                    }
                    stages {
                        stage('Clone Code') {
                            steps {
                                git changelog: false, poll: false, url: 'https://github.com/edgexfoundry/edgex-go.git'

                                // setup git-semver and write VERSION file
                                getSemverVersion()
                            }
                        }
                        stage('Stage Snap'){
                            steps {
                                edgeXSnap(jobType: 'stage', snapChannel: 'latest/edge')
                            }
                        }
                    }
                }
                stage('arm64'){
                    agent { label 'ubuntu18.04-docker-arm64-4c-16g' }
                    environment {
                        ARCH = 'arm64'
                        SEMVER_BRANCH = 'master'
                    }
                    stages {
                        stage('Clone Code') {
                            steps {
                                git changelog: false, poll: false, url: 'https://github.com/edgexfoundry/edgex-go.git'

                                // setup git-semver and write VERSION file
                                getSemverVersion()
                            }
                        }
                        stage('Stage Snap'){
                            steps {
                                edgeXSnap(jobType: 'stage', snapChannel: 'latest/edge')
                            }
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            edgeXInfraPublish()
        }
        cleanup {
            cleanWs()
        }
    }
}

// TODO: Migrate this to edgeXSemver when we refactor it.
def getSemverVersion() {
    def nextSemver = edgeXSemver 'init'
   //  println "--> Next Semver version: v${env.VERSION}" // debug

    // git semver gives us the next version due to the pipelines bumping
    // at the end. We will need to rollback one previous semver
    // version to get the "current"

    def isPre = nextSemver.contains('-')
    def currSemver

    if(isPre) {
        semverSplit  = nextSemver.split('-')
        def preSplit = semverSplit[1].split('\\.')
        def nextPre  = preSplit[1].toInteger()
        def currPre  = nextPre - 1

        currSemver = "${semverSplit[0]}-${preSplit[0]}.${currPre}"
    } else {
        def semverSplit = nextSemver.split('\\.')
        def nextVer = semverSplit.last().toInteger()
        def currVer = nextVer - 1

        def currSemverArray = []
        for(int i = 0; i < semverSplit.size(); i++) {
            def ver = (i != semverSplit.size() - 1) ? semverSplit[i] : currVer
            currSemverArray << ver
        }
        currSemver = currSemverArray.join('.')
    }

    env.VERSION = currSemver

    // Write the new version file
    sh "echo '${currSemver}' > VERSION"
    // sh 'cat VERSION' // debug

    println "--> Current version is: ${env.VERSION}" // debug

    currSemver
}