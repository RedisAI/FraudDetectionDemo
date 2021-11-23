import redis
from redisai import Client
import argparse
import time
import numpy as np
from random import randrange
from urllib.parse import urlparse

def predict(conn, min_ts, max_ts):
    start = time.time()

    # Create a random transaction tensor
    transaction_tensor = np.random.randn(1, 30).astype(np.float32)

    # Find the relevant reference data (transaction that occurred within the time interval)
    ref_data_keys = conn.zrangebyscore("references", min_ts, max_ts)
    print(ref_data_keys)

    # Create a DAG (execution plan) for RedisAI. First, use the helper script to convert the reference data
    # within the hashes into a tensor. Then run the 2 models and obtain 2 outputs,
    # and finally use the helper script to take their average to be the result (and persist it in key space)
    output_key_name = 'result{1}'
    dag = conn.dag(persist=[output_key_name])
    dag.tensorset('transaction', transaction_tensor)
    dag.scriptexecute('helper_script', 'hash_to_tensors', keys=[ref_data_keys], outputs=['reference'])
    dag.modelexecute('model_1', inputs=['transaction', 'reference'], outputs=['out_1'])
    dag.modelexecute('model_2', inputs=['transaction', 'reference'], outputs=['out_2'])
    dag.scriptexecute('helper_script', 'post_processing', inputs=['out_1', 'out_2'], outputs=[output_key_name])
    dag.execute()

    # get result
    result = conn.tensorget(output_key_name)
    # result = conn.execute_command('AI.TENSORGET','model_result','VALUES')
    print("result: ", result)
    print("Total execution took: " + str((time.time() - start) * 1000) + " ms")


if __name__ == '__main__':
    # Set up redis connection
    conn = Client(host='localhost', port=6379)
    if not conn.ping():
        raise Exception('Redis unavailable')

    min_ts = conn.zrangebyscore("references", "-inf", "+inf", withscores=True, start=0, num=1)[0][1]
    max_ts = conn.zrevrangebyscore("references", "+inf", "-inf", withscores=True, start=0, num=1)[0][1]

    # Running a single execution
    min_sample_time = randrange(min_ts, max_ts)
    max_sample_time = randrange(min_ts, max_ts)
    if min_sample_time > max_sample_time:
        min_sample_time, max_sample_time = max_sample_time, min_sample_time
    predict(conn, min_sample_time, max_sample_time)
