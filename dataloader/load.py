import redis
import argparse
import time
import pandas as pd
import numpy as np
from random import randrange
from urllib.parse import urlparse


class DataGenerator:
    def __init__(self, conn, path, n_samples):
        self._conn = conn
        # Read csv file
        print("path: ", path)
        df = pd.read_csv(path, nrows=n_samples)
        print("df shape: ", df.shape)
        # Remove classification
        del df['Class']
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
            # Use a unique key name, which is '<time_stamp>_<index>{tag}'
            hash_key_name = timestamp + '_' + str(key_names[timestamp]) + '{tag}'
            key_names[timestamp] = key_names[timestamp] + 1

            # set reference raw data
            self._conn.hset(hash_key_name, mapping=record)

            # add key of reference to sorted set
            self._conn.zadd("references{tag}", {hash_key_name: timestamp})


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

    # Load reference data
    dg = DataGenerator(conn, "data/creditcard.csv", args.nrows)
    dg.generate_data()
