pipeline {
    agent any

    environment {
        
        DOCKER_HUB_USER = "salahod"
        REGISTRY_CREDENTIALS_ID = 'docker-hub-credentials'
        COMPOSE_PROJECT_NAME = "react-flask-mongodb-v1"
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
                       
                        sleep 30
                        sh '''
                            docker run --rm --network react-flask-mongodb-v1_backend curlimages/curl -v --fail http://api:5000/api/tasks || (docker logs react-flask-mongodb-v1-api-1 && exit 1)
                        '''
                        echo "API Test Passed"
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error("Test failed: ${e.message}")
                    } finally {
                        // Clean up resources even if test fails
                        sh 'docker compose down -v'
                    }
                }
            }
        }

        stage('Push') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${REGISTRY_CREDENTIALS_ID}") {
                        // Tag and push images
                        
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
