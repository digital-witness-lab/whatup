# Deploy Instructions

## Local + Docker Compose


## VM + Docker Compose

```bash
gcloud compute instances create whatup-vm \
    --project=whatup-395208 \
    --zone=asia-southeast2-a \
    --machine-type=e2-small \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=840014935177-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/bigquery,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/trace.append,https://www.googleapis.com/auth/devstorage.read_write \
    --create-disk=boot=yes,device-name=whatup-vm-boot,image=projects/ubuntu-os-cloud/global/images/ubuntu-minimal-2304-lunar-amd64-v20230810,mode=rw,size=64,type=projects/whatup-395208/zones/asia-southeast2-a/diskTypes/pd-balanced \
    --shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any
```

## GKE + Kubernetes
