from random import randrange

import redis
import argparse
import time
import pandas as pd
import numpy as np
from random import randrange
from urllib.parse import urlparse


class DataGenerator:
    def __init__(self, conn, df):
        self._conn = conn
        self._df = df

    def generate_data(self):
        # df.to_dict('records') converts the data frame to a list of dictionaries
        records = self._df.to_dict('records')
        key_names = {}
        for record in records:
            timestamp = int(record['Time'])
            timestamp = str(timestamp)
            if timestamp not in key_names:
                key_names[timestamp] = 0
            hash_key_name = timestamp + '_' + str(key_names[timestamp])
            key_names[timestamp] = key_names[timestamp] + 1
            self._conn.hmset(hash_key_name, mapping=record)
            self._conn.zadd("transactions", {hash_key_name: timestamp})


def dictToTensor(sample, conn):
    values = np.empty((1, 30), dtype=np.float32)
    for i, key in enumerate(sample.keys()):
        value = sample[key]
        values[0][i] = value
    conn.execute_command("AI.TENSORSET", "sample", "FLOAT", "1", "30", "BLOB", values.tobytes())


def predict(df, conn, min_ts, max_ts):
    start = time.time()
    sample = df.sample(1).to_dict('records')[0]
    dictToTensor(sample, conn)
    conn.execute_command('RG.TRIGGER', 'is_fraud', str(min_ts), str(max_ts), "sample")
    print("Total execution took: " + str((time.time() - start) * 1000) + " ms")


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
        res = conn.execute_command('RG.PYEXECUTE', gear)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-rs', '--redis_server', help='Redis URL', type=str, default='redis://127.0.0.1:6379')

    args = parser.parse_args()

    # Set up redis connection
    url = urlparse(args.redis_server)
    conn = redis.Redis(host=url.hostname, port=url.port)
    if not conn.ping():
        raise Exception('Redis unavailable')
    # Read csv file
    df = pd.read_csv("data/creditcard.csv")
    # Remove classification
    del df['Class']
    # Set script
    set_script(conn)
    # Set model
    set_model(conn)
    # Set gear
    set_gear(conn)

    # Load reference data
    dg = DataGenerator(conn, df)
    dg.generate_data()

    min_ts = df["Time"].min()
    max_ts = df["Time"].max()
    while True:
        # for i in range(10000):
        min_sample_time = randrange(min_ts, max_ts)
        max_sample_time = randrange(min_ts, max_ts)
        if min_sample_time > max_sample_time:
            min_sample_time, max_sample_time = max_sample_time, min_sample_time
        predict(df, conn, min_sample_time, max_sample_time)
