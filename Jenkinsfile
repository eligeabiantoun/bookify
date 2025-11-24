pipeline {
    agent any

    environment {
        DOCKER_USER = 'YOUR_DOCKERHUB_USERNAME'
        REGISTRY_CREDENTIALS = 'dockerhub'
        K8S_NAMESPACE = 'bookify'
    }

    triggers {
        pollSCM('H/2 * * * *')   // Every 2 minutes (same as tutorial)
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

                    docker.withRegistry('https://registry.hub.docker.com', REGISTRY_CREDENTIALS) {

                        services.each { svc ->
                            def tag = "${DOCKER_USER}/bookify-${svc.name}:${env.BUILD_NUMBER}"
                            def latest = "${DOCKER_USER}/bookify-${svc.name}:latest"

                            echo "Building image ${tag}"

                            def img = docker.build(tag, "./${svc.path}")

                            echo "Pushing image ${tag}"
                            img.push()

                            echo "Tagging and pushing latest"
                            sh "docker tag ${tag} ${latest}"
                            sh "docker push ${latest}"
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "Deploying Bookify to Kubernetes..."
                    sh "kubectl apply -n ${K8S_NAMESPACE} -f k8s/"
                    sh "kubectl get pods -n ${K8S_NAMESPACE}"
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Build #${env.BUILD_NUMBER} deployed successfully!"
        }
        failure {
            echo "❌ Build #${env.BUILD_NUMBER} failed."
        }
    }
}
