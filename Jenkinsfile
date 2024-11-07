pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "revhire:latest"
        DOCKER_CREDENTIALS_ID = 'gopika'
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/vamsimalle1790/revhire.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    bat "docker build -t %DOCKER_IMAGE% ."
                }
            }        
        }
        stage('Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
                        bat "docker tag %DOCKER_IMAGE% krishnak3/%DOCKER_IMAGE%"
                        bat "docker push krishnak3/%DOCKER_IMAGE%"
                    }
                }
            }        
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
