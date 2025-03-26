// Copyright (c) 2025 IOTech Ltd.

def jobs = []

def bumpStage(job, branch) {
    return {
        def cloneUrl = job.split('"clone_url": "')[1].replaceAll('",','')
        def repoUrl = cloneUrl.split('\\.git')[0]
        def repoUrlSplit = repoUrl.split('edgexfoundry\\/')
        if (repoUrlSplit.size() > 1){
            def name = repoUrlSplit[1]
            stage(name) {
                sh "git clone --branch ${branch} ${cloneUrl}"
                dir(name) {
                    def tagExists = sh(script: "git ls-remote --tags origin v${params.Version}", returnStdout: true).trim()
                    if (!tagExists){
                        withEnv(["GIT_BRANCH=${branch}"]) {
                            edgeXSemver('init', env.Version)
                            edgeXSemver('push')
                        }
                    } else {
                        echo "Bump '${name}' Semver skipped due to tag 'v${params.Version}' already exists"
                    }
                }
            }
        }
    }
}

pipeline {
    agent { label 'ubuntu20.04-docker-8c-8g' }
    options {
        timestamps()
    }
    parameters {
        string(name: 'Version', defaultValue: '', description: 'Version to update.(e.g. 4.1.0-dev.1)')
        string(
            name: 'Query',
            defaultValue: 'go+OR+app+OR+device',
            description:
            '''Search query to use to select which repositories to update the version file for.
            <br>
            <br>Default: "go+OR+app+OR+device", all un-archived repositories using semantic versioning within the edgexfoundry Github organization will be selected.
            <br>Example: "device", all repositories with *device* in title will be selected.
            <br>Example: "go-mod+NOT+device", all go-mod repositories will be selected.
            '''
        )
        string(
            name: 'Branch',
            defaultValue: 'main',
            description:
            '''Target semver file to update.
            <br>
            <br>Default: main
            '''
        )
    }
    stages {
        stage('Bump Version') {
            when {
                expression { params.Version.trim() =~ /^(0|([1-9]\d*))\.(0|([1-9]\d*))\.(0|([1-9]\d*))-dev\.([1-9]\d*)$/ }
            }
            steps {
                script {
                    jobs = sh (
                        script: "curl -i \"https://api.github.com/search/repositories?q=user:edgexfoundry+archived:false+${params.Query}&per_page=200&sort=name&order=asc\" | grep clone_url",
                        returnStdout: true).trim().split("\n")
                    echo "parallel jobs: ${jobs}"
                    parallel jobs.collectEntries {[(it.split('edgexfoundry/')[1].split('.git')[0]) : bumpStage(it, params.Branch)]}
                }
            }
        }
    }
    post {
        cleanup {
            cleanWs()
        }
    }
}
