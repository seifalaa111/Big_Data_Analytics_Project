"""
producer.py - Kafka Transaction Producer
Reads creditcard.csv and streams each row as a JSON message
into the 'transactions' Kafka topic, simulating a live feed.
"""
import pandas as pd
import json
import time
import sys
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"
DATA_PATH = "creditcard.csv"

def create_producer():
    """Connect to Kafka broker with retries."""
    print(f"Connecting to Kafka at {KAFKA_BROKER}...")
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        api_version=(2, 5, 0),
    )
    print("Connected.\n")
    return producer

def stream_transactions(producer, df):
    """Stream each row of the dataframe to Kafka."""
    total = len(df)
    print(f"Streaming {total} transactions to topic '{TOPIC}'...")
    print("Press Ctrl+C to stop.\n")

    for i, row in df.iterrows():
        msg = row.to_dict()
        msg["Transaction_ID"] = i  # unique ID for tracking

        producer.send(TOPIC, value=msg)

        # ~20 transactions/sec for a nice live effect
        time.sleep(0.05)

        if (i + 1) % 500 == 0:
            print(f"  Sent {i + 1}/{total}")

    producer.flush()
    print(f"\nDone. {total} transactions streamed.")

def main():
    df = pd.read_csv(DATA_PATH)
    producer = create_producer()
    stream_transactions(producer, df)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
