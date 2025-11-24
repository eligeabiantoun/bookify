pipeline {
    agent any

    environment {
        // Your Docker Hub username
        DOCKER_USER = 'eligeabiantoun'

        // EXACT Jenkins credentials ID you gave me
        REGISTRY_CREDENTIALS = '59f3eecc-8523-4749-8d42-64879ca4c0e9'

        // Your Kubernetes namespace
        K8S_NAMESPACE = 'bookify'
    }

    // Check GitHub every 2 minutes (like your tutorial)
    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                checkout scm
            }
        }

        stage('Build & Push Docker Images') {
            steps {
                script {
                    // Your microservice folders
                    def services = [
                        [name: 'accounts',     path: 'accounts'],
                        [name: 'booking',      path: 'booking'],
                        [name: 'restaurants',  path: 'restaurants'],
                        [name: 'reviews',      path: 'reviews'],
                        [name: 'search',       path: 'search'],
                        [name: 'frontend',     path: 'frontend']
                    ]

                    // Login to Docker Hub using your Jenkins credentials
                    withCredentials([usernamePassword(
                        credentialsId: REGISTRY_CREDENTIALS,
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_PASS'
                    )]) {

                        sh '''
                            echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        '''

                        services.each { svc ->
                            def imageTag  = "${DOCKERHUB_USER}/bookify-${svc.name}:${env.BUILD_NUMBER}"
                            def latestTag = "${DOCKERHUB_USER}/bookify-${svc.name}:latest"

                            echo "🔨 Building image ${imageTag} from ${svc.path}"

                            sh """
                                docker build -t ${imageTag} ${svc.path}
                                docker tag ${imageTag} ${latestTag}
                                docker push ${imageTag}
                                docker push ${latestTag}
                            """
                        }

                        // optional: logout
                        sh 'docker logout || true'
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "🚀 Deploying Bookify to Kubernetes namespace: ${K8S_NAMESPACE}"
                    // Your manifests folder
                    sh "kubectl apply -n ${K8S_NAMESPACE} -f k8s/"
                    sh "kubectl get pods -n ${K8S_NAMESPACE}"
                }
            }
        }
    }

    post {
        success {
            echo "✅ Bookify CI/CD pipeline succeeded for build #${env.BUILD_NUMBER}"
        }
        failure {
            echo "❌ Bookify CI/CD pipeline FAILED for build #${env.BUILD_NUMBER} – check the stages above."
        }
    }
}
