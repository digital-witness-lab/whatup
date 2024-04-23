.PHONY: auth auth-test auth-prod lint-ci

auth-carter-prod:
	pulumi org set-default mynameisfiber
	pulumi stack select mynameisfiber/carter-prod
	make auth

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
	gcloud auth application-default set-quota-project $$( pulumi config get gcp:project )
	make auth-docker

auth-docker:
	gcloud auth configure-docker $$( pulumi config get gcp:region )-docker.pkg.dev

fix-test-stack:
	pulumi refresh --skip-preview --stack digitalwitnesslab/test
	pulumi stack export --stack digitalwitnesslab/test > stack.test.json
	grep "reserved-private-4677207" stack.test.json | wc -l
	sed -i 's/reserved-private-4677207/reserved-private-6100a84/g' stack.test.json 
	grep "reserved-private-4677207" stack.test.json | wc -l
	pulumi stack import --stack digitalwitnesslab/test --file stack.test.json 
	rm stack.test.json

lint-ci:
	pip install -r requirements.txt
	flake8 .

cloudlogs:
	gcloud alpha logging tail --buffer-window=10 --format=json 'resource.type="gce_instance"' | jq --stream -r 'select(length == 2 and .[0][-1] == "message") | .[1]' | egrep .
