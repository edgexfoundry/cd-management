pipeline {
    agent { label 'ubuntu18.04-docker-8c-8g' }
    parameters {
        choice(
            choices: getEdgexRepos(),
            name: 'REPO',
            description: 'Select a repository to create patch release branch'
        )
        string(
            name: 'BRANCH_SOURCE',
            defaultValue: 'main',
            description: 'Source branch to branch from'
        )
        string(
            name: 'NEW_BRANCH',
            defaultValue: '',
            description: 'Enter a unique branch name. Note: The branch must not already exist.'
        )
        string(
            name: 'SEMVER_INIT',
            defaultValue: '',
            description: 'Enter the semantic version to init the branch with. Example: 3.1.1-dev.1'
        )
        string(
            name: 'GO_VERSION',
            defaultValue: '1.21',
            description: 'Enter the Go version the branch will use'
        )
    }
    stages {
        stage('Create Patch Release Branch') {
            when {
                beforeAgent true
                triggeredBy 'UserIdCause'
            }
            stages {
                stage('SSH Fix') {
                    steps {
                        // Remove existing ssh-rsa key for github.com in known hosts to fix IP mismatch
                        sh '''
                        grep -v github.com /etc/ssh/ssh_known_hosts > /tmp/ssh_known_hosts
                        if [ -e /tmp/ssh_known_hosts ]; then
                            sudo mv /tmp/ssh_known_hosts /etc/ssh/ssh_known_hosts
                        fi
                        '''
                    }
                }

                stage('Clone Repo') {
                    when {
                        expression { params.REPO != '- select repo -' }
                    }
                    steps {
                        sshagent(credentials: ['edgex-jenkins-ssh']) {
                            sh "git clone -b ${params.BRANCH_SOURCE} git@github.com:edgexfoundry/${params.REPO}.git ${env.WORKSPACE}/repo"
                            sh "git clone -b ${params.BRANCH_SOURCE} git@github.com:edgexfoundry/${params.REPO}.git ${env.WORKSPACE}/semver"
                            
                            sh '''
                            git config --global user.email "jenkins@edgexfoundry.org"
                            git config --global user.name "EdgeX Jenkins"
                            '''
                        }
                    }
                }

                stage('Semver Init') {
                    when {
                        expression { params.REPO != '- select repo -' && params.NEW_BRANCH.trim() != '' }
                    }
                    steps {
                        script {
                            dir('semver') {
                                sshagent(credentials: ['edgex-jenkins-ssh']) {
                                    sh '''#!/bin/bash

                                    git checkout semver
                                    echo "$SEMVER_INIT" | tee $NEW_BRANCH
                                    if [[ -n $(git status -s) ]]; then
                                        echo "We have detected there are semver changes to commit..."
                                        git add .
                                        git commit -m "semver($NEW_BRANCH): init $SEMVER_INIT"
                                        git push origin semver
                                    else
                                        echo "Nothing to push...Exiting."
                                    fi
                                    '''
                                }
                            }
                        }
                    }
                }

                stage('Go Version') {
                    when {
                        expression { params.REPO != '- select repo -' && params.NEW_BRANCH.trim() != '' }
                    }
                    steps {
                        dir('repo') {
                            sshagent(credentials: ['edgex-jenkins-ssh']) {
                                sh '$WORKSPACE/go_version.sh'
                            }
                        }
                    }
                }

                stage('Push Branch') {
                    when {
                        expression { params.REPO != '- select repo -' && params.NEW_BRANCH.trim() != '' }
                    }
                    steps {
                        script {
                            dir('repo') {
                                sshagent(credentials: ['edgex-jenkins-ssh']) {
                                    sh '''#!/bin/bash

                                    if [[ -n $(git status -s) ]]; then
                                        echo "We have detected there are changes to commit..."
                                        git add .
                                        git commit -s -m "ci($NEW_BRANCH): automated changes for patch release branch"
                                        git push origin "$NEW_BRANCH"
                                    else
                                        echo "Nothing to push...Exiting."
                                    fi
                                    '''
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

def getEdgexRepos() {
    [
        '- select repo -', 'app-functions-sdk-go', 'app-record-replay',
        'app-rfid-llrp-inventory', 'app-service-configurable', 'device-bacnet-c',
        'device-coap-c', 'device-gpio', 'device-modbus-go', 'device-mqtt-go',
        'device-onvif-camera', 'device-rest-go', 'device-rfid-llrp-go',
        'device-sdk-c', 'device-sdk-go', 'device-snmp-go', 'device-uart',
        'device-usb-camera', 'device-virtual-go', 'edgex-compose',
        'edgex-examples', 'edgex-go', 'edgex-ui-go', 'go-mod-bootstrap',
        'go-mod-configuration', 'go-mod-core-contracts', 'go-mod-messaging',
        'go-mod-registry', 'go-mod-secrets', 'sample-service'
    ]
}