pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('List project files') {
            steps {
                sh 'pwd'
                sh 'ls -R'
            }
        }

        stage('Run tests (placeholder)') {
            steps {
                sh 'echo "Here I would run Bookify tests"'
            }
        }
    }

    post {
        success {
            echo 'Pipeline OK ✅'
        }
        failure {
            echo 'Pipeline failed ❌'
        }
    }
}

