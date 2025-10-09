steps:
  - name: gcr.io/cloud-builders/docker
    entrypoint: docker
    args: ['pull', 'gcr.io/$PROJECT_ID/umpiregpt-streamlit:v1']
    id: pull-app
    waitFor: ['-']
  - name: gcr.io/cloud-builders/docker
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/umpiregpt-streamlit:v1', '-f', 'Dockerfile-streamlit', '.', '--cache-from', 'gcr.io/$PROJECT_ID/umpiregpt-streamlit:v1']
    id: build-app
    waitFor: ['pull-app']
  - name: gcr.io/cloud-builders/docker
    args: ['push', 'gcr.io/$PROJECT_ID/umpiregpt-streamlit:v1']
    id: push-app
    waitFor: ['build-app']
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk:542.0.0
    entrypoint: gcloud
    args:
      - run
      - deploy
      - umpiregpt-streamlit
      - --image=gcr.io/$PROJECT_ID/umpiregpt-streamlit:v1
      - --region=us-central1
      - --platform=managed
      - --allow-unauthenticated
      - --port=8501
      - --min-instances=1
      - --timeout=600s
    id: deploy
    waitFor: ['push-app']
