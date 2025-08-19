pipeline {
    agent { 
        node {
            label 'docker-test'
            }
      }
    triggers {
        pollSCM '*/5 * * * *'
    }
    stages {
        stage('Build') {
            steps {
                echo "Building.."
                sh '''
                apt-get update && apt-get install -y \
                    build-essential \
                    libmysqlclient-dev \
                    libssl-dev \
                    rustc \
                    libjpeg-dev \
                    zlib1g-dev \
                    libpng-dev

                cd lndvr_site
                python3 -m pip install --upgrade pip
                python3 -m pip install -r requirements.txt
                '''
            }
        }
        stage('Test') {
            steps {
                echo "Testing.."
                sh '''
                echo "doing test stuff.."
                '''
            }
        }
        stage('Deliver') {
            steps {
                echo 'Deliver....'
                sh '''
                echo "doing delivery stuff.."
                '''
            }
        }
    }
}