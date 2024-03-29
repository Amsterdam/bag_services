#!groovy

String PLAYBOOK = 'deploy.yml'

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block()
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t
    }
    finally {
        if (tearDown) {
            tearDown()
        }
    }
}

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH != "master") {
    node {
        stage("Checkout") {
            checkout scm
        }

        stage('Test') {
            tryStep "test", {
                sh ".jenkins-test/test.sh"
            }
        }

        stage("Build image") {
            tryStep "build", {
                    docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    def image = docker.build("datapunt/bag_services:${env.BUILD_NUMBER}", ".")
                    image.push()
                }
            }
        }
    }
}

if (BRANCH == "master") {

    node {
        stage("Checkout") {
            checkout scm
        }

        stage('Test') {
            tryStep "test", {
                sh ".jenkins-test/test.sh"
            }
        }

        stage("Build image") {
            tryStep "build", {
                    docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    def image = docker.build("datapunt/bag_v11:${env.BUILD_NUMBER}")
                    image.push()
                }
            }
        }
    }

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    def image = docker.image("datapunt/bag_v11:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("acceptance")
                }
            }
        }
    }

    node {
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: "${PLAYBOOK}"],
                    [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_bag_v11"],
                ]
            }
        }
    }

    stage('Waiting for approval') {
        slackSend channel: '#ci-channel', color: 'warning', message: 'BAG is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                def image = docker.image("datapunt/bag_v11:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("production")
                    image.push("latest")
                }
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: "${PLAYBOOK}"],
                    [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_bag_v11"],
                ]
            }
        }
    }
}
