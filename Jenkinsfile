pipeline {
    agent any

    // 🔁 Poll GitHub every 2 minutes
    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                // Use the repo configured in the job (you already have this working)
                checkout scm
                // If you want explicit Git instead, you could do:
                // git branch: 'main', url: 'https://github.com/eligeabiantoun/bookify.git'
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
            echo ">>> Using Jenkins kubeconfig"
            export KUBECONFIG=$WORKSPACE/k8s/jenkins-kubeconfig

            echo ">>> Applying Kubernetes manifests"
            kubectl apply --validate=false -f k8s/ -n bookify
        '''
    }
}
    }
}
