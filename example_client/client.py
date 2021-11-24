from redisai import Client
import time
import numpy as np
from random import randrange


def predict(conn, min_ts, max_ts, references_key, model_key, script_key):
    start = time.time()

    # Create a random transaction tensor, with 'Time' set as the max_ts (to simulate a condition
    # where we retrieve the latest transactions as our reference data)
    transaction_tensor = np.random.randn(1, 30).astype(np.float32)
    transaction_tensor[0] = max_ts

    # Find the relevant reference data (transaction that occurred within the time interval)
    ref_data_keys = conn.zrangebyscore(references_key, min_ts, max_ts)

    # Create a DAG (execution plan) for RedisAI. First, use the helper script to convert the reference data
    # within the hashes into a tensor. Then run the 2 models and obtain 2 outputs,
    # and finally use the helper script to take their average to be the result (and persist it in key space)
    output_key_name = 'result{tag}'
    dag = conn.dag(persist=[output_key_name])
    dag.tensorset('transaction', transaction_tensor)
    dag.scriptexecute(script_key, 'hashes_to_tensor', keys=ref_data_keys, outputs=['reference'])
    dag.modelexecute(model_key, inputs=['transaction', 'reference'], outputs=['out_1'])
    dag.modelexecute(model_key, inputs=['transaction', 'reference'], outputs=['out_2'])
    dag.scriptexecute(script_key, 'post_processing', inputs=['out_1', 'out_2'], outputs=[output_key_name])
    dag.execute()

    # get result
    result = conn.tensorget(output_key_name)
    print("result: ", result[0])
    print("Total execution took: " + str((time.time() - start) * 1000) + " ms")


def main():
    # Set up redis connection
    conn = Client(host='localhost', port=6379)
    if not conn.ping():
        raise Exception('Redis unavailable')

    # Add '{tag}' to every key name to ensure that all keys will be mapped to te same shard in cluster environment.
    references_key = "references{tag}"
    min_ts = conn.zrangebyscore(references_key, "-inf", "+inf", withscores=True, start=0, num=1)[0][1]
    max_ts = conn.zrevrangebyscore(references_key, "+inf", "-inf", withscores=True, start=0, num=1)[0][1]

    # Generate random time interval, and use the transactions in this time as the reference data.
    min_sample_time = randrange(min_ts, max_ts)
    max_sample_time = randrange(min_ts, max_ts)
    if min_sample_time > max_sample_time:
        min_sample_time, max_sample_time = max_sample_time, min_sample_time

    # Running a single execution
    print("time interval: ", (min_sample_time, max_sample_time))
    model_key = 'fraud_detection_model{tag}'
    script_key = 'helper_script{tag}'
    predict(conn, min_sample_time, max_sample_time, references_key, model_key, script_key)


if __name__ == '__main__':
    main()
