pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker images') {
    steps {
        sh '''
            echo ">>> Building Bookify images (local Docker, no Docker Hub)"

            docker build -f frontend_service/Dockerfile    -t bookify-frontend-service:latest .
            docker build -f accounts_service/Dockerfile    -t bookify-accounts-service:latest .
            docker build -f booking_service/Dockerfile     -t bookify-booking-service:latest .
            docker build -f restaurants_service/Dockerfile -t bookify-restaurants-service:latest .
            docker build -f reviews_service/Dockerfile     -t bookify-reviews-service:latest .
            docker build -f search_service/Dockerfile      -t bookify-search-service:latest .
        '''
    }
}

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    echo ">>> Applying Kubernetes manifests"

                    kubectl apply -f k8s/ -n bookify

                    echo ">>> Restarting deployments"
                    kubectl rollout restart deployment/accounts-deployment      -n bookify
                    kubectl rollout restart deployment/booking-deployment       -n bookify
                    kubectl rollout restart deployment/restaurants-deployment   -n bookify
                    kubectl rollout restart deployment/reviews-deployment       -n bookify
                    kubectl rollout restart deployment/search-deployment        -n bookify
                    kubectl rollout restart deployment/frontend-deployment      -n bookify

                    echo ">>> Current pods:"
                    kubectl get pods -n bookify
                '''
            }
        }
    }
}
