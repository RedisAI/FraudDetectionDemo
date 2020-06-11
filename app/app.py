from random import randrange

import redis
import argparse
import time
from random import randrange
from urllib.parse import urlparse


def set_script(conn):
    with open('script.torch', 'rb') as f:
        script = f.read()
        res = conn.execute_command('AI.SCRIPTSET', 'concat_script', 'CPU', 'SOURCE', script)


def set_model(conn):
    with open('../app/models/creditcardfraud.pb', 'rb') as f:
        model = f.read()
        res = conn.execute_command('AI.MODELSET', 'model_1', 'TF', 'CPU', 'INPUTS', 'transaction',
                                   'reference', 'OUTPUTS', 'output', 'BLOB', model)
        res = conn.execute_command('AI.MODELSET', 'model_2', 'TF', 'CPU', 'INPUTS', 'transaction',
                                   'reference', 'OUTPUTS', 'output', 'BLOB', model)

def set_gear(conn):
    with open('gear.py', 'rb') as f:
        gear = f.read()
        res = conn.execute_command('RG.PYEXECUTE', gear, 'REQUIREMENTS', 'numpy')


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
    # Set gear
    set_gear(conn)
