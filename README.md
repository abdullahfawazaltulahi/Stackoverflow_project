# StackOverflow Data Analysis and Topic Classification
![project description](https://github.com/abdullahfawazaltulahi/Stackoverflow_project/assets/63244923/d9fd05c7-7670-45c9-bef0-1d65ad20adb3)

# Introduction:

In the dynamic world of technology, staying informed about the latest trends and discussions is essential for IT professionals and enthusiasts. This project aims to harness the power of Azure cloud services to build a robust big-data engineering solution that not only analyzes data from StackOverflow but also provides continuous updates on the platform's user behavior, post trends, and topic popularity.

# Project Objectives:

The primary objective of this project is to develop an Azure-based big data engineering solution that continuously ingests, transforms, and visualizes data from StackOverflow, ensuring that the insights and visualizations are always up-to-date. The specific objectives of the project are as follows:

  - Ingest data from two sources: AWS RDS Postgres database and Azure Storage Blob container, with continuous updates for the "Posts" data.
  -  Perform data transformation using Databricks notebook to clean, transform, and apply machine learning techniques continuously.
  - Generate interactive visualizations using Azure Synapse to display the top 10 discussed topics on StackOverflow, updated continuously.

# Project Scope:
The project will focus on the following key tasks, ensuring continuous updates for each component:

  # Data Ingestion:
    - Establish a connection to AWS RDS Postgres database and ingest "Users" and "PostTypes" tables into Azure Data Lake.
    - Connect to Azure Storage Blob container and ingest daily "Posts" data files in Parquet format, ensuring that the data is updated continuously.
  
  # Data Transformation:
  Create a Databricks notebook to perform the following operations continuously:
    - Data cleaning and transformation to prepare the data for machine learning.
    - Develop a machine learning model to classify the topics of StackOverflow posts based on their text content, with continuous updates to the model.
  
  # Data Visualization:
  Utilize Azure Synapse to connect to the Data Lake and generate a chart that displays the top 10 topics of the day, updated continuously.
  
  # Project Deliverables:
  Upon completion of the project, the following deliverables will be produced:
  
    - A comprehensive Azure-based big data engineering solution for StackOverflow data analysis, with continuous updates.
    - A Databricks notebook containing the data transformation and machine learning code, updated continuously.
    - An interactive dashboard generated using Azure Synapse that visualizes the top 10 discussed topics on StackOverflow, updated continuously.

## Project Status:
Please note that this project is currently in progress and is undergoing continuous development. The data ingestion, transformation, and visualization processes are designed to run on a continuous basis, ensuring that the insights and visualizations provided are always up-to-date.
