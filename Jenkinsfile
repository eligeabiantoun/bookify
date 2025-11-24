pipeline {
    agent any

    triggers {
        // Poll GitHub every 2 minutes
        pollSCM('H/2 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker images') {
    steps {
        sh '''
          echo "==== Building Bookify images ===="

          docker build -f frontend_service/Dockerfile    -t bookify-frontend-service:latest    .
          docker build -f accounts_service/Dockerfile    -t bookify-accounts-service:latest    .
          docker build -f booking_service/Dockerfile     -t bookify-booking-service:latest     .
          docker build -f restaurants_service/Dockerfile -t bookify-restaurants-service:latest .
          docker build -f reviews_service/Dockerfile     -t bookify-reviews-service:latest     .
          docker build -f search_service/Dockerfile      -t bookify-search-service:latest      .
        '''
    }
}


        stage('Deploy to Kubernetes') {
    steps {
        sh '''
          kubectl apply -n bookify -f k8s/

          kubectl rollout restart deployment/frontend-deployment      -n bookify
          kubectl rollout restart deployment/accounts-deployment      -n bookify
          kubectl rollout restart deployment/booking-deployment       -n bookify
          kubectl rollout restart deployment/restaurants-deployment   -n bookify
          kubectl rollout restart deployment/reviews-deployment       -n bookify
          kubectl rollout restart deployment/search-deployment        -n bookify

          kubectl rollout status deployment/frontend-deployment      -n bookify
          kubectl rollout status deployment/accounts-deployment      -n bookify
          kubectl rollout status deployment/booking-deployment       -n bookify
          kubectl rollout status deployment/restaurants-deployment   -n bookify
          kubectl rollout status deployment/reviews-deployment       -n bookify
          kubectl rollout status deployment/search-deployment        -n bookify
        '''
    }
}
    }
}
