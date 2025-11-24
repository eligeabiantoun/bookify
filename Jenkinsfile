pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker images for services') {
            steps {
                sh '''
                echo "Building Bookify service images..."

                # FRONTEND SERVICE
                docker build -t bookify-frontend-service:latest ./frontend_service

                # ACCOUNTS SERVICE
                docker build -t bookify-accounts-service:latest ./accounts_service

                # BOOKING SERVICE
                docker build -t bookify-booking-service:latest ./booking_service

                # RESTAURANTS SERVICE
                docker build -t bookify-restaurants-service:latest ./restaurants_service

                # REVIEWS SERVICE
                docker build -t bookify-reviews-service:latest ./reviews_service

                # SEARCH SERVICE
                docker build -t bookify-search-service:latest ./search_service

                echo "All service images built."
                '''
            }
        }

        stage('Tests (optional)') {
            steps {
                sh 'echo "Here I would run tests (pytest, manage.py test, etc.)"'
            }
        }
    }

    post {
        success {
            echo '🚀 Bookify Docker images built successfully!'
        }
        failure {
            echo '❌ Pipeline failed.'
        }
    }
}
