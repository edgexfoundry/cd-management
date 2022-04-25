pipeline {
    agent { label 'centos7-docker-4c-2g' }
    parameters {
        string(name: 'BRANCH', defaultValue: '', description: 'Specify branch to generate')
        booleanParam(name: 'PUSH_BRANCH', defaultValue: false, description: 'Should the generated branch be pushed?')
    }
    stages {
        stage('Clone') {
            steps {
                dir('edgex-compose') {
                    git url: 'git@github.com:edgexfoundry/edgex-compose.git', branch: 'main', credentialsId: 'edgex-jenkins-ssh', changelog: false, poll: false
                }
            }
        }
        stage('Build Env File') {
            agent {
                dockerfile {
                    filename 'Dockerfile.build'
                    reuseNode true
                }
            }
            environment {
                GH_TOKEN = credentials('edgex-jenkins-github-personal-access-token')
            }
            steps {
                sh 'env-builder --envfile edgex-compose/compose-builder/.env --out .env.new'
                stash name: 'new-env', includes: '.env.new'
            }
        }
        stage('Generate Compose') {
            when {
                allOf {
                    triggeredBy 'UserIdCause'
                    expression { params.BRANCH.trim() != '' }
                }
            }
            stages {
                stage('Prep') {
                    steps {
                        dir('edgex-compose') {
                            script {
                                branchExists = sh(script: "git checkout ${params.BRANCH}", returnStatus: true)

                                // Branch does not exist
                                if(branchExists != 0) {
                                    echo "[edgex-compose-builder] ${params.BRANCH} does not exist. Creating new one."
                                    sh "git checkout -b ${params.BRANCH}"
                                }
                            }
                        }
                    }
                }

                stage('Compose Builder') {
                    agent {
                        docker {
                            image 'nexus3.edgexfoundry.org:10003/edgex-devops/edgex-compose:latest'
                            args  '--entrypoint='
                            reuseNode true
                        }
                    }
                    steps {
                        dir('edgex-compose/compose-builder') {
                            unstash 'new-env'
                            
                            // new custom changes. Remove WIP from gen-header
                            sh 'sed -i "s/WIP //g" gen-header'

                            sh 'mv .env.new .env'
                            sh 'ls -al .'
                            sh 'make build'
                        }
                    }

                }

                stage('Push Changes') {
                    when { expression { return params.PUSH_BRANCH } }
                    steps {
                        dir('edgex-compose') {
                            script {
                                // sh 'git diff'
                                def changesDetected = sh(script: 'git diff-index --quiet HEAD --', returnStatus: true)
                                echo "We have detected there are changes to commit: [${changesDetected}] [${changesDetected != 0}]"

                                if(changesDetected != 0) {
                                    sh 'git config --global user.email "jenkins@edgexfoundry.org"'
                                    sh 'git config --global user.name "EdgeX Jenkins"'
                                    sh 'git add .'
                                    sh "sudo chmod -R ug+w .git/*"

                                    sh "git commit -s -m 'ci: edgex-compose automation for ${params.BRANCH} release'"

                                    sshagent (credentials: ['edgex-jenkins-ssh']) {
                                        sh "git push origin ${params.BRANCH}"
                                    }
                                }
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
    }
}