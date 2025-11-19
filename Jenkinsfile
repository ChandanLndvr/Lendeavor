pipeline {
    agent any

    stages {

        stage('Clone Repository') {
            steps {
                // Clone main branch from GitHub
                git branch: 'main', url: 'https://github.com/ChandanLndvr/Lendeavor.git'
            }
        }

        stage('Setup Python Environment') {
            steps {
                // Create virtual environment
                bat "python -m venv venv"

                // Activate virtual environment and upgrade pip
                bat "call venv\\Scripts\\activate && python -m pip install --upgrade pip"

                // Install dependencies from requirements.txt
                bat "call venv\\Scripts\\activate && pip install -r requirements.txt"
            }
        }

        stage('Run Migrations') {
            steps {
                // Activate virtual environment and apply migrations
                bat "call venv\\Scripts\\activate && cd lndvr_site && python manage.py migrate"
            }
        }

        stage('Run Tests') {
            steps {
                // Activate virtual environment and run tests
                bat "call venv\\Scripts\\activate && cd lndvr_site && python manage.py test"
            }
        }

        stage('Show Versions') {
            steps {
                // Optional: check Python and Django versions for debugging
                bat "call venv\\Scripts\\activate && python --version"
                bat "call venv\\Scripts\\activate && python -m django --version"
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed. Check the logs."
        }
    }
}
