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

        stage('Static Code Analysis') {
            steps {
                script {
                    // 1. Hadolint: Check Dockerfiles for best practices
                    // Runs instantly, no DB download
                    echo 'Running Hadolint on Dockerfiles...'
                    sh 'docker run --rm -i hadolint/hadolint < client/Dockerfile || true' // || true to not fail build on warnings yet
                    sh 'docker run --rm -i hadolint/hadolint < backend/Dockerfile || true'

                    // 2. Bandit: Check Python Backend for security issues
                    // Runs in a small python container, installs bandit (~2MB), runs scan
                    echo 'Running Bandit on Backend...'
                    sh 'docker run --rm -v $PWD/backend:/app -w /app python:3.8-slim sh -c "pip install bandit -q && bandit -r ."'
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
                        sleep 25
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
