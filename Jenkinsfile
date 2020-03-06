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
    agent { label 'centos7-docker-4c-2g' }
    environment {
        GH_SRC_ORG      = 'edgexfoundry'
        LABEL_SRC_REPO  = 'cd-management'
        GH_TOKEN        = credentials('edgex-jenkins-access-username')
        // BLACKLIST_REPOS = '' // pipe delimited list of repo names example: blackbox-testing|ci-management
    }
    // run at midnight
    triggers {
        cron '''TZ=US/Eastern
        @midnight'''
    }
    stages{
        stage('Apply GitHub Labels') {
            when {
                anyOf {
                    triggeredBy 'UserIdCause'
                    triggeredBy 'TimerTrigger'
                }
            }
            steps {
                sh './github-copy-labels.sh "$GH_SRC_ORG" "$LABEL_SRC_REPO" "$BLACKLIST_REPOS"'
            }
        }
    }
}