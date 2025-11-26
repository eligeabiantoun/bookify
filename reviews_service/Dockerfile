pipeline {
    agent any
    triggers { pollSCM('H/2 * * * *') }
    environment {
        DOCKER_HOST = "unix:///var/run/docker.sock"
        KUBECONFIG  = "${WORKSPACE}/kubeconfig-minikube"
    }
    stages {
        stage('Checkout') { steps { checkout scm } }

        stage('Build reviews image') {
            when { changeset "reviews_service/**" }
            steps {
                sh '''
                    set -e
                    echo ">>> Building reviews image"
                    docker build -f reviews_service/Dockerfile \
                        -t bookify-reviews-service:latest .
                    docker images | grep bookify-reviews-service || true
                '''
            }
        }

        stage('Deploy search to Minikube') {
            when { changeset "reviews_service/**" }
            steps {
                sh '''
                    set -e
                    echo ">>> Applying search k8s manifest"
                    kubectl apply -f k8s/reviews-deployment.yaml

                    echo ">>> Waiting for rollout"
                    kubectl rollout status deployment/reviews-deployment -n bookify || \
                    kubectl rollout status deployment/reviews-deployment
                '''
            }
        }
    }
}
