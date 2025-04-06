FROM apache/airflow:2.10.5

USER root
# Install java sdk for spark jobs
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk wget && \
    apt-get clean;

# SET JAVA HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
RUN export JAVA_HOME
#RUN mkdir -p /opt/bitnami/spark/jars/

# Download Spark-related JARs dynamically
# RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-azure/3.3.4/hadoop-azure-3.3.4.jar -P /opt/bitnami/spark/jars/ \
# && wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.10.0.jre11/mssql-jdbc-12.10.0.jre11.jar -P /opt/bitnami/spark/jars/

USER airflow
# Copy the requirements file into the container
COPY requirements.txt .
# Install pip packages
RUN pip install -r requirements.txt

