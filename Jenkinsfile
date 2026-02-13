pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'thrinadhprasadapu/wine-quality'
        REGISTRY_CREDENTIALS = 'dockerhub-creds'
    }

    stages {
        stage('Checkout') {
            steps {
                // Task 4 - Stage 1: Checkout
                checkout scm
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                // Task 4 - Stage 2: Setup Python Virtual Environment
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                // Task 4 - Stage 3: Train Model
                sh '''
                    . venv/bin/activate
                    python scripts/train.py
                '''
            }
        }

        stage('Read Accuracy') {
            steps {
                // Task 4 - Stage 4: Read Accuracy
                script {
                    env.CURRENT_ACCURACY = sh(script: "jq -r '.R2' app/artifacts/metrics.json", returnStdout: true).trim()
                    echo "Current R2 Score: ${env.CURRENT_ACCURACY}"
                }
            }
        }

        stage('Compare Accuracy') {
            steps {
                // Task 4 - Stage 5: Compare Accuracy
                withCredentials([string(credentialsId: 'best-accuracy', variable: 'BEST_ACCURACY')]) {
                    script {
                        def currentAcc = env.CURRENT_ACCURACY.toDouble()
                        def bestAcc = env.BEST_ACCURACY.toDouble()
                        
                        echo "Comparing Current: ${currentAcc} with Best: ${bestAcc}"
                        
                        if (currentAcc > bestAcc) {
                            env.IS_BETTER = 'true'
                            echo "Metric improved. Proceeding with deployment."
                        } else {
                            env.IS_BETTER = 'false'
                            echo "Metric did not improve. Model will not be deployed."
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                environment name: 'IS_BETTER', value: 'true'
            }
            steps {
                // Task 4 - Stage 6: Build Docker Image (Conditional)
                script {
                    docker.withRegistry('', REGISTRY_CREDENTIALS) {
                        dockerImage = docker.build("${env.DOCKER_IMAGE}:${env.BUILD_NUMBER}")
                    }
                }
            }
        }

        stage('Push Docker Image') {
            when {
                environment name: 'IS_BETTER', value: 'true'
            }
            steps {
                // Task 4 - Stage 7: Push Docker Image (Conditional)
                script {
                    docker.withRegistry('', REGISTRY_CREDENTIALS) {
                        dockerImage.push("${env.BUILD_NUMBER}")
                        dockerImage.push('latest')
                    }
                }
            }
        }
    }

    post {
        always {
            // Task 5: Artifact Archiving
            archiveArtifacts artifacts: 'app/artifacts/**', allowEmptyArchive: true
        }
    }
}
