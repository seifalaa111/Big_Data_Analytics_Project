"""
spark_analysis.py - Batch Analytics with Apache Spark (Bonus)
Performs large-scale exploratory analysis on the credit card dataset
using PySpark to demonstrate distributed data processing capability.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.stat import Correlation

DATA_PATH = "creditcard.csv"


def create_spark():
    """Initialize a local Spark session."""
    spark = SparkSession.builder \
        .appName("FraudDetection-BatchAnalysis") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def load_data(spark):
    """Load the CSV into a Spark DataFrame."""
    df = spark.read.csv(DATA_PATH, header=True, inferSchema=True)
    print(f"Loaded {df.count()} rows, {len(df.columns)} columns\n")
    return df


def basic_stats(df):
    """Print basic dataset statistics."""
    print("=" * 50)
    print("1. DATASET OVERVIEW")
    print("=" * 50)
    df.describe().show()

    fraud_count = df.filter(F.col("Class") == 1).count()
    normal_count = df.filter(F.col("Class") == 0).count()
    total = fraud_count + normal_count

    print(f"Normal transactions : {normal_count} ({normal_count/total*100:.3f}%)")
    print(f"Fraud transactions  : {fraud_count} ({fraud_count/total*100:.3f}%)")
    print(f"Imbalance ratio     : 1:{normal_count // fraud_count}\n")


def fraud_amount_analysis(df):
    """Compare transaction amounts between fraud and normal."""
    print("=" * 50)
    print("2. TRANSACTION AMOUNT ANALYSIS")
    print("=" * 50)

    df.groupBy("Class").agg(
        F.mean("Amount").alias("avg_amount"),
        F.max("Amount").alias("max_amount"),
        F.min("Amount").alias("min_amount"),
        F.stddev("Amount").alias("std_amount"),
        F.expr("percentile_approx(Amount, 0.5)").alias("median_amount"),
    ).show()


def time_analysis(df):
    """Analyze fraud distribution over time."""
    print("=" * 50)
    print("3. TEMPORAL FRAUD PATTERNS")
    print("=" * 50)

    # Convert 'Time' (seconds from first txn) into hours
    df_time = df.withColumn("Hour", (F.col("Time") / 3600).cast("int") % 24)

    fraud_by_hour = df_time.filter(F.col("Class") == 1) \
        .groupBy("Hour") \
        .count() \
        .orderBy("Hour")

    print("Fraud count by hour of day:")
    fraud_by_hour.show(24)


def top_features(df):
    """Find the PCA features most correlated with fraud."""
    print("=" * 50)
    print("4. TOP FEATURES CORRELATED WITH FRAUD")
    print("=" * 50)

    feature_cols = [f"V{i}" for i in range(1, 29)] + ["Amount"]
    correlations = []

    for col_name in feature_cols:
        corr = df.stat.corr(col_name, "Class")
        correlations.append((col_name, abs(corr), corr))

    # Sort by absolute correlation
    correlations.sort(key=lambda x: x[1], reverse=True)

    print(f"{'Feature':<10} {'|Corr|':<10} {'Direction':<10}")
    print("-" * 30)
    for name, abs_corr, raw_corr in correlations[:10]:
        direction = "Positive" if raw_corr > 0 else "Negative"
        print(f"{name:<10} {abs_corr:<10.4f} {direction:<10}")
    print()


def high_risk_segments(df):
    """Identify high-risk transaction segments."""
    print("=" * 50)
    print("5. HIGH-RISK TRANSACTION SEGMENTS")
    print("=" * 50)

    # Bucket amounts
    df_buck = df.withColumn("amount_bucket", F.when(F.col("Amount") < 10, "0-10")
                            .when(F.col("Amount") < 100, "10-100")
                            .when(F.col("Amount") < 500, "100-500")
                            .otherwise("500+"))

    df_buck.groupBy("amount_bucket").agg(
        F.count("*").alias("total"),
        F.sum("Class").alias("fraud_count"),
        (F.sum("Class") / F.count("*") * 100).alias("fraud_rate_%"),
    ).orderBy("amount_bucket").show()


def main():
    spark = create_spark()
    df = load_data(spark)

    basic_stats(df)
    fraud_amount_analysis(df)
    time_analysis(df)
    top_features(df)
    high_risk_segments(df)

    print("\nSpark batch analysis complete.")
    spark.stop()


if __name__ == "__main__":
    main()
