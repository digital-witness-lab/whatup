.PHONY: auth auth-test auth-prod lint-ci

auth-test:
	pulumi org set-default digitalwitnesslab
	pulumi stack select digitalwitnesslab/test
	make auth

auth-prod:
	pulumi org set-default mynameisfiber
	pulumi stack select mynameisfiber/prod
	make auth

auth:
	gcloud auth login
	gcloud auth application-default login
	gcloud config set project $$( pulumi config get gcp:project )
	make auth-docker

auth-docker:
	gcloud auth configure-docker $$( pulumi config get gcp:region )-docker.pkg.dev

fix-test-stack:
	pulumi stack export --stack digitalwitnesslab/test > stack.test.yaml
	grep "reserved-private-4677207" stack.test.yaml | wc -l
	sed -i 's/reserved-private-4677207/reserved-private-6100a84/g' stack.test.yaml 
	grep "reserved-private-4677207" stack.test.yaml | wc -l
	pulumi stack import --stack digitalwitnesslab/test --file stack.test.yaml 
	rm stack.test.yaml

lint-ci:
	pip install -r requirements.txt
	flake8 .
