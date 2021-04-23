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

def jobs = []

def generateStage(job) {
    return {    
        def clone_url = job.split('"clone_url": "')[1].replaceAll('",','')
        def repo_url = clone_url.split('\\.git')[0]
        def name = repo_url.split('edgexfoundry\\/')[1]
        sh "git clone ${clone_url}"
        sh "mkdir -p ${name}/.chglog && cp --no-clobber -r .chglog-default/. ${name}/.chglog"
        docker.image('quay.io/git-chglog/git-chglog').inside('--entrypoint=""'){
            dir("${name}"){
                sh "git tag | grep dev | xargs -n 1 -i% git tag -d %"
                sh "/usr/local/bin/git-chglog --repository-url ${repo_url} --next-tag x.y.z --sort semver --output ${name}-CHANGELOG.md || /usr/local/bin/git-chglog --next-tag x.y.z --output ${name}-CHANGELOG.md"
            }
        }
        archiveArtifacts allowEmptyArchive: true, artifacts: "${name}/${name}-CHANGELOG.md"
    }
}

pipeline {
    agent {
        label 'centos7-docker-4c-2g'
    }
    options {
        timestamps()
    }

    triggers {
        cron '@weekly'
    }
    stages {
        stage('Parallel Changelog Generator'){
            steps {
                script {
                    jobs = sh (
                        script: 'curl -i "https://api.github.com/search/repositories?q=user:edgexfoundry+archived:false&per_page=200" | grep clone_url',
                        returnStdout: true).trim().split("\n")
                    parallel jobs.collectEntries {[(it.split('edgexfoundry/')[1].split('.git')[0]) : generateStage(it)]}
                }
            }
        }
    }
}

