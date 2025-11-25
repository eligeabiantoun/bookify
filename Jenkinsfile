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
                    echo ">>> Building Bookify images"

                    docker build frontend_service/          -t bookify-frontend-service:latest
                    docker build accounts_service/          -t bookify-accounts-service:latest
                    docker build booking_service/           -t bookify-booking-service:latest
                    docker build restaurants_service/       -t bookify-restaurants-service:latest
                    docker build reviews_service/           -t bookify-reviews-service:latest
                    docker build search_service/            -t bookify-search-service:latest
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
