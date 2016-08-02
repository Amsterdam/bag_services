#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


    String BRANCH = "${env.BRANCH_NAME}"
    String INVENTORY = (BRANCH == "master" ? "production" : "acceptance")

node {
    stage "Checkout"
        checkout scm

    stage "Test"
    tryStep "Test",  {
        sh "docker-compose -p bag -f .jenkins/docker-compose.yml run -u root --rm tests"
    }, {
        step([$class: "JUnitResultArchiver", testResults: "reports/junit.xml"])

        sh "docker-compose -p bag -f .jenkins/docker-compose.yml down"
    }

    stage "Build"

        def image = docker.build("admin.datapunt.amsterdam.nl:5000/datapunt/bag:${BRANCH}")
        image.push()

        if (BRANCH == "master") {
            image.push("latest")
        }
    }

node {
    stage name: "Deploy", concurrency: 1
    tryStep "deployment", {
        build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: INVENTORY],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-bag.yml'],
                        [$class: 'StringParameterValue', name: 'BRANCH', value: BRANCH],
                ]
    }
}