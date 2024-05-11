# StackOverflow Data Analysis and Topic Classification
![Uploading project description.png…]()

## Objective:
The objective of this Big Data Engineering project is to ingest data from multiple sources, including a Postgres database and an Azure Storage Blob container, into a Data Lake in Azure. The project involves data transformation, running a machine learning model to classify post topics, and generating a report using Azure Synapse.
he main goals of this project are as follows:

### Data Ingestion:
Connect to an AWS RDS Postgres database and ingest the Users and PostTypes tables into the Data Lake.
Connect to the WeCloudData Azure blob container and ingest the daily Posts data files in Parquet format into the Data Lake.
### Data Transformation:
Use Azure Data Factory to create a pipeline for data transformation.
Create a Databricks notebook to process the data and feed it into a machine learning model.
Output the running result from the machine learning model, which classifies the topic of each post.
Use Spark to output a file listing the topics for the current day, ordered by their occurrence.
### Data Visualization:
Use Azure Synapse to connect to the Data Lake and generate a chart displaying the top 10 topics of the day.
Create a BI dashboard using the output data from the machine learning model.
