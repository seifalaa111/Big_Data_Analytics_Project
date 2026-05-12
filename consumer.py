"""
consumer.py - Kafka Fraud Detection Consumer
Listens to the 'transactions' topic, runs each message through
the trained XGBoost model, classifies it, and triggers alerts
for fraudulent transactions. Results are logged to results.csv.
"""

import json
import csv
import os
import datetime
import traceback
import joblib
import numpy as np
from kafka import KafkaConsumer

KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"
MODEL_PATH = "model.pkl"
RESULTS_FILE = "results.csv"
ALERT_LOG = "fraud_alerts.log"

# The 30 features the model expects (same order as training)
MODEL_FEATURES = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


def load_model():
    """Load the serialized XGBoost model."""
    print(f"Loading model from {MODEL_PATH}...")
    model = joblib.load(MODEL_PATH)
    print("Model loaded.\n")
    return model


def init_results_file():
    """Create the results CSV with headers if it doesn't exist."""
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "transaction_id", "amount",
                "prediction", "fraud_probability", "true_label"
            ])


def log_alert(txn_id, amount, prob):
    """Append a fraud alert to the log file."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] FRAUD ALERT | TXN: {txn_id} | Amount: ${amount:.2f} | Confidence: {prob:.2%}\n"
    with open(ALERT_LOG, "a") as f:
        f.write(line)


def save_result(txn_id, amount, prediction, probability, true_label):
    """Append one classification result to the CSV."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([ts, txn_id, amount, prediction, f"{probability:.6f}", true_label])


def process_message(msg, model):
    """Classify a single transaction and handle alerts."""
    txn_id = msg.get("Transaction_ID", "N/A")
    amount = msg.get("Amount", 0)
    true_label = int(msg.get("Class", -1))

    # Build the feature vector in the correct order
    features = np.array([[msg.get(f, 0) for f in MODEL_FEATURES]])

    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])

    # Save every result to CSV (dashboard reads this)
    save_result(txn_id, amount, prediction, probability, true_label)

    # Trigger alert if fraud detected
    if prediction == 1:
        log_alert(txn_id, amount, probability)
        print(f"  *** FRAUD ALERT *** TXN {txn_id} | ${amount:.2f} | confidence: {probability:.2%}")
    else:
        print(f"  OK  TXN {txn_id} | ${amount:.2f}")


def main():
    model = load_model()
    init_results_file()

    print(f"Listening on topic '{TOPIC}'...")
    print("Waiting for messages...\n")

    consumer = None
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=False,
            group_id=None,
        )

        count = 0
        while True:
            records = consumer.poll(timeout_ms=1000)
            for batch in records.values():
                for message in batch:
                    process_message(message.value, model)
                    count += 1
                    if count % 500 == 0:
                        print(f"\n--- Processed {count} transactions so far ---\n")
    finally:
        if consumer is not None:
            consumer.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nConsumer stopped.")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
