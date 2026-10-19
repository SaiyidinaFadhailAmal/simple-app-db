// Pipeline untuk Jenkins di Windows (Docker Desktop). Untuk agent Linux gunakan Jenkinsfile.linux.
pipeline {
    agent any

    options {
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    triggers {
        githubPush()
    }

         environment {
           saiyidinal
           IMAGE_NAME           = 'saiyidinal/simple-app-db'
           IMAGE_TAG            = "${env.BUILD_NUMBER}"
           REGISTRY_CREDENTIALS = 'dockerhub-credentials'
           COMPOSE_PROJECT_NAME = 'simple-app-db'
       }
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Test') {
            steps {
                // Tahap "test" pada Dockerfile menjalankan pytest saat build
                bat 'docker build --target test -t %IMAGE_NAME%-test:%IMAGE_TAG% .'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build --target runtime -t %IMAGE_NAME%:%IMAGE_TAG% -t %IMAGE_NAME%:latest .'
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.REGISTRY_CREDENTIALS,
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    bat 'echo %DH_PASS%| docker login -u %DH_USER% --password-stdin'
                    bat 'docker push %IMAGE_NAME%:%IMAGE_TAG%'
                    bat 'docker push %IMAGE_NAME%:latest'
                }
            }
        }

        stage('Deploy (App + MySQL)') {
            steps {
                bat 'docker compose up -d --remove-orphans'
            }
        }

        stage('Smoke Test') {
            steps {
                retry(10) {
                    sleep time: 6, unit: 'SECONDS'
                    bat 'curl.exe -fsS http://localhost:5000/health'
                }
            }
        }
    }

    post {
        always {
            bat 'docker logout'
            bat 'docker image rm %IMAGE_NAME%-test:%IMAGE_TAG% || exit 0'
            echo 'Selesai build'
        }
        success {
            echo "Build #${env.BUILD_NUMBER} sukses: ${env.IMAGE_NAME}:${env.IMAGE_TAG} berjalan di http://localhost:5000"
        }
        failure {
            bat 'docker compose logs --tail=50 || exit 0'
        }
    }
}
