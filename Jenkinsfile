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

def githubsyncImage

pipeline {
    agent {
        label 'centos7-docker-4c-2g'
    }
    environment {
        DRY_RUN = shouldDoDryRun()
        GH_BASE_URL = 'api.github.com'
        GH_TARGET_ORG = 'edgexfoundry'
        GH_SOURCE_REPO = 'edgexfoundry/cd-management'
        GH_TOKEN = credentials('edgex-jenkins-github-personal-access-token')
        GH_BLACKLIST_REPOS = 'cd-management'
    }
    triggers {
        cron '''TZ=US/Eastern
        0 23 * * *'''
    }
    stages{
        stage('Build') {
            steps {
                script {
                    githubsyncImage = docker.build('githubsync:latest')
                }
            }
        }
        stage('Execute') {
            when {
                anyOf {
                    triggeredBy 'UserIdCause'
                    triggeredBy 'TimerTrigger'
                }
            }
            steps {
                script {
                    // full synchronization on Sunday and incremental all other days
                    def command = 'githubsync --procs 10'
                    def today = getDay()
                    if(today != 'Sunday') {
                        command += ' --modified-since 2d'
                    }
                    githubsyncImage.inside() {
                        sh command
                    }
                }
            }
        }
    }
}

def getDay() {
    // return day of week
   def dayMap = [
       1: 'Sunday',
       2: 'Monday',
       3: 'Tuesday',
       4: 'Wednesday',
       5: 'Thursday',
       6: 'Friday',
       7: 'Saturday'
    ]
    Calendar calendar = Calendar.getInstance()
    def day = calendar.get(Calendar.DAY_OF_WEEK)
    dayMap[day]
}

def shouldDoDryRun() {
    env.GIT_BRANCH != 'git-label-sync' ? true : false
}
