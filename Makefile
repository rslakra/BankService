ROOT_DIR:=${PWD}

# Python Settings
VENV:=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
ACTIVATE=. $(VENV)/bin/activate
ENV_FILE ?= .env
APP_ENV ?= develop

# Date Settings
TIMESTAMP:=$(date +%s)
DATE_TIMESTAMP:=$(date '+%Y-%m-%d')

# App Static Variables
HOST_PORT=8000
CONTAINER_PORT=8000
PROJECT_OWNER=Rohtash Lakra
CONTAINER_NAME:=bank-service
DOCKER_REPOSITORY:=${PROJECT_OWNER}/${PROJECT__NAME}
DOCKER_FILE_NAME:=Dockerfile
IMAGE_TAG:=latest

# MySQL Settings
NETWORK_NAME=mysql-network
MYSQL_CONTAINER_NAME=mysql-docker
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=tod

# Database Settings
DATABASE_USERNAME=root
DATABASE_PASSWORD=
DATABASE_NAME=tod

ifeq ($(tag),)
	IMAGE_TAG=latest
else
	IMAGE_TAG=$(tag)
endif


# Makefile configs
.PHONY: help

# default target executed whenever we just type `make`
.DEFAULT_GOAL: help
all: help

# Make docs generator
define find.functions
	@# @fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
    @printf "%-25s %s\n" "Target" "Description"
    @printf "%-25s %s\n" "----------------" "----------------"
    @make -pqR : 2>/dev/null \
        | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' \
        | sort \
        | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' \
        | xargs -I _ sh -c 'printf "%-25s " _; make _ -nB | (grep -i "^# Help:" || echo "") | tail -1 | sed "s/^# Help: //g"'
endef

# A hidden target
.hidden:


help:
	@echo
	@echo 'The following commands can be used:'
	@echo
	$(call find.functions)
	@echo


clean:
	@# Help: Remove build and cache files
	@echo "Cleaning up ..."
	rm -rf $(VENV)


setup-venv:
	@# Help: Sets up environment and installs requirements
	@echo "Setting up the environment ..."
	python3 -m pip install virtualenv
	python3 -m $(VENV) $(VENV)
	$(ACTIVATE)


install-modules:
	@# Help: Installs the module requirements
	@echo "Installing the requirements ..."
	$(ACTIVATE)
	$(PIP) install --upgrade pip
	$(PIP) install -r ./requirements.txt


test:
	@# Help: Tests the python application
	@echo "Testing python app ..."
	@$(PYTHON) -m unittest


run-app:
	@# Help: Runs the FastAPI server locally
	@echo "Starting Server with APP_ENV=$(APP_ENV) | ENV_FILE=$(ENV_FILE)..."
	$(ACTIVATE) && APP_ENV=$(APP_ENV) uvicorn main:app --host 0.0.0.0 --port $(CONTAINER_PORT) --reload


run-docker-compose:
	@# Help: Runs the docker container locally
	@echo "🚀 Starting Docker Services with APP_ENV=$(APP_ENV) | ENV_FILE=$(ENV_FILE) ..."
	@chmod +x ./envValidator.sh
	@./envValidator.sh $(ENV_FILE)
	APP_ENV=$(APP_ENV) ENV_FILE=$(ENV_FILE) docker-compose -f ./docker-compose.yml --env-file $(ENV_FILE) up --build


build-container:
	@# Help: Builds the docker container image
	@echo "Building docker container image ..."
	@echo "service: $(service), tag: $(tag)"
	@echo "CONTAINER_NAME: $(CONTAINER_NAME), DOCKER_FILE_NAME: $(DOCKER_FILE_NAME), IMAGE_TAG: $(IMAGE_TAG)"
	docker build -t ${CONTAINER_NAME}:${IMAGE_TAG} -f ${DOCKER_FILE_NAME} .


run-container:
	@# Help: Runs the docker container as background service
	@echo "Running Docker Container ..."
	docker run --name ${CONTAINER_NAME} -p ${HOST_PORT}:${CONTAINER_PORT} -d ${CONTAINER_NAME}:${IMAGE_TAG}


log-container:
	@# Help: Shows the docker container's log
	@echo "Showing docker container logs [${CONTAINER_NAME}] ..."
	docker logs -f ${CONTAINER_NAME}


bash-container:
	@# Help: Executes the 'bash' shell in the container
	@echo "Executing docker container [${CONTAINER_NAME}] ..."
	docker exec -it ${CONTAINER_NAME} bash


stop-container:
	@# Help: Stops the docker container
	@echo "Stopping docker container [${CONTAINER_NAME}] ..."
	docker stop ${CONTAINER_NAME}
	docker container rm ${CONTAINER_NAME}

