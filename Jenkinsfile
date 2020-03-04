pipeline {
    agent { label 'centos7-docker-4c-2g' }
    environment {
        GH_SRC_ORG      = 'edgexfoundry'
        LABEL_SRC_REPO  = '...'
        GH_TOKEN        = credentials('edgex-jenkins-access-username')
        BLACKLIST_REPOS = '' // pipe delimited list of repo names example: blackbox-testing|ci-management
    }
    triggers {
        cron('H 9 * * 1')
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