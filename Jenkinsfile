def nexusImages = [
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-app-service-configurable:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/app-service-configurable/master/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-camera-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-camera-go/master/Dockerfile'],
    [scratch: true, image: 'nexus3.edgexfoundry.org:10004/docker-device-modbus-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-modbus-go/master/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-mqtt-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-mqtt-go/master/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-random-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-random/master/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-rest-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-rest-go/master/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-snmp-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-snmp-go/master/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-device-virtual-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/device-virtual-go/master/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-edgex-consul:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/docker-edgex-consul/master/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-core-metadata-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/master/cmd/core-metadata/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-core-data-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/master/cmd/core-data/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-core-command-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/master/cmd/core-command/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-support-notifications-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/master/cmd/support-notifications/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-support-scheduler-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/master/cmd/support-scheduler/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-sys-mgmt-agent-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/master/cmd/sys-mgmt-agent/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-security-proxy-setup-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/master/cmd/security-proxy-setup/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-security-secretstore-setup-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/master/cmd/security-secretstore-setup/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-edgex-ui-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-ui-go/master/Dockerfile'],
    [scratch: false, image: 'nexus3.edgexfoundry.org:10004/docker-security-bootstrapper-go:master', dockerfile: 'https://raw.githubusercontent.com/edgexfoundry/edgex-go/master/cmd/security-bootstrapper/Dockerfile']
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