# Databricks notebook source
storageAccountName = config_data['storageAccountName']
containerName = config_data['containerName']
applicationId = config_data['applicationId']
directoryID = config_data['directoryID']
secretValue = config_data['secretValue']
endpoint = 'https://login.microsoftonline.com/' + directoryID + '/oauth2/token'
source = 'abfss://' + containerName + '@' + storageAccountName + '.dfs.core.windows.net/'
mountPoint = "/mnt/sof-mountpoint"

configs = {"fs.azure.account.auth.type": "OAuth",
           "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
           "fs.azure.account.oauth2.client.id": applicationId,
           "fs.azure.account.oauth2.client.secret": secretValue,
           "fs.azure.account.oauth2.client.endpoint": endpoint}


dbutils.fs.mount(source = source,mount_point = mountPoint, extra_configs = configs)

# COMMAND ----------

#display(dbutils.fs.ls('/mnt/sof-mountpoint')) # /mnt/sof-mountpoint -> it's will show us the two files that we have it in our Storage account and inside the contianer that we have, we have two folders one for daily and weekly loaded files and archive old file .


display(dbutils.fs.ls('/mnt/sof-mountpoint/Landing'))# if we want to see what inside Landing folder we can add it into the 

# COMMAND ----------

# MAGIC %md
# MAGIC # Creating a spark session
# MAGIC is we use the databricks inside azure here we don't need to create a session or sparkcontext, but if you work localy you need to createa a session before you start.
# MAGIC
# MAGIC from pyspark.sql import SparkSession
# MAGIC
# MAGIC spark = (SparkSession
# MAGIC          .builder
# MAGIC          .appName("Table Loading")
# MAGIC          .getOrCreate())
# MAGIC
# MAGIC sc = spark.sparkContext

# COMMAND ----------

display(dbutils.fs.ls('/mnt/sof-mountpoint/Landing/sample-data-training/'))

# COMMAND ----------

# now we need to create a dataframe for Post and to doing that we need to use file location which mean that we recall the mount point of storage workshop that data mount in /mnt/sof-mountpoint/Landing
file_location = '/mnt/sof-mountpoint/Landing/sample-data-training/post/*'# * here mean all file inside the path 

posts = spark.read.parquet(file_location) # here we creating the DataFrame be read the file_location as parquet which the files format inside the mount point 
num_columns = len(posts.schema.fields) # info about the num of columns that we have 
print(f'the number of columns that we have :{num_columns}') # 17

display(posts) # 2,066 rows | 9.21 seconds runtime

# COMMAND ----------

# in PostType and user we need to define(Build) the structure of the dataframe

from pyspark.sql.types import *

pt_schema = StructType([
    StructField("id", IntegerType(),True),
    StructField("Type",StringType(),True)
])

# COMMAND ----------

# now we creating the PostType dataframe by defining the File_location and then we create it 
pt_file_location = '/mnt/sof-mountpoint/Landing/sample-data-training/PostTypes.txt'

post_type = spark.read.option('header',True).option('sep',',').schema(pt_schema).csv(pt_file_location)
display(post_type)

# COMMAND ----------

# in PostType and user we need to define(Build) the structure of the dataframe

users_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("Age", IntegerType(), True),
    StructField("CreationDate", DateType(), True),
    StructField("DisplayName", StringType(), True),
    StructField("DownVotes", IntegerType(), True),
    StructField("EmailHash", StringType(), True),
    StructField("Location", StringType(), True),
    StructField("Reputation", IntegerType(), True),
    StructField("UpVotes", IntegerType(), True),
    StructField("Views", IntegerType(), True),
    StructField("WebsiteUrl", StringType(), True),
    StructField("AccountId", IntegerType(), True)
])

# COMMAND ----------

# now we creating the user dataframe by defining the File_location and then we create it 
user_file_location = '/mnt/sof-mountpoint/Landing/sample-data-training/users.csv'
user = spark.read.option('header',True).option('sep',',').schema(users_schema).csv(user_file_location)

display(user)

# COMMAND ----------

# Saving the dataframes for easy retrieval So we will save 3 tables to databricks local file system
posts.write.parquet('/temp/projects/sof/post.parquet')
post_type.write.parquet('/temp/projects/sof/post_type.parquet')
user.write.parquet('/temp/projects/sof/user.parquet')

