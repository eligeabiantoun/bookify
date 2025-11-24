pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Rebuild Bookify (Docker Compose)') {
    steps {
        sh '''
        docker-compose down || true
        docker-compose build --no-cache
        docker-compose up -d
        '''
    }
}

        stage('Tests (optional)') {
            steps {
                sh 'echo "Tests would run here"'
            }
        }
    }

    post {
        success {
            echo '🚀 Bookify updated successfully!'
        }
        failure {
            echo '❌ Something went wrong.'
        }
    }
}
