def nexusImages = [
    [scratch: false, image: 'nexus3.edgexfoundry.org:10003/edgex-devops/edgex-golang-base:1.17-alpine', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/ci-build-images/golang-1.17/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10002/edgex-devops/edgex-golang-base:1.17-alpine-lts', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/ci-build-images/golang-1.17-lts/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10003/edgex-devops/edgex-golang-base:1.18-alpine', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/ci-build-images/golang-1.18/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10003/edgex-devops/edgex-gcc-base:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/ci-build-images/gcc/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10002/edgex-devops/edgex-gcc-base:gcc-lts', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/ci-build-images/gcc-lts/Dockerfile'],
]
pipeline {
    agent {
        label 'ubuntu18.04-docker-8c-8g'
    }
    options {
        timestamps()
    }
    parameters {
        string(
            name: 'EmailRecipients',
            defaultValue: 'security-issues@lists.edgexfoundry.org',
            description: 'The email recipients for Synk HTML report')
    }
    triggers {
        cron '@weekly'
    }
    stages {
        stage('Run Snyk scan') {
            when {
                anyOf {
                    triggeredBy 'UserIdCause'
                    triggeredBy 'TimerTrigger'
                }
            }
            steps {
                script {
                    nexusImages.each {
                        try{
                            if (!it.scratch){
                                sh 'rm -rf Dockerfile'
                                sh "curl -s ${it.dockerfile} > Dockerfile"
                                edgeXSnyk(
                                    command: 'test',
                                    dockerImage: it.image,
                                    dockerFile: 'Dockerfile',
                                    severity: 'high',
                                    sendEmail: true,
                                    emailTo: params.EmailRecipients,
                                    htmlReport: true
                                )
                            }
                        }catch (Exception ex){
                            println "[ERROR]: ${ex}"
                        }

                    }
                }
            }
        }
    }
}