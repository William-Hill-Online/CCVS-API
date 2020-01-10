help:
	@echo
	@echo "Please use 'make <target>' where <target> is one of"
	@echo

	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install pipenv
	echo "Installing deps"
	@pipenv install --dev

clean: ## Clear *.pyc files, etc
	@rm -rf build dist *.egg-info
	@find . \( -name '*.pyc' -o  -name '__pycache__' -o -name '**/*.pyc' -o -name '*~' \) -delete

tests: install ## Run tests
	echo "Running tests"
	@pipenv run coverage run src/manage.py test --settings=ccvs.settings.tests --keepdb

migrate: install ## Run django migrate
	echo "Running django migrate"
	@pipenv run python src/manage.py migrate

run: migrate ## Run runserver
	echo "Running server"
	@pipenv run python src/manage.py runserver 0.0.0.0:8000

run-debug: migrate ## Run runserver with debug
	echo "Running server(debuging mode)"
	@pipenv run python src/manage.py runserver 0.0.0.0:8001

makemigrations: install ## Run django makemigrations
	echo "Running django makemigrations"
	@pipenv run python src/manage.py makemigrations

tests-docker: run-docker ## Run tests inside docker
	echo "Running tests inside docker"
	docker exec ccvs_api make tests

run-docker: ## Run docker
	echo "Running docker"
	docker-compose --file development/docker-compose.yml up -d --build

run-docker-vendors: ## Run docker(vendors)
	echo "Running docker(vendors)"
	echo "Running docker vendor anchore"
	docker-compose --file development/vendors/anchore-engine/docker-compose.yml up -d --build
	echo "Running docker vendor clair"
	docker-compose --file development/vendors/clair/docker-compose.yml up -d --build

run-celery: install ## Run celery
	echo "Running celery"
	cd src && DJANGO_SETTINGS_MODULE=ccvs.settings.development pipenv run celery -A ccvs worker -l info
