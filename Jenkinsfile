pipeline {
    agent { label 'centos7-docker-8c-8g' }
    triggers {
        cron('@weekly')
    }
    stages {
        stage('Prep') {
            steps {
                script {
                    sh "curl -v https://raw.githubusercontent.com/edgexfoundry/edgex-compose/master/docker-compose-pre-release.yml > docker-compose.yml"
                    docker
                        .image('nexus3.edgexfoundry.org:10003/edgex-devops/edgex-compose:latest')
                        .inside('-u 0:0 --entrypoint= --net host --security-opt label:disable -v /var/run/docker.sock:/var/run/docker.sock')
                    {
                        sh """
                            docker ps -a
                            docker-compose up -d
                            sleep 60
                            docker ps -a
                        """
                    }
                }
            }
        }

        stage('CIS Benchmark') {
            steps {
                script {
                    def checks = ['check_4_1','check_5_3','check_5_4','check_5_5','check_5_6','check_5_7',
                        'check_5_9','check_5_12','check_5_15','check_5_16','check_5_19','check_5_20',
                        'check_5_21','check_5_24','check_5_25','check_5_29','check_5_30','check_5_31'
                    ]
                    sh """
                        docker run --net host --pid host --cap-add audit_control \
                        -e DOCKER_CONTENT_TRUST= -v /var/lib:/var/lib -v /var/run/docker.sock:/var/run/docker.sock \
                        -v /usr/lib/systemd:/usr/lib/systemd -v /etc:/etc --label docker_bench_security \
                        docker/docker-bench-security -c ${checks.join(',')}
                    """
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