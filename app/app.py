from random import randrange

import redis
import argparse
import time
from random import randrange
from urllib.parse import urlparse


def set_script(conn):
    with open('script.py', 'rb') as f:
        script = f.read()
        res = conn.execute_command('AI.SCRIPTSTORE', 'helper_script', 'CPU',
                                   'ENTRY_POINTS', 2, 'hashes_to_tensor', 'post_processing', 'SOURCE', script)


def set_model(conn):
    with open('../app/models/creditcardfraud.pb', 'rb') as f:
        model = f.read()
        res = conn.execute_command('AI.MODELSTORE', 'model_1', 'TF', 'CPU', 'INPUTS', 2, 'transaction',
                                   'reference', 'OUTPUTS', 1, 'output', 'BLOB', model)
        res = conn.execute_command('AI.MODELSTORE', 'model_2', 'TF', 'CPU', 'INPUTS', 2, 'transaction',
                                   'reference', 'OUTPUTS', 1, 'output', 'BLOB', model)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-rs', '--redis_server', help='Redis URL', type=str, default='redis://127.0.0.1:6379')

    args = parser.parse_args()

    # Set up redis connection
    url = urlparse(args.redis_server)
    conn = redis.Redis(host=url.hostname, port=url.port)
    if not conn.ping():
        raise Exception('Redis unavailable')

    # Set script
    set_script(conn)
    # Set model
    set_model(conn)
