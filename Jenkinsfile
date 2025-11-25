pipeline {
    agent any

    // 🔁 Poll GitHub every 2 minutes
    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                // Uses the repo configured in the Jenkins job
                checkout scm
            }
        }

        stage('Build Docker images') {
            steps {
                sh '''
                set -e
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
                set -e
                echo ">>> Using Jenkins kubeconfig"
                export KUBECONFIG="$WORKSPACE/k8s/jenkins-kubeconfig"

                echo ">>> Applying Kubernetes manifests"
                kubectl apply --validate=false -f k8s/ -n bookify

                echo ">>> Forcing rollout restart so pods pick up rebuilt images"
                kubectl rollout restart deployment/accounts-deployment    -n bookify
                kubectl rollout restart deployment/booking-deployment     -n bookify
                kubectl rollout restart deployment/restaurants-deployment -n bookify
                kubectl rollout restart deployment/reviews-deployment     -n bookify
                kubectl rollout restart deployment/search-deployment      -n bookify
                kubectl rollout restart deployment/frontend-deployment    -n bookify
                '''
            }
        }
    }
}
