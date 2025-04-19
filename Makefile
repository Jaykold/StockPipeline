SHELL := /bin/bash

# Set Airflow UID and GID once
AIRFLOW_UID := $(shell id -u)
AIRFLOW_GID := $(shell id -g)

.PHONY: tf-apply tf-output docker-build docker-start docker-stop git tf-destroy

tf-apply:
	cd terraform && \
	terraform init && \
	terraform validate && \
	echo "Terraform initialized and validated successfully" && \
	terraform plan -out=tfplan && \
	echo "Terraform plan executed successfully" && \
	terraform apply tfplan && \
	rm -f tfplan && \
	echo "Terraform apply executed successfully"

tf-output:
	@echo "This is not advised in production, but for testing purposes, we will output the Terraform state."
	cd terraform && \
	terraform output -json
			
docker-build:
	@echo "Building Docker image..." && \
	docker build -t custom_airflow:latest . && \
	echo "Docker image built successfully"

airflow-init:
	@echo "Initializing Airflow..."
	docker-compose up airflow-init
	@echo "Airflow initialized successfully"

docker-start:
	@grep -q "^AIRFLOW_UID=" .env || echo "AIRFLOW_UID=$(AIRFLOW_UID)" >> .env
	@grep -q "^AIRFLOW_GID=" .env || echo "AIRFLOW_GID=$(AIRFLOW_GID)" >> .env
	@echo "Running Docker containers now..."
	#docker-compose up -d
	
docker-stop:
	@echo "Stopping Docker container..."
	docker-compose down

tf-destroy:
	@echo "Are you sure you want to destroy the Terraform infrastructure? (yes/no)"
	@read answer && \
	if [ "$$answer" != "yes" ]; then \
		echo "Aborting Terraform destroy"; \
		exit 1; \
	fi
	@echo "Destroying Terraform infrastructure..."
	cd terraform && \
	terraform destroy