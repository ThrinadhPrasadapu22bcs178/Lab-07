pipeline {
    agent any

    environment {
        // Task 1: Prepare Test Inputs
        // Valid inference input matching the feature structure
        VALID_INPUT_QUERY = 'fixed_acidity=7.4&volatile_acidity=0.7&citric_acid=0&residual_sugar=1.9&chlorides=0.076&free_sulfur_dioxide=11&total_sulfur_dioxide=34&density=0.9978&ph=3.51&sulphates=0.56&alcohol=9.4'
        // Invalid input with missing fields and bad types
        INVALID_INPUT_QUERY = 'fixed_acidity=invalid_string_instead_of_float'

        DOCKER_IMAGE = 'thrinadhprasadapu/wine-quality:latest'
        CONTAINER_NAME = "inference-api-${BUILD_NUMBER}"
        API_PORT = '8000'
    }

    stages {
        stage('Pull Image') {
            steps {
                script {
                    echo "Pulling Docker image: ${env.DOCKER_IMAGE}"
                    def pullStatus = sh(script: "docker pull ${env.DOCKER_IMAGE}", returnStatus: true)
                    
                    if (pullStatus == 0) {
                        echo "Verify: Image download was successful."
                    } else {
                        error "Failed to pull Docker image."
                    }
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    echo "Starting container: ${env.CONTAINER_NAME} exposing port ${env.API_PORT}"
                    sh "docker run -d --name ${env.CONTAINER_NAME} -p ${env.API_PORT}:8000 ${env.DOCKER_IMAGE}"
                }
            }
        }

        stage('Wait for Service Readiness') {
            steps {
                script {
                    echo "Waiting for API to respond to health endpoint..."
                    def ready = false
                    
                    // Extract internal container IP instead of using localhost
                    env.CONTAINER_IP = sh(script: "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${env.CONTAINER_NAME}", returnStdout: true).trim()
                    echo "Container is running at IP: ${env.CONTAINER_IP}"

                    // Retry up to 15 times with 5 seconds delay (75s timeout)
                    for (int i = 0; i < 15; i++) {
                        def url = "http://${env.CONTAINER_IP}:8000/docs"
                        def res = sh(script: "curl -s -o /dev/null -w '%{http_code}' '${url}' || echo 'FAIL'", returnStdout: true).trim()
                        if (res == '200' || res == '307') {
                            ready = true
                            echo "Service is ready."
                            break
                        }
                        echo "Service not ready yet, retrying in 5 seconds..."
                        sleep(5)
                    }

                    if (!ready) {
                        error "Service did not start within timeout."
                    }
                }
            }
        }

        stage('Send Valid Inference Request') {
            steps {
                script {
                    echo "Sending valid inference request with input: ${env.VALID_INPUT_QUERY}"
                    def url = "http://${env.CONTAINER_IP}:8000/predict?${env.VALID_INPUT_QUERY}"
                    
                    // Task 4: Logging and Reporting - Jenkins console logs show API responses
                    def response = sh(script: "curl -s -w '\\nHTTP_STATUS:%{http_code}' '${url}'", returnStdout: true).trim()
                    echo "API Response Array:\n${response}"
                    
                    def respLines = response.split('\nHTTP_STATUS:')
                    def jsonBody = respLines[0]
                    def httpCode = respLines.size() > 1 ? respLines[1] : ""
                    
                    echo "Validation Check -> HTTP Status Code: ${httpCode}"
                    
                    if (httpCode != '200') {
                        error("Validation Failed: HTTP status code is ${httpCode}, expected 200.")
                    }
                    
                    def cmdExists = "echo '${jsonBody}' | jq -r 'has(\"wine_quality\")'"
                    def fieldExists = sh(script: cmdExists, returnStdout: true).trim()
                    if (fieldExists != 'true') {
                        error("Validation Failed: Prediction field 'wine_quality' does not exist in response.")
                    }
                    
                    def cmdValue = "echo '${jsonBody}' | jq -r '.wine_quality'"
                    def predictionValue = sh(script: cmdValue, returnStdout: true).trim()
                    echo "Validation Check -> Prediction Value: ${predictionValue}"
                    
                    if (!predictionValue.isNumber()) {
                        error("Validation Failed: Prediction value '${predictionValue}' is not numeric.")
                    }
                    
                    echo "Valid request successful. All validation checks passed."
                }
            }
        }

        stage('Send Invalid Request') {
            steps {
                script {
                    echo "Sending invalid inference request with input: ${env.INVALID_INPUT_QUERY}"
                    def url = "http://${env.CONTAINER_IP}:8000/predict?${env.INVALID_INPUT_QUERY}"
                    
                    // Task 4: Logging and Reporting - Jenkins console logs show API responses
                    def response = sh(script: "curl -s -w '\\nHTTP_STATUS:%{http_code}' '${url}'", returnStdout: true).trim()
                    echo "API Error Response Array:\n${response}"
                    
                    def respLines = response.split('\nHTTP_STATUS:')
                    def jsonBody = respLines[0]
                    def httpCode = respLines.size() > 1 ? respLines[1] : ""
                    
                    echo "Validation Check -> HTTP Status Code for Invalid: ${httpCode}"
                    
                    if (httpCode == '200') {
                        error("Validation Failed: Expected error response, but API returned 200 OK.")
                    } else {
                        echo "API returned error response as expected."
                    }
                    
                    def errorDetail = sh(script: "echo '${jsonBody}' | jq -r '.detail'", returnStdout: true).trim()
                    if (errorDetail == 'null' || errorDetail.isEmpty()) {
                        error("Validation Failed: Error message from API is not meaningful or not found.")
                    } else {
                        echo "Meaningful error message received: ${errorDetail}"
                    }
                }
            }
        }
        
        stage('Stop Container') {
            steps {
                script {
                    // Task 3: Stage 6 - Stop and remove container
                    echo "Stopping and removing container: ${env.CONTAINER_NAME}"
                    sh "docker stop ${env.CONTAINER_NAME} || true"
                    sh "docker rm ${env.CONTAINER_NAME} || true"
                    echo "Ensure no leftover running containers related to this pipeline run."
                }
            }
        }

        stage('Pipeline Result') {
            steps {
                script {
                    echo "Pipeline reached the end of validation steps successfully."
                    // Stage 7: Pipeline Result
                    // Mark pipeline successful only if all tests pass
                    currentBuild.result = 'SUCCESS'
                }
            }
        }
    }

    post {
        always {
            script {
                // Ensure we delete container on pipeline abort or error
                sh "docker stop ${env.CONTAINER_NAME} || true"
                sh "docker rm ${env.CONTAINER_NAME} || true"
            }
        }
        failure {
            script {
                // Task 3: Stage 7 - Mark pipeline failed if any validation step fails
                currentBuild.result = 'FAILURE'
                echo "Pipeline marked as failed due to validation errors."
            }
        }
    }
}
