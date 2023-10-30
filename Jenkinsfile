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
            description: 'Enter the semantic version to init the branch with. Example: 3.1.1'
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
                stage('Clone Repo') {
                    when {
                        expression { params.REPO != '- select repo -' }
                    }
                    steps {
                        dir('repo') {
                            git(
                                url: "git@github.com:edgexfoundry/${params.REPO}.git",
                                branch: params.BRANCH_SOURCE,
                                changelog: false,
                                poll: false,
                                credentialsId: 'edgex-jenkins-ssh'
                            )
                        }
                    }
                }

                stage('Create Patch Release') {
                    when {
                        expression { params.REPO != '- select repo -' && params.NEW_BRANCH.trim() != '' }
                    }
                    steps {
                        dir('repo') {
                            sh '''
                            git  ls-remote --exit-code --heads origin "refs/heads/$NEW_BRANCH"
                            if [ $? -eq 2 ]; then
                                # checkout new branch
                                git checkout -b "$NEW_BRANCH"

                                # update go version
                                if grep -q "goVersion" Jenkinsfile; then
                                    # This is a bit crude, but should work for all cases
                                    echo "Jenkinsfile already contains a goVersion, Updating..."

                                    go_version=$(grep goVersion Jenkinsfile | cut -d: -f 2)
                                    sed -i "s/$go_version/ '$GO_VERSION',/g" Jenkinsfile
                                    cat Jenkinsfile
                                else
                                    echo "Jenkinsfile does not contain goVersion, Pinning..."

                                    new_block=$(sed 's/^)/    goVersion: '$GO_VERSION'\\n)/g' Jenkinsfile | grep -v "//" | grep -v "(\\|)" | sed '/^$/d' | sed 's/,$//g' | sed 's/$/,/g')
                                    block_added=0
                                    while read line; do
                                        if echo "${line}" | grep -q ".*: .*"; then
                                            if [ $block_added -eq 0 ]; then
                                                echo "$new_block"
                                                block_added=1
                                            fi
                                        else
                                            echo "$line"
                                        fi
                                    done <<< "$(cat Jenkinsfile)" > Jenkinsfile.new
                                    cat Jenkinsfile.new
                                fi
                            else
                                echo "[$NEW_BRANCH] already exists. Exiting!"
                                exit 1
                            fi
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
                            edgeXSemver('init', params.SEMVER_INIT)
                        }
                    }
                }
            }
        }
    }
}

def getEdgexRepos() {
    ['- select repo -', 'app-functions-sdk-go', 'app-record-replay', 'app-rfid-llrp-inventory', 'app-service-configurable', 'device-bacnet-c', 'device-coap-c', 'device-gpio', 'device-modbus-go', 'device-mqtt-go', 'device-onvif-camera', 'device-rest-go', 'device-rfid-llrp-go', 'device-sdk-c', 'device-sdk-go', 'device-snmp-go', 'device-uart', 'device-usb-camera', 'device-virtual-go', 'edgex-compose', 'edgex-examples', 'edgex-go', 'edgex-ui-go', 'go-mod-bootstrap', 'go-mod-configuration', 'go-mod-core-contracts', 'go-mod-messaging', 'go-mod-registry', 'go-mod-secrets', 'sample-service']
}