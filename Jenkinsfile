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
                    }
                    stages {
                        stage('Clone Code') {
                            steps {
                                git changelog: false, poll: false, url: 'https://github.com/edgexfoundry/edgex-go.git'
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
                    }
                    stages {
                        stage('Clone Code') {
                            steps {
                                git changelog: false, poll: false, url: 'https://github.com/edgexfoundry/edgex-go.git'
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