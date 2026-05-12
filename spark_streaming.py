"""
spark_streaming.py - Real-Time Spark Structured Streaming Consumer (Bonus)
Reads from Kafka 'transactions' topic using Spark Structured Streaming,
applies the trained model, and prints fraud alerts in real time.

This demonstrates how the pipeline could scale to millions of transactions
using distributed Spark workers instead of a single Python consumer.

Prerequisites:
  pip install pyspark
  Kafka must be running (docker-compose up -d)
  Producer must be streaming (python producer.py)

Run:
  python spark_streaming.py
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, DoubleType, IntegerType, StringType
)
import joblib
import numpy as np

MODEL_PATH = "model.pkl"
KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"

# Define the schema for incoming JSON messages
SCHEMA = StructType(
    [StructField("Time", DoubleType())] +
    [StructField(f"V{i}", DoubleType()) for i in range(1, 29)] +
    [StructField("Amount", DoubleType())] +
    [StructField("Class", IntegerType())] +
    [StructField("Transaction_ID", IntegerType())]
)

FEATURE_COLS = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


def create_spark():
    """Create Spark session with Kafka connector."""
    spark = SparkSession.builder \
        .appName("FraudDetection-SparkStreaming") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def main():
    # Load the trained model
    print(f"Loading model from {MODEL_PATH}...")
    model = joblib.load(MODEL_PATH)
    print("Model loaded.\n")

    # Broadcast model features for use in UDF
    feature_cols = FEATURE_COLS

    spark = create_spark()

    # Read stream from Kafka
    print(f"Connecting to Kafka topic '{TOPIC}'...")
    raw_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    # Parse the JSON messages
    parsed = raw_stream \
        .selectExpr("CAST(value AS STRING) as json_str") \
        .select(F.from_json(F.col("json_str"), SCHEMA).alias("data")) \
        .select("data.*")

    # We need to collect each micro-batch and run predictions
    # Using foreachBatch to apply the sklearn model
    def process_batch(batch_df, batch_id):
        if batch_df.count() == 0:
            return

        # Convert to pandas for sklearn prediction
        pdf = batch_df.toPandas()

        # Extract features
        X = pdf[feature_cols].values

        # Predict
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)[:, 1]

        pdf["prediction"] = predictions
        pdf["fraud_probability"] = probabilities

        # Show results
        frauds = pdf[pdf["prediction"] == 1]
        normals = pdf[pdf["prediction"] == 0]

        print(f"\n--- Batch {batch_id}: {len(pdf)} transactions "
              f"({len(frauds)} fraud, {len(normals)} normal) ---")

        for _, row in frauds.iterrows():
            print(f"  *** FRAUD *** TXN {int(row['Transaction_ID'])} "
                  f"| ${row['Amount']:.2f} | confidence: {row['fraud_probability']:.2%}")

    # Start the streaming query
    print("Starting Spark Structured Streaming...\n")
    query = parsed.writeStream \
        .foreachBatch(process_batch) \
        .outputMode("update") \
        .start()

    query.awaitTermination()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSpark streaming stopped.")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Kafka is running and producer.py is streaming data.")
