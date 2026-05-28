pipeline {
    agent any

    environment {
        AWS_REGION            = 'eu-west-1'
        ECR_REPOSITORY_NAME   = 'repo1'
        EC2_USER              = 'root'
        EC2_HOST              = "${env.HOST}"
        SSH_CREDENTIAL_ID     = 'ssh-target'
        AWS_ACCESS_KEY_ID     = credentials('aws_access_key_id')
        AWS_SECRET_ACCESS_KEY = credentials('aws_secret_access_key')
        VENV_DIR              = '/opt/jenkins-venv'
    }

    stages {
        stage('Fetch Images') {
            steps {
                sh "${VENV_DIR}/bin/python fetch-ecr-images.py > image_tags.txt"
                script {
                    env.IMAGE_LIST = readFile('image_tags.txt').trim()
                }
                echo "Available images:\n${env.IMAGE_LIST}"
            }
        }

        stage('Select Image') {
            steps {
                script {
                    def tags = env.IMAGE_LIST.split('\n').toList()
                    def userInput = input(
                        message: 'Select the image to deploy:',
                        parameters: [
                            choice(
                                name: 'IMAGE_TAG',
                                choices: tags,
                                description: 'Available ECR images (newest first)'
                            )
                        ]
                    )
                    env.SELECTED_TAG = userInput.split()[0]
                    echo "User selected: ${env.SELECTED_TAG}"
                }
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${SSH_CREDENTIAL_ID}",
                        keyFileVariable: 'SSH_KEY'
                    )
                ]) {
                    sh "${VENV_DIR}/bin/python deploy.py"
                }
            }
        }
    }
}