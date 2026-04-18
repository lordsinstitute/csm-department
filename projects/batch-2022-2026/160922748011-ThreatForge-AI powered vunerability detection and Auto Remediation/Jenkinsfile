pipeline {
    agent any

    environment {
        // DockerHub or ECR image name — update with your repo
        IMAGE_NAME      = "threatforge-api"
        IMAGE_TAG       = "${env.BUILD_NUMBER}"
        AWS_REGION      = "us-east-1"
        EC2_USER        = "ec2-user"
        // Store these in Jenkins → Manage Credentials
        DOCKERHUB_CREDS = credentials('dockerhub-credentials')
        EC2_HOST        = credentials('ec2-host')          // e.g. 1.2.3.4
        EC2_SSH_KEY     = credentials('ec2-ssh-key')       // private key file
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        // ── 1. Checkout ─────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Checked out branch: ${env.BRANCH_NAME}"
            }
        }

        // ── 2. Lint & Basic Checks ───────────────────────────────────────
        stage('Lint') {
            steps {
                sh '''
                    python3 -m pip install --quiet flake8
                    flake8 backend/app --max-line-length=120 --ignore=E501,W503 || true
                '''
            }
        }

        // ── 3. Build Docker Image ────────────────────────────────────────
        stage('Build') {
            steps {
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                """
                echo "✅ Docker image built: ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        // ── 4. Push to DockerHub ─────────────────────────────────────────
        stage('Push') {
            when {
                branch 'main'
            }
            steps {
                sh """
                    echo \${DOCKERHUB_CREDS_PSW} | docker login -u \${DOCKERHUB_CREDS_USR} --password-stdin
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} \${DOCKERHUB_CREDS_USR}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} \${DOCKERHUB_CREDS_USR}/${IMAGE_NAME}:latest
                    docker push \${DOCKERHUB_CREDS_USR}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push \${DOCKERHUB_CREDS_USR}/${IMAGE_NAME}:latest
                """
                echo "✅ Pushed to DockerHub"
            }
        }

        // ── 5. Deploy to EC2 ─────────────────────────────────────────────
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            # Pull latest image
                            docker pull \${DOCKERHUB_CREDS_USR}/${IMAGE_NAME}:latest

                            # Stop and remove old container
                            docker stop threatforge-api 2>/dev/null || true
                            docker rm   threatforge-api 2>/dev/null || true

                            # Run new container
                            docker run -d \\
                              --name threatforge-api \\
                              --restart unless-stopped \\
                              -p 8000:8000 \\
                              --env-file /home/ec2-user/threatforge/.env \\
                              -v threatforge_data:/app/backend/data \\
                              \${DOCKERHUB_CREDS_USR}/${IMAGE_NAME}:latest

                            # Prune old images to save disk
                            docker image prune -f
                        '
                    """
                }
                echo "✅ Deployed to EC2 at ${EC2_HOST}"
            }
        }

        // ── 6. Health Check ───────────────────────────────────────────────
        stage('Health Check') {
            when {
                branch 'main'
            }
            steps {
                sh """
                    sleep 15
                    curl -sf http://${EC2_HOST}:8000/health | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('ok') else 1)"
                """
                echo "✅ Health check passed"
            }
        }
    }

    post {
        success {
            echo "🎉 Pipeline succeeded — build #${env.BUILD_NUMBER}"
        }
        failure {
            echo "❌ Pipeline failed — check logs above"
        }
        always {
            // Clean up local Docker images to save Jenkins server space
            sh "docker rmi ${IMAGE_NAME}:${IMAGE_TAG} 2>/dev/null || true"
        }
    }
}