# COMMAND ----------

# review the local file system
display(dbutils.fs.ls("/temp/projects/sof/"))

# COMMAND ----------

# MAGIC %md
# MAGIC # Join tables and filter data

# COMMAND ----------

# First we need to import the necessary library
from pyspark.sql.functions import split, translate, trim, explode, regexp_replace, col, lower

# COMMAND ----------

# now we want to read the tables
posts= spark.read.parquet('/temp/projects/sof/post.parquet')
post_type = spark.read.parquet('/temp/projects/sof/post_type.parquet')
user = spark.read.parquet('/temp/projects/sof/user.parquet')

# COMMAND ----------

# at this moment, we only use Posts and posttypes to train the model. so let's join them with the posttype id. 
join_p_pt = posts.join(post_type,posts.PostTypeId == post_type.id)
display(join_p_pt)

# COMMAND ----------

# MAGIC %md
# MAGIC # Filter the data
# MAGIC In the `posttypes` table, there is a column called `Type` which indicates if the posts is a question or an answer. We only need the `question` entires. For these `Question` rows, we will run machine learning model on the join the `Body` column of the `Posts` table. To tell what topic this post is about.

# COMMAND ----------

filtering_join_p_pt = join_p_pt.filter(col("Type") == "Question")
display(filtering_join_p_pt)

# COMMAND ----------

# BODY:<p>I have an abstract class with a protected variable</p> <pre><code>abstract class Beverage { protected string description; } </code></pre> <p>I can't access it from a subclass. Intellisense doesn't show it accessible. Why is that so?</p> <pre><code>class Espresso:Beverage { //this.description ?? } </code></pre>
# Tags: <c#><.net><abstract-class><protected>

# COMMAND ----------

# MAGIC %md
# MAGIC # Formatting for Machine Learning:
# MAGIC - Machine learning algorithms typically work best with numerical data. Text data like the content in your `Body` and `Tags` columns needs preprocessing to be suitable for training these models.Removing HTML Tags, and we can use `regexp_replace` function removes HTML tags, and for Tags columns we can use `split`

# COMMAND ----------

# we need now to Formatting the 'Body' and `Tag` columns for machine learning training
df = (filtering_join_p_pt.withColumn('Body',\
       regexp_replace(filtering_join_p_pt.Body, r'<.*?>', ''))# Transforming HTML code to strings
      
      .withColumn("Tags", split(trim(translate(col("Tags"), "<>", " ")), " ")) # Making a list of the tags
)

display(df)

# COMMAND ----------

# Filter the dataframe to only include questions
df = df.filter(col("Type") == "Question")
display(df)

# COMMAND ----------

df = df.select(col("Body").alias("text"), col("Tags"))

# COMMAND ----------

# Producing the tags as individual tags instead of an array
# This is duplicating the posts for each possible tag
df = df.select("text", explode("Tags").alias("tags"))

# COMMAND ----------

display(df)

# COMMAND ----------

# saving the file as a checkpoint (in case the cluster gets terminated)

df.write.parquet("/tmp/project/sof.df.parquet")

# COMMAND ----------

# MAGIC %md
# MAGIC ### df.cache():
# MAGIC > This method instructs Spark to cache the DataFrame df in memory across the cluster.Purpose of using `cache()` Caching improves the performance of subsequent operations on the same DataFrame because Spark doesn't need to re-read the data from the original source (e.g., disk storage) every time.
# MAGIC - Benefits:
# MAGIC   - Faster execution for repeated operations on the same DataFrame.
# MAGIC   - Useful when working with large datasets that are accessed multiple times within your notebook.
# MAGIC > so we cache the DataFrame df after applying transformations like explode. This ensures faster execution if you perform further operations on the same DataFrame within your notebook.
# MAGIC ### df.count():
# MAGIC - we use the `count` After caching fro serveal purpose:
# MAGIC   - Verifies if the data has been loaded successfully and provides the total number of rows after the explode operation.
# MAGIC   - Since the DataFrame is cached, counting should be relatively fast.

# COMMAND ----------

# Saving the dataframe to memory for repetitive use
df.cache()
df.count()

