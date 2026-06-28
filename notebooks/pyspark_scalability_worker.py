import sys
import json
import time
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, avg, count


def main():
    n_cores = sys.argv[1]
    events_path = sys.argv[2]

    spark = (
        SparkSession.builder
        .appName(f"TBDPhase2Scalability_{n_cores}")
        .master(f"local[{n_cores}]")
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )

    df = spark.read.parquet(events_path)

    start = time.perf_counter()
    filtered = df.filter(
        (col("likes") > 100)
        & (col("event_date") >= "2026-03-01")
        & (col("event_date") <= "2026-03-31")
    )
    result = filtered.groupBy("post_type", "country").agg(
        spark_sum("likes").alias("sum_likes"),
        avg("engagement_score").alias("avg_engagement"),
        count("*").alias("cnt"),
    ).toPandas()
    elapsed = time.perf_counter() - start

    rows = df.count()
    spark.stop()

    output = {
        "n_cores": n_cores,
        "elapsed_s": elapsed,
        "rows": rows,
        "result_len": len(result),
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
