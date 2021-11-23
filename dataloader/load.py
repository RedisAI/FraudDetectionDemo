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
            # Use a unique key name, which is '<time_stamp>_<index>'
            hash_key_name = timestamp + '_' + str(key_names[timestamp])
            key_names[timestamp] = key_names[timestamp] + 1

            # set reference raw data
            self._conn.hmset(hash_key_name, mapping=record)

            # add key of reference to sorted set
            self._conn.zadd("references", {hash_key_name: timestamp})


def dictToTensor(sample, keyname, conn):
    values = np.empty((1, 30), dtype=np.float32)
    for i, key in enumerate(sample.keys()):
        value = sample[key]
        values[0][i] = value
    conn.execute_command("AI.TENSORSET", keyname, "FLOAT", "1", "30", "BLOB", values.tobytes())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-rs', '--redis_server', help='Redis URL', type=str, default='redis://127.0.0.1:6379')
    parser.add_argument('-n', '--nrows', help='Number of rows to read from input file', type=str, default=1000)

    args = parser.parse_args()

    # Set up redis connection
    url = urlparse(args.redis_server)
    conn = redis.Redis(host=url.hostname, port=url.port)
    if not conn.ping():
        raise Exception('Redis unavailable')
    # Read csv file
    df = pd.read_csv("data/creditcard.csv", nrows=args.nrows)
    # Remove classification
    del df['Class']
    # Load reference data
    dg = DataGenerator(conn, df)
    dg.generate_data()
