pipeline {
    agent any

    environment {
        // Set this to the namespace where your Bookify deployments are
        K8S_NAMESPACE = 'bookify'
    }

    // Check GitHub every 2 minutes for changes
    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                echo "📥 Pulling latest code from GitHub via SCM config..."
                // Uses the repo & branch you configured in the Jenkins job
                checkout scm
            }
        }

        stage('Build Docker Images (local only)') {
            steps {
                script {
                    // Microservice folders – each must contain a Dockerfile
                    def services = [
                        [name: 'accounts',     path: 'accounts'],
                        [name: 'booking',      path: 'booking'],
                        [name: 'restaurants',  path: 'restaurants'],
                        [name: 'reviews',      path: 'reviews'],
                        [name: 'search',       path: 'search'],
                        [name: 'frontend',     path: 'frontend']
                    ]

                    services.each { svc ->
                        def imageName = "bookify-${svc.name}:latest"

                        echo "🔨 Building local image ${imageName} from ./${svc.path}"

                        sh """
                            docker build -t ${imageName} ${svc.path}
                        """
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "🚀 Applying Kubernetes manifests in namespace: ${K8S_NAMESPACE}"
                    sh "kubectl apply -n ${K8S_NAMESPACE} -f k8s/"

                    echo "📊 Current pods:"
                    sh "kubectl get pods -n ${K8S_NAMESPACE}"
                }
            }
        }
    }

    post {
        success {
            echo "✅ Bookify pipeline succeeded for build #${env.BUILD_NUMBER}"
        }
        failure {
            echo "❌ Bookify pipeline FAILED for build #${env.BUILD_NUMBER} – check the logs above."
        }
    }
}
