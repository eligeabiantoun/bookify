pipeline {
    agent any

    // 🔁 Poll GitHub every 2 minutes (like the tutorial)
    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        // So kubectl can see your config
        KUBECONFIG = "${HOME}/.kube/config"
    }

    stages {

        stage('Checkout') {
            steps {
                // OPTION A (recommended if job is "Pipeline script from SCM"):
                checkout scm

                // OPTION B (if you are using "Pipeline script" and not SCM):
                // git branch: 'main', url: 'YOUR_GITHUB_URL'
            }
        }

        stage('Build in Minikube Docker') {
            steps {
                sh '''
                  echo "==== Switch Docker to Minikube ===="
                  eval $(minikube docker-env)
                  docker info > /dev/null

                  echo "==== Build Bookify images ===="

                 docker build -f frontend_service/Dockerfile -t bookify-frontend-service:latest .
                 docker build -f accounts_service/Dockerfile -t bookify-accounts-service:latest .
                 docker build -f booking_service/Dockerfile -t bookify-booking-service:latest .
                 docker build -f restaurants_service/Dockerfile -t bookify-restaurants-service:latest .
                 docker build -f reviews_service/Dockerfile -t bookify-reviews-service:latest .
                 docker build -f search_service/Dockerfile -t bookify-search-service:latest .
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                  echo "==== Apply Kubernetes manifests ===="
                  kubectl apply -f k8s/

                  echo "==== Wait for rollouts ===="
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
