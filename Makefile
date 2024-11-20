PROJECT_NAME = terraformers
REGION = eu-west-2
PYTHON_INTERPRETER = python
WD=$(shell pwd)
PYTHONPATH=${WD}/python/lambda1:${WD}/python/lambda2:${WD}/python/lambda3
SHELL := /bin/bash
PROFILE = default
PIP:=pip

## Create python interpreter environment.
create-environment:
	@echo ">>> About to create environment: $(PROJECT_NAME)..."
	@echo ">>> check python3 version"
	( \
		$(PYTHON_INTERPRETER) --version; \
	)
	@echo ">>> Setting up VirtualEnv."
	( \
	    $(PIP) install -q virtualenv virtualenvwrapper; \
	    virtualenv venv --python=$(PYTHON_INTERPRETER); \
	)

# Define utility variable to help calling Python from the virtual environment
ACTIVATE_ENV := source venv/bin/activate

# Execute python related functionalities from within the project's environment
define execute_in_env
	$(ACTIVATE_ENV) && $1
endef

## Build the environment requirements
requirements: create-environment
	$(call execute_in_env, $(PIP) install pip-tools)
	$(call execute_in_env, pip-compile requirements.in)
	$(call execute_in_env, $(PIP) install -r requirements.txt)

################################################################################################################
# Set Up
## Install bandit
bandit:
	$(call execute_in_env, $(PIP) install bandit)

## Install pip-audit
pip-audit:
	$(call execute_in_env, $(PIP) install pip-audit)

## Install black
black:
	$(call execute_in_env, $(PIP) install black)

## Install pytest-cov
pytest-cov:
	$(call execute_in_env, $(PIP) install pytest-cov)

## Install flake8
flake8:
	$(call execute_in_env, $(PIP) install flake8)

## Set up dev requirements (bandit, pip-audit, black)
dev-setup: bandit pip-audit black flake8 pytest-cov

# Build / Run

## Run the security test (bandit + pip-audit)
security-test:
	$(call execute_in_env, pip-audit -r requirements.txt \
									 -r	requirements-lambda1.txt \
									 -r	requirements-lambda2.txt \
									 -r	requirements-lambda3.txt )

	$(call execute_in_env, bandit -lll python/lambda1/src/*.py \
								 	python/lambda1/test/*.py \
								 	python/lambda2/src/*.py \
								 	python/lambda2/test/*.py \
								 	python/lambda3/src/*.py \
								 	python/lambda3/test/*.py)

## Run the black code check
run-black:
	$(call execute_in_env, black python/lambda1/src/*.py \
								 python/lambda1/test/*.py \
								 python/lambda2/src/*.py \
								 python/lambda2/test/*.py \
								 python/lambda3/src/*.py \
								 python/lambda3/test/*.py)

## Run the unit tests
unit-test:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest python -vv)

## Run the coverage check
check-coverage:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest --cov=src \
									 python/lambda1/test \
									 python/lambda2/test \
									 python/lambda3/test)

## Run all checks
run-checks: security-test run-black unit-test check-coverage
