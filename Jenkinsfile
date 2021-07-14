def nexusImages = [
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/app-service-configurable:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/app-service-configurable/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/core-command:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/core-command/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/core-data:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/core-data/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/core-metadata:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/core-metadata/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/device-camera:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-camera-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/device-coap:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-coap-c/main/scripts/Dockerfile.alpine'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/device-gpio:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-gpio/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/device-rfid-llrp:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-rfid-llrp-go/main/Dockerfile'],
    [scratch: true,  image: 'nexus3.edgexfoundry.org:10004/device-modbus:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-modbus-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/device-mqtt:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-mqtt-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/device-rest:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-rest-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/device-snmp:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-snmp-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/device-virtual:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-virtual-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/edgex-ui:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-ui-go/main/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/security-bootstrapper:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/security-bootstrapper/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/security-proxy-setup:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/security-proxy-setup/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/security-secretstore-setup:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/security-secretstore-setup/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/support-notifications:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/support-notifications/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/support-scheduler:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/support-scheduler/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/sys-mgmt-agent:latest', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/main/cmd/sys-mgmt-agent/Dockerfile']
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