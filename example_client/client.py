import redis
import argparse
import time
from random import randrange
from urllib.parse import urlparse

def predict(conn, min_ts, max_ts):
    start = time.time()
    # TODO Set transaction
    conn.execute_command('RG.TRIGGER', 'is_fraud', str(min_ts), str(max_ts), "transaction")
    result = conn.execute_command('AI.TENSORGET','model_result','VALUES')
    print(result)
    print("Total execution took: " + str((time.time() - start) * 1000) + " ms")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-rs', '--redis_server', help='Redis URL', type=str, default='redis://127.0.0.1:6379')

    args = parser.parse_args()

    # Set up redis connection
    url = urlparse(args.redis_server)
    conn = redis.Redis(host=url.hostname, port=url.port)
    if not conn.ping():
        raise Exception('Redis unavailable')


    # TODO get min max from sorted set
    min_ts = 0
    max_ts = 500

    # Running a single execution
    min_sample_time = randrange(min_ts, max_ts)
    max_sample_time = randrange(min_ts, max_ts)
    if min_sample_time > max_sample_time:
        min_sample_time, max_sample_time = max_sample_time, min_sample_time
    predict(conn, min_sample_time, max_sample_time)
