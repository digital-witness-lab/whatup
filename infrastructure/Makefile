.PHONY: auth auth-test auth-prod lint-ci

auth-test:
	pulumi stack select test
	make auth

auth-prod:
	pulumi stack select prod
	make auth

auth:
	gcloud auth login
	gcloud auth application-default login
	gcloud config set project $$( pulumi config get gcp:project )
	make auth-docker

auth-docker:
	gcloud auth configure-docker $$( pulumi config get gcp:region )-docker.pkg.dev


lint-ci:
	pip install -r requirements.txt
	flake8 .