# COMMAND ----------

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC # Text Cleaning Preprocessing
# MAGIC - pyspark.sql.functions.regexp_replace is used to process the text
# MAGIC * by using the regexp_replace we will do:
# MAGIC    - Remove URLs such as http://stackoverflow.com
# MAGIC    - Remove special characters
# MAGIC    - Substituting multiple spaces with single space
# MAGIC    - Lowercase all text
# MAGIC    - Trim the leading/trailing whitespaces

# COMMAND ----------

from pyspark.sql.functions import regexp_replace


# COMMAND ----------

data_cleaning = df.withColumn('text',regexp_replace("text",r"http\S+"," ")) \
            .withColumn('text',regexp_replace("text",r"[^a-zA-z]"," ")) \
            .withColumn('text',regexp_replace("text",r"\s+"," ")) \
            .withColumn('text',lower('text')) \
            .withColumn('text',trim('text'))
display(data_cleaning)

# COMMAND ----------

# MAGIC %md
# MAGIC # Machine Learning Model Training

# COMMAND ----------

# Importing all the libraries
from pyspark.ml.feature import Tokenizer 
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import StringIndexer
from pyspark.ml.feature import HashingTF, IDF
from pyspark.sql.functions import split, translate, trim, explode, regexp_replace, col, lower
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# COMMAND ----------

# Train Test Split
train, test = data_cleaning.randomSplit([0.9, 0.1], seed=20200819)

# COMMAND ----------

# Feature Transformer Tokenizer
tokenizer_field = Tokenizer(inputCol="text", outputCol="tokens")
tokenized = tokenizer_field.transform(data_cleaning)
display(tokenized)

# COMMAND ----------

# Stopword Removal
sw_remover = StopWordsRemover(inputCol='tokens',outputCol='filtered_word')
sw = sw_remover.transform(tokenized)
display(sw)


# COMMAND ----------

# CountVectorizer (TF - Term Frequency)
count_vectorizer = CountVectorizer(vocabSize=2**16,inputCol='filtered_word',outputCol='vectorization_count')
cv_model=count_vectorizer.fit(sw)
cv_text = cv_model.transform(sw)
display(cv_text)

# COMMAND ----------

# TF-IDF Vectorization
idf = IDF(inputCol='vectorization_count', outputCol="features", minDocFreq=5) #minDocFreq: remove sparse terms
idf_model = idf.fit(cv_text)
text_idf = idf_model.transform(cv_text)

display(text_idf)

# COMMAND ----------

#Label Encoding

label_encoder = StringIndexer(inputCol = "tags", outputCol = "label")
le_model = label_encoder.fit(text_idf)
final = le_model.transform(text_idf)

display(final)

# COMMAND ----------

# Model Training
logistic_reg = LogisticRegression(maxIter=100)

logistic_reg_model = logistic_reg.fit(final)

predictions = logistic_reg_model.transform(final)
display(predictions)

# COMMAND ----------



# COMMAND ----------

# Model Evalution
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

evaluator = MulticlassClassificationEvaluator(predictionCol="prediction")
roc_auc = evaluator.evaluate(predictions)
accuracy = predictions.filter(predictions.label == predictions.prediction).count() / float(predictions.count())

print("Accuracy Score: {0:.4f}".format(accuracy))
print("ROC-AUC: {0:.4f}".format(roc_auc))

# COMMAND ----------

# Creating the pipeline
pipeline = Pipeline(stages=[tokenizer_field, sw_remover, count_vectorizer, idf, label_encoder, logistic_reg])


# COMMAND ----------



# COMMAND ----------

# Fitting and transforming (predicting) using the pipeline
pipeline_model = pipeline.fit(train)
predictions = pipeline_model.transform(test)

# COMMAND ----------

# Save the Model file to Azure storage
# Saving model object to the /mnt/deBDProject directory. Yours name may be different.
pipeline_model.save('/mnt/sof-mountpoint/model')

# Save the the String Indexer to decode the encoding. We need it in the future Sentiment Analysis.
le_model.save('/mnt/sof-mountpoint/stringindexer')

# COMMAND ----------

# Review the directory
display(dbutils.fs.ls("/mnt/sof-mountpoint/model"))

# COMMAND ----------

# MAGIC %md
# MAGIC
