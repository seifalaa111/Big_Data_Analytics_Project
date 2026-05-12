"""
config.py - Centralized Configuration
All components import settings from here instead of hardcoding values.
"""

# Kafka
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "transactions"

# Paths
DATA_PATH = "creditcard.csv"
MODEL_PATH = "model.pkl"
RESULTS_FILE = "results.csv"
ALERT_LOG = "fraud_alerts.log"

# Model features (must match training order)
MODEL_FEATURES = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]

# Producer
STREAM_DELAY = 0.05  # seconds between messages (~20 txn/sec)

# Dashboard
DASHBOARD_REFRESH = 3  # seconds
