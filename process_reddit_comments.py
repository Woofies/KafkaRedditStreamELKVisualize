import spacy
import logging
import json
from kafka import KafkaProducer
from kafka import KafkaConsumer
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType

# Function to get named entities from comments using spaCy
def get_named_entities(comment):
    doc = nlp(comment)
    named_entities = [ent.text for ent in doc.ents]
    return named_entities

# Kafka settings for topic2 (replace 'localhost:9092' with your Kafka brokers address)
kafka_bootstrap_servers = "localhost:9092"
topic2 = "topic2"
topic1 = "topic1"

# Load the spaCy model using large set to cover more words
nlp = spacy.load("en_core_web_lg")

# Initialize SparkSession and configure proper jar to use kafka
spark = SparkSession.builder \
    .appName("NamedEntityCount") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
    .getOrCreate()

# Read data from Kafka topic1
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", topic1) \
    .load()

# Extract the comment body from the Kafka message
kafka_df = kafka_df.selectExpr("CAST(value AS STRING) AS comment")

# Register the UDF (User-Defined Function) for named entity extraction
spark.udf.register("get_named_entities", get_named_entities)

# Initialize the named entity counts dictionary
named_entity_counts = {}

# Process the comment stream from Kafka
comment_stream = kafka_df.writeStream \
    .outputMode("update") \
    .foreachBatch(lambda df, epochId: process_comments(df)) \
    .start()

# Function to process each comment batch from the stream
def process_comments(df):
    global named_entity_counts  # Use the global dictionary

    # Iterate through each comment in the batch
    for row in df.rdd.collect():
        comment = row["comment"]
        named_entities = get_named_entities(comment)

        for entity in named_entities:
            named_entity_counts[entity] = named_entity_counts.get(entity, 0) + 1

    # Send named entity counts to Kafka topic2
    send_to_kafka(named_entity_counts)

# Function to send named entity count to Kafka topic2
def send_to_kafka(entity_counts):
    # Initialize Kafka producer
    producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)

    # Send named entity counts to the output Kafka topic convert to json format for the sake of using ELK for visualization
    for entity, count in entity_counts.items():
       data = {"entity": entity, "count": count}
       message = json.dumps(data).encode('utf-8')
       producer.send(topic2, value=message)

    # Flush and close the Kafka producer
    producer.flush()
    producer.close()

# Wait for the query to terminate
comment_stream.awaitTermination()