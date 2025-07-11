gcloud builds submit --tag us-central1-docker.pkg.dev/no-licence-proj/no-licence-user-db-manager/no-licence-user-db-manager-img-v111:version-111

gcloud run deploy no-licence-user-db-manager-runner --image us-central1-docker.pkg.dev/no-licence-proj/no-licence-user-db-manager/no-licence-user-db-manager-img-v111:version-111 --platform managed --region us-central1 --service-account signed-url-service-no-licence@no-licence-proj.iam.gserviceaccount.com --allow-unauthenticated


444




:: For Testing Purposes:

gcloud builds submit --tag us-central1-docker.pkg.dev/no-licence-proj/no-licence-user-db-manager/no-licence-user-db-manager-img-v1-test:version-1-test
