import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.hdinsight import HDInsightManagementClient
from azure.mgmt.hdinsight.models import (ClusterCreateParameters, 
                                         SparkJobDefinition,
                                         SparkJobProperties)


# Replace with your Azure subscription ID, resource group, and HDInsight cluster name
subscription_id = "your_subscription_id"
resource_group_name = "your_resource_group"
cluster_name = "your_cluster_name"
spark_job_name = "your_spark_job_name"
spark_script_path = "path_to_your_spark_script.py"  # Path to the Spark script you want to submit

# Set up the Azure authentication and HDInsight client
credential = DefaultAzureCredential()
client = HDInsightManagementClient(credential, subscription_id)

# Define the Spark job parameters
job_properties = SparkJobProperties(
    file=spark_script_path,
    arguments=["arg1", "arg2"],  # Replace with any arguments your Spark job might need
    class_name="your.main.class",  # This is typically needed for Java/Scala jobs; omit for Python jobs
    driver_memory="2g",  # Memory allocated for the driver
    executor_memory="2g",  # Memory allocated for the executors
    executor_cores=2,  # Number of cores to allocate for executors
)

# Create the Spark job definition
spark_job_definition = SparkJobDefinition(properties=job_properties)

# Submit the Spark job to the cluster
job = client.jobs.create(
    resource_group_name,
    cluster_name,
    spark_job_name,
    spark_job_definition
)

print(f"Spark job {spark_job_name} submitted successfully.")
print(f"Job details: {job}")
