pipeline {
    agent any

    environment {
        // Replace with your Docker Hub username
        DOCKER_HUB_USER = "salahod"
        REGISTRY_CREDENTIALS_ID = 'docker-hub-credentials'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Security Scan (SAST)') {
            steps {
                script {
                    // Scan filesystem for vulnerabilities (Code + Dependencies)
                    // We use the dockerized version of Trivy to avoid installing it on the agent
                    // --exit-code 0 means don't fail build yet (change to 1 to enforce security)
                    // --severity CRITICAL,HIGH limits noise
                    sh 'docker run --rm -v $PWD:/app -w /app aquasec/trivy fs . --severity CRITICAL,HIGH --no-progress'
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    sh 'docker compose build'
                }
            }
        }

        stage('Security Scan (Image)') {
            steps {
                script {
                    // Scan the built images
                    // Need to mount docker socket to see local images
                    sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image react-flask-mongodb-v1-api:latest --severity CRITICAL,HIGH --no-progress"
                    sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image react-flask-mongodb-v1-client:latest --severity CRITICAL,HIGH --no-progress"
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    try {
                        // Start containers in detached mode
                        sh 'docker compose up -d'
                        
                        // Simple health check: wait for API to be responsive
                        // In a real scenario, use a specific healthcheck script or endpoint test
                        sleep 10
                        sh 'curl --fail http://localhost:5000/api/tasks || exit 1'
                        echo "API Test Passed"
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error("Test failed: ${e.message}")
                    } finally {
                        // Clean up resources even if test fails
                        sh 'docker compose down'
                    }
                }
            }
        }

        stage('Push') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${REGISTRY_CREDENTIALS_ID}") {
                        // Tag and push images
                        // You need to ensure your docker-compose builds images with these names
                        // or tag them manually here.
                        // Example if docker-compose built 'react-flask-mongodb-v1-api':
                        sh "docker tag react-flask-mongodb-v1-api ${DOCKER_HUB_USER}/react-flask-mongodb-v1-api:latest"
                        sh "docker push ${DOCKER_HUB_USER}/react-flask-mongodb-v1-api:latest"
                        
                        sh "docker tag react-flask-mongodb-v1-client ${DOCKER_HUB_USER}/react-flask-mongodb-v1-client:latest"
                        sh "docker push ${DOCKER_HUB_USER}/react-flask-mongodb-v1-client:latest"
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
