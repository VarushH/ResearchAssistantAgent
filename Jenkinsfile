// pipeline {
//     agent {
//         docker {
//             image 'google/cloud-sdk:latest'
//         }
//     }
    
//     environment {
//         PROJECT_ID = 'glassy-land-482114-j4'
//         REGION     = 'us-central1'
//         REPO_NAME  = 'research-agent-repo'
//         IMAGE_NAME = 'research-assistant-agent'
//         SERVICE_NAME = 'research-assistant-service'
//         // Construct the full image path
//         IMAGE_TAG  = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
//     }

//     stages {
//         // stage('Authenticate GCP') {
//         //     steps {
//         //         withCredentials([file(credentialsId: 'gcp-deploy-key', variable: 'GCP_KEY')]) {
//         //             // Log in to GCP using the service account key
//         //             bat "gcloud auth activate-service-account --key-file=%GCP_KEY%"
//         //             bat "gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet"
//         //         }
//         //     }
//         // }

//         stage('Authenticate GCP') {
//             steps {
//                 withCredentials([file(credentialsId: 'gcp-deploy-key', variable: 'GCP_KEY')]) {
//                     // Using "call" or full path ensures Windows finds the .cmd file
//                     bat "call gcloud auth activate-service-account --key-file=\"%GCP_KEY%\""
//                     bat "call gcloud auth configure-docker us-central1-docker.pkg.dev --quiet"
//                 }
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 bat "docker build -t ${IMAGE_TAG} ."
//             }
//         }

//         stage('Push to Artifact Registry') {
//             steps {
//                 bat "docker push ${IMAGE_TAG}"
//             }
//         }

//         stage('Deploy to Cloud Run') {
//             steps {
//                 bat """
//                 gcloud run deploy ${SERVICE_NAME} \
//                     --image ${IMAGE_TAG} \
//                     --platform managed \
//                     --region ${REGION} \
//                     --allow-unauthenticated \
//                     --port 8080 \
//                     --memory 2Gi
//                 """
//             }
//         }
//     }
// }





pipeline {
    agent {
        docker {
            image 'google/cloud-sdk:latest'
            args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        PROJECT_ID   = 'glassy-land-482114-j4'
        REGION       = 'us-central1'
        REPO_NAME    = 'research-agent-repo'
        IMAGE_NAME   = 'research-assistant-agent'
        SERVICE_NAME = 'research-assistant-service'
        IMAGE_TAG    = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${BUILD_NUMBER}"
    }

    stages {

        stage('Authenticate GCP') {
            steps {
                withCredentials([file(credentialsId: 'gcp-deploy-key', variable: 'GCP_KEY')]) {
                    sh '''
                        gcloud auth activate-service-account --key-file="$GCP_KEY"
                        gcloud config set project $PROJECT_ID
                        gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t $IMAGE_TAG .
                '''
            }
        }

        stage('Push to Artifact Registry') {
            steps {
                sh '''
                    docker push $IMAGE_TAG
                '''
            }
        }

        stage('Deploy to Cloud Run') {
            steps {
                sh '''
                    gcloud run deploy $SERVICE_NAME \
                      --image $IMAGE_TAG \
                      --platform managed \
                      --region $REGION \
                      --allow-unauthenticated \
                      --port 8080 \
                      --memory 2Gi
                '''
            }
        }
    }
}
