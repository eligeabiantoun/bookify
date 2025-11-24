pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Use Minikube Docker') {
            steps {
                sh '''
                  echo "Switching Docker to Minikube..."
                  eval $(minikube docker-env)
                  docker info > /dev/null
                '''
            }
        }

        stage('Build Docker images for services') {
            steps {
                sh '''
                  echo "Building Bookify service images..."

                  # FRONTEND
                  docker build -f frontend_service/Dockerfile -t bookify-frontend-service:latest frontend_service

                  # ACCOUNTS
                  docker build -f accounts_service/Dockerfile -t bookify-accounts-service:latest accounts_service

                  # BOOKING
                  docker build -f booking_service/Dockerfile -t bookify-booking-service:latest booking_service

                  # RESTAURANTS
                  docker build -f restaurants_service/Dockerfile -t bookify-restaurants-service:latest restaurants_service

                  # REVIEWS
                  docker build -f reviews_service/Dockerfile -t bookify-reviews-service:latest reviews_service

                  # SEARCH
                  docker build -f search_service/Dockerfile -t bookify-search-service:latest search_service
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                  echo "Applying Kubernetes manifests..."
                  kubectl apply -f k8s/

                  echo "Waiting for deployments to roll out..."
                  kubectl rollout status deployment/frontend-deployment -n bookify
                  kubectl rollout status deployment/accounts-deployment -n bookify
                  kubectl rollout status deployment/booking-deployment -n bookify
                  kubectl rollout status deployment/restaurants-deployment -n bookify
                  kubectl rollout status deployment/reviews-deployment -n bookify
                  kubectl rollout status deployment/search-deployment -n bookify
                '''
            }
        }
    }
}
