pipeline {
    agent any

    environment {
        AWS_REGION          = 'eu-west-1'
        ECR_REPOSITORY_NAME = 'repo1'
        SSH_CREDENTIAL_ID   = 'ssh-target'
        AWS_ACCESS_KEY_ID     = credentials('aws_access_key_id')
        AWS_SECRET_ACCESS_KEY = credentials('aws_secret_access_key')
        VENV_DIR            = "${WORKSPACE}/.venv"   // venv lives inside the workspace
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    ${VENV_DIR}/bin/pip install --upgrade pip
                    ${VENV_DIR}/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Fetch Images') {
            steps {
                // Python fetches tags and saves them to a file
                sh 'pip install'
                sh 'python3 fetch-ecr-images.py > image_tags.txt'
                script {
                    env.IMAGE_LIST = readFile('image_tags.txt').trim()
                }
                echo "Available images:\n${env.IMAGE_LIST}"
            }
        }

        stage('Select Image') {
            steps {
                script {
                    // Parse the tags into a list for the dropdown
                    def tags = env.IMAGE_LIST.split('\n').toList()

                    // Jenkins pauses here and shows the user a dropdown
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
                    env.SELECTED_TAG = userInput
                    echo "User selected: ${env.SELECTED_TAG}"
                }
            }
        }
    }
}