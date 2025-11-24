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
        docker build -f frontend_service/Dockerfile -t bookify-frontend-service:latest .

        # ACCOUNTS SERVICE
        docker build -f accounts_service/Dockerfile -t bookify-accounts-service:latest .

        # BOOKING SERVICE
        docker build -f booking_service/Dockerfile -t bookify-booking-service:latest .

        # RESTAURANTS SERVICE
        docker build -f restaurants_service/Dockerfile -t bookify-restaurants-service:latest .

        # REVIEWS SERVICE
        docker build -f reviews_service/Dockerfile -t bookify-reviews-service:latest .

        # SEARCH SERVICE
        docker build -f search_service/Dockerfile -t bookify-search-service:latest .

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
