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
        GEMINI_API_KEY = "AIzaSyC0PI-x9vrZ2ngpA8uDKgJj-3zqihGdjo4"
        TAVILY_API_KEY = "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"
        GEMINI_MODEL_NAME = "gemini-3-pro-preview"
        CHROMA_PERSIST_DIR="./chroma_db"
        API_BASE = "http://localhost:5000"
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
                      --set-env-vars "GEMINI_API_KEY = $GEMINI_API_KEY,TAVILY_API_KEY=$TAVILY_API_KEY,GEMINI_MODEL_NAME=$GEMINI_MODEL_NAME,CHROMA_PERSIST_DIR=$CHROMA_PERSIST_DIR,API_BASE=$API_BASE" \
                      --allow-unauthenticated \
                      --port 8080 \
                      --memory 4Gi
                '''
            }
        }
    }
}
