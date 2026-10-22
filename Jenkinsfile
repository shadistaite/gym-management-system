pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        JWT_SECRET_KEY = 'jenkins-test-secret-key-change-this'
        PYTHONDONTWRITEBYTECODE = '1'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage('Build and Install Dependencies') {
            steps {
                dir('/Users/shadi/Desktop/gym-management-system') {
                    sh '''
                        /opt/homebrew/bin/python3.12 --version

                        /opt/homebrew/bin/python3.12 -m venv .jenkins-venv

                        .jenkins-venv/bin/python -m pip install --upgrade pip

                        .jenkins-venv/bin/python -m pip install \
                            -r api-service/requirements.txt

                        .jenkins-venv/bin/python -m pip install \
                            -r gym-service/requirements.txt

                        .jenkins-venv/bin/python -m pip install \
                            -r processing-service/requirements.txt

                        .jenkins-venv/bin/python -m pip install -e ./gym-summary-utils

                        .jenkins-venv/bin/python -m pip install \
                            pytest pytest-cov ruff pip-audit
                    '''
                }
            }
        }

        stage('Static Analysis') {
            steps {
                dir('/Users/shadi/Desktop/gym-management-system') {
                    sh '''
                        .jenkins-venv/bin/ruff check \
                            api-service \
                            gym-service \
                            processing-service \
                            gym-summary-utils \
                            tests
                    '''
                }
            }
        }

        stage('Dependency Security Audit') {
            steps {
                dir('/Users/shadi/Desktop/gym-management-system') {
                    sh '''
                        .jenkins-venv/bin/pip-audit \
                            -r api-service/requirements.txt \
                            -r gym-service/requirements.txt \
                            -r processing-service/requirements.txt \
                            --strict
                    '''
                }
            }
        }

        stage('Automated Security and Functional Tests') {
            steps {
                dir('/Users/shadi/Desktop/gym-management-system') {
                    sh '''
                        mkdir -p reports

                        .jenkins-venv/bin/python -m pytest tests/ \
                            --junitxml=reports/junit.xml \
                            --cov=api-service \
                            --cov=gym-service \
                            --cov=processing-service \
                            --cov-report=xml:reports/coverage.xml \
                            --cov-report=term \
                            -v
                    '''
                }
            }
        }
    }

    post {
        always {
            dir('/Users/shadi/Desktop/gym-management-system') {
                junit testResults: 'reports/junit.xml',
                      allowEmptyResults: true

                archiveArtifacts artifacts: 'reports/**',
                                 allowEmptyArchive: true
            }
        }

        success {
            echo 'Build, security checks, and tests completed successfully.'
        }

        failure {
            echo 'The pipeline failed. Review the stage logs and test reports.'
        }
    }
}