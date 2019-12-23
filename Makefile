help:
	@echo
	@echo "Please use 'make <target>' where <target> is one of"
	@echo

	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install pipenv
	@pipenv install

clean: ## Clear *.pyc files, etc
	@rm -rf build dist *.egg-info
	@find . \( -name '*.pyc' -o  -name '__pycache__' -o -name '**/*.pyc' -o -name '*~' \) -delete

tests: ## Run tests
	@pipenv run python src/manage.py test --settings=ccvs.settings.tests --keepdb

migrate: ## Run django migrate
	@pipenv run python src/manage.py migrate

run: migrate ## Run runserver
	@pipenv run python src/manage.py runserver 0.0.0.0:8000

run-debug: ## Run runserver with debug
	@pipenv run python src/manage.py runserver 0.0.0.0:8001

makemigrations: ## Run django makemigrations
	@pipenv run python src/manage.py makemigrations

all: clean install tests run ## Run clean, install, tests, run

tests-docker: ## Run tests inside docker
	docker-compose --file docker-compose-tests.yml up --build
	docker-compose --file docker-compose-tests.yml down -v

run-docker: ## Run docker
	docker-compose --file docker-compose.yml up -d --build

run-celery: ## Run celery
	cd src; DJANGO_SETTINGS_MODULE=ccvs.settings.development celery -A ccvs worker -l info
