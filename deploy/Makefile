PROJECT_ID := whatup-395208
CLUSTER_NAME := whatup
REGION := asia-south1


authenticate:
	gcloud container clusters get-credentials ${CLUSTER_NAME} \
		--region ${REGION} \
		--project ${PROJECT_ID}

create-cluster:
	gcloud container clusters create ${CLUSTER_NAME} \
	    --region=${REGION} \
		--project ${PROJECT_ID} \
	    --workload-pool=${PROJECT_ID}.svc.id.goog

	gcloud container node-pools create ${CLUSTER_NAME}_nodepool \
    	--cluster=${CLUSTER_NAME} \
    	--region=${REGION} \
    	--workload-metadata=GKE_METADATA

deploy:
	kubectl apply -f ./definitions/
