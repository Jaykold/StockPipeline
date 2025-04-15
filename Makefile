SHELL := /bin/bash
.PHONY: tf-apply tf-output docker-build docker-start docker-stop git tf-destroy

tf-apply:
	cd terraform && \
	terraform init && \
	terraform validate && \
	echo "Terraform initialized and validated successfully" && \
	terraform plan -out=tfplan && \
	echo "Terraform plan executed successfully" && \
	terraform apply tfplan && \
	echo "Terraform apply executed successfully"

tf-output:
	@echo "This is not advised in production, but for testing purposes, we will output the Terraform state."
	cd terraform && \
	terraform output -json
			
docker-build:
	@echo "Building Docker image..." && \
	docker build -t custom_airflow:latest . && \
	echo "Docker image built successfully"

docker-start:
	@echo -e "AIRFLOW_UID=$$(id -u)\nAIRFLOW_GID=$$(id -g)" >> .env
	@echo "Running Docker containers now..."
	docker-compose up -d
	
docker-stop:
	@echo "Stopping Docker container..."
	docker-compose down

git:
	git status
	@echo "Enter files to add ('-u' for tracked modified files, '.' for all changes):"
	@read files && git add $$files
	@echo "Enter commit message:"
	@read msg && git commit -m "$$msg"
	@echo "Pushing changes to remote..."
	git push
	@echo "Git operations completed successfully"

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
	