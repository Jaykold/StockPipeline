FROM apache/airflow:2.10.5

USER root
# Install java sdk for spark jobs
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk wget && \
    apt-get clean;

# SET JAVA HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow

# Copy the requirements file into the container
COPY requirements.txt .
# Install pip packages
RUN pip install -r requirements.txt