pipeline {
    agent any
    
    environment {
        // Application Configuration
        APP_NAME = 'password-manager'
        AWS_REGION = 'us-east-1'
        
        // ECR Configuration
        ACCOUNT_ID = '503561414328'
        ECR_URL = "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_REPO = "${ECR_URL}/${APP_NAME}"
        
        // Image Tagging
        // Use first 12 characters of git commit hash, or 'dev' if not available
        IMAGE_TAG = "${env.GIT_COMMIT?.take(12) ?: 'dev'}"
        
        // Fix PATH for macOS
        PATH = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${env.PATH}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    // Display git commit info
                    sh(script: 'git log -1 --oneline', returnStdout: true)
                }
            }
        }
        
        stage('Setup Python') {
            steps {
                sh '''
                    #!/bin/bash
                    set -e
                    echo "Setting up Python virtual environment..."
                    python3 -m venv .venv
                    source .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    echo "✓ Python environment ready"
                '''
            }
        }
        
        stage('Lint & Tests') {
            steps {
                script {
                    // Run flake8 if available (don't fail build)
                    sh '''
                        #!/bin/bash
                        set -e
                        source .venv/bin/activate
                        if command -v flake8 &> /dev/null || pip show flake8 &> /dev/null; then
                            echo "Running flake8..."
                            flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                            flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || true
                        else
                            echo "flake8 not installed, skipping linting"
                        fi
                    '''
                    
                    // Run tests
                    sh '''
                        #!/bin/bash
                        set -e
                        source .venv/bin/activate
                        echo "Running tests..."
                        make test
                        echo "✓ Tests completed"
                    '''
                }
            }
            post {
                always {
                    // Publish JUnit test results
                    junit 'reports/junit.xml'
                    
                    // Archive coverage reports
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
                    
                    // Publish HTML coverage if exists
                    script {
                        if (fileExists('htmlcov/index.html')) {
                            publishHTML([
                                reportName: 'Coverage Report',
                                reportDir: 'htmlcov',
                                reportFiles: 'index.html',
                                keepAll: true
                            ])
                        }
                    }
                }
            }
        }
        
        stage('SonarQube Analysis & Quality Gate') {
            steps {
                script {
                    // Check if sonar-project.properties exists
                    if (fileExists('sonar-project.properties')) {
                        echo "✓ Running SonarQube analysis using Docker..."
                        withSonarQubeEnv('sonar-local') {
                            // Track if scanner actually ran
                            def scannerRan = false
                            
                            // Use Docker to run sonar-scanner (no local installation needed)
                            // Note: withSonarQubeEnv sets SONAR_HOST_URL and SONAR_TOKEN environment variables
                            def scannerOutput = sh(
                                script: '''
                                    #!/bin/bash
                                    set -e
                                    
                                    # Check if Docker is available
                                    if ! command -v docker &> /dev/null; then
                                        echo "⚠ Docker not found, skipping SonarQube analysis"
                                        exit 0
                                    fi
                                    
                                    # Check if SonarQube environment variables are set
                                    if [ -z "${SONAR_HOST_URL}" ] || [ -z "${SONAR_TOKEN}" ]; then
                                        echo "⚠ SonarQube credentials not configured, skipping analysis"
                                        echo "Configure SonarQube in Jenkins: Manage Jenkins → Configure System → SonarQube servers"
                                        echo "SONAR_HOST_URL=${SONAR_HOST_URL}"
                                        echo "SONAR_TOKEN=${SONAR_TOKEN}"
                                        exit 0
                                    fi
                                    
                                    # Convert localhost:9000 to host.docker.internal:9000 for Docker container access
                                    # Docker containers can't access localhost on the host, need host.docker.internal
                                    SONAR_URL="${SONAR_HOST_URL}"
                                    if [[ "${SONAR_URL}" == *"localhost"* ]] || [[ "${SONAR_URL}" == *"127.0.0.1"* ]]; then
                                        SONAR_URL=$(echo "${SONAR_URL}" | sed 's/localhost/host.docker.internal/g' | sed 's/127.0.0.1/host.docker.internal/g')
                                        echo "Updated SonarQube URL for Docker: ${SONAR_URL}"
                                    fi
                                    
                                    echo "SonarQube URL: ${SONAR_URL}"
                                    echo "SonarQube Token: ${SONAR_TOKEN:0:10}..." # Show first 10 chars for debugging
                                    
                                    # Run sonar-scanner via Docker
                                    # Mount current directory and use sonar-scanner Docker image
                                    # Pass SonarQube properties as environment variables (scanner reads SONAR_HOST_URL and SONAR_TOKEN)
                                    # The scanner will write report-task.txt to the mounted directory
                                    docker run --rm \\
                                        -v "$(pwd):/usr/src" \\
                                        -w /usr/src \\
                                        -e SONAR_HOST_URL="${SONAR_URL}" \\
                                        -e SONAR_TOKEN="${SONAR_TOKEN}" \\
                                        sonarsource/sonar-scanner-cli:latest
                                    
                                    echo "✓ SonarQube analysis completed"
                                    
                                    # Verify report-task.txt was created (contains task ID for quality gate)
                                    if [ -f ".scannerwork/report-task.txt" ]; then
                                        echo "✓ report-task.txt found"
                                        cat .scannerwork/report-task.txt
                                        echo "SCANNER_RAN=yes"
                                    else
                                        echo "⚠ report-task.txt not found"
                                        echo "SCANNER_RAN=no"
                                    fi
                                ''',
                                returnStdout: true
                            )
                            
                            // Check if scanner actually ran
                            if (scannerOutput.contains('SCANNER_RAN=yes')) {
                                scannerRan = true
                                echo scannerOutput
                            } else {
                                echo scannerOutput
                                echo "⚠ SonarQube scanner did not run, skipping quality gate"
                            }
                            
                            // Wait for quality gate only if scanner ran successfully
                            if (scannerRan && fileExists('.scannerwork/report-task.txt')) {
                                script {
                                    echo "Waiting for SonarQube Quality Gate..."
                                    timeout(time: 5, unit: 'MINUTES') {
                                        waitForQualityGate abortPipeline: true
                                    }
                                }
                            } else {
                                echo "⚠ Skipping quality gate - SonarQube analysis did not complete"
                                echo "Fix: Configure SonarQube token in Jenkins → Manage Jenkins → Configure System → SonarQube servers"
                            }
                        }
                    } else {
                        echo "⚠ sonar-project.properties not found, skipping SonarQube analysis"
                    }
                }
            }
        }
        
        stage('Docker Build & Push') {
            steps {
                script {
                    // Ensure ECR repository exists
                    sh """
                        #!/bin/bash
                        set -e
                        echo "Checking ECR repository..."
                        if ! aws ecr describe-repositories --repository-names ${APP_NAME} --region ${AWS_REGION} &>/dev/null; then
                            echo "Creating ECR repository..."
                            aws ecr create-repository \\
                                --repository-name ${APP_NAME} \\
                                --region ${AWS_REGION} \\
                                --image-scanning-configuration scanOnPush=true \\
                                --encryption-configuration encryptionType=AES256
                        else
                            echo "✓ ECR repository exists"
                        fi
                    """
                    
                    // Login to ECR
                    sh """
                        #!/bin/bash
                        set -e
                        echo "Logging into ECR..."
                        aws ecr get-login-password --region ${AWS_REGION} | \\
                            docker login --username AWS --password-stdin ${ECR_URL}
                        echo "✓ ECR login successful"
                    """
                    
                    // Build Docker image with multiple tags
                    sh """
                        #!/bin/bash
                        set -e
                        echo "Building Docker image..."
                        docker build \\
                            --platform linux/amd64 \\
                            -t ${ECR_REPO}:${IMAGE_TAG} \\
                            -t ${ECR_REPO}:latest \\
                            .
                        echo "✓ Docker image built"
                    """
                    
                    // Push both tags
                    sh """
                        #!/bin/bash
                        set -e
                        echo "Pushing Docker images..."
                        docker push ${ECR_REPO}:${IMAGE_TAG}
                        docker push ${ECR_REPO}:latest
                        echo "✓ Images pushed to ECR"
                    """
                }
            }
        }
        
        stage('Deploy to EC2') {
            when {
                // Only deploy on main/master branch
                // Also check if branch name is null (manual trigger) - allow deployment
                anyOf {
                    branch 'main'
                    branch 'master'
                    expression { 
                        // Allow deployment if branch is null (manual trigger) or if we're on main/master
                        return env.BRANCH_NAME == null || 
                               env.BRANCH_NAME == 'main' || 
                               env.BRANCH_NAME == 'master' ||
                               env.GIT_BRANCH == 'origin/main' ||
                               env.GIT_BRANCH == 'origin/master'
                    }
                }
            }
            steps {
                script {
                    // TODO: Replace <EC2_PUBLIC_IP> with your EC2 instance public IP
                    def EC2_HOST = '54.198.152.202'
                    def EC2_USER = 'ec2-user'
                    
                    sshagent(credentials: ['ec2-ssh']) {
                        sh """
                            #!/bin/bash
                            set -e
                            echo "Deploying to EC2..."
                            
                            ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << 'ENDSSH'
                                #!/bin/bash
                                set -e
                                cd /opt/password-manager
                                
                                # Login to ECR
                                echo "Logging into ECR..."
                                export AWS_REGION=${AWS_REGION}
                                export ACCOUNT_ID=${ACCOUNT_ID}
                                aws ecr get-login-password --region \${AWS_REGION} | \\
                                    docker login --username AWS --password-stdin \${ACCOUNT_ID}.dkr.ecr.\${AWS_REGION}.amazonaws.com
                                
                                # Set image tag
                                export TAG=${IMAGE_TAG}
                                echo "Deploying tag: \${TAG}"
                                
                                # Fetch environment variables
                                ./fetch-env.sh
                                
                                # Update docker-compose.yml with new tag
                                sed -i "s|image:.*|image: \${ACCOUNT_ID}.dkr.ecr.\${AWS_REGION}.amazonaws.com/${APP_NAME}:\${TAG}|" docker-compose.yml
                                
                                # Pull and start
                                docker compose pull
                                docker compose up -d
                                
                                # Health check loop (up to 20 tries, 5 seconds apart)
                                echo "Waiting for application to be healthy..."
                                MAX_TRIES=20
                                TRIES=0
                                while [ \$TRIES -lt \$MAX_TRIES ]; do
                                    if curl -f http://localhost/health &>/dev/null; then
                                        echo "✓ Application is healthy!"
                                        exit 0
                                    fi
                                    TRIES=\$((TRIES + 1))
                                    echo "Health check attempt \$TRIES/\$MAX_TRIES failed, retrying in 5 seconds..."
                                    sleep 5
                                done
                                
                                # Health check failed - rollback
                                echo "✗ Health check failed after \$MAX_TRIES attempts"
                                echo "Rolling back to latest tag..."
                                
                                # Rollback to latest
                                sed -i "s|image:.*|image: \${ACCOUNT_ID}.dkr.ecr.\${AWS_REGION}.amazonaws.com/${APP_NAME}:latest|" docker-compose.yml
                                docker compose pull
                                docker compose up -d
                                
                                echo "Rollback complete, but deployment failed"
                                exit 1
ENDSSH
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Clean workspace
            cleanWs()
            
            // Summary
            script {
                echo """
                    ==========================================
                    Pipeline Summary
                    ==========================================
                    Branch: ${env.BRANCH_NAME}
                    Commit: ${env.GIT_COMMIT?.take(12) ?: 'N/A'}
                    Image Tag: ${IMAGE_TAG}
                    ECR Repository: ${ECR_REPO}
                    ==========================================
                """
            }
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}

