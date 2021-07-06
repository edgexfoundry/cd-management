def nexusImages = [
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-app-service-configurable:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/app-service-configurable/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-camera-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-camera-go/main/Dockerfile'],
    [scratch: true, image: 'nexus3.edgexfoundry.org:10004/docker-device-modbus-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-modbus-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-mqtt-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-mqtt-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-random-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-random/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-rest-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-rest-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-snmp-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-snmp-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-virtual-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-virtual-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-edgex-consul:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/docker-edgex-consul/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-core-metadata-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/core-metadata/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-core-data-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/core-data/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-core-command-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/core-command/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-support-notifications-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/support-notifications/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-support-scheduler-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/support-scheduler/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-sys-mgmt-agent-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/sys-mgmt-agent/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-security-proxy-setup-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/security-proxy-setup/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-security-secretstore-setup-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/security-secretstore-setup/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-edgex-ui-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-ui-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-security-bootstrapper-go:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/security-bootstrapper/Dockerfile']
]
pipeline {
    agent {
        label 'centos7-docker-4c-2g'
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