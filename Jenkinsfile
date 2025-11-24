pipeline {
    agent any

    environment {
        // 🔁 CHANGE THIS to your real Docker Hub username
        DOCKER_USER = 'YOUR_DOCKERHUB_USERNAME'

        // ID of Docker Hub credentials in Jenkins (Username+Password)
        REGISTRY_CREDENTIALS = 'dockerhub'

        // Kubernetes namespace
        K8S_NAMESPACE = 'bookify'
    }

    // Same as the tutorial: poll Git every 2 minutes
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
                    def services = [
                        [name: 'accounts',     path: 'accounts'],
                        [name: 'booking',      path: 'booking'],
                        [name: 'restaurants',  path: 'restaurants'],
                        [name: 'reviews',      path: 'reviews'],
                        [name: 'search',       path: 'search'],
                        [name: 'frontend',     path: 'frontend']
                    ]

                    // Login to Docker Hub using Jenkins credentials
                    withCredentials([usernamePassword(
                        credentialsId: REGISTRY_CREDENTIALS,
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_PASS'
                    )]) {
                        sh '''
                            echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        '''

                        services.each { svc ->
                            def imageTag   = "${DOCKERHUB_USER}/bookify-${svc.name}:${env.BUILD_NUMBER}"
                            def latestTag  = "${DOCKERHUB_USER}/bookify-${svc.name}:latest"

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
