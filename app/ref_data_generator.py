from random import randrange

import redis
import argparse
import pandas as pd
from urllib.parse import urlparse


class DataGenerator:
    def __init__(self, conn, df):
        self._conn = conn
        self._df = df

    def generate_data(self, user_id):
        mapping = {}
        for col in self._df.columns:
            mapping[col] = self._df[col].sample().item()
        timestamp = int(mapping['Time'])
        hash_key_name = str(user_id) + '_' + str(timestamp)
        if not self._conn.exists(hash_key_name):
            self._conn.hmset(hash_key_name, mapping=mapping)
            self._conn.zadd(user_id, {hash_key_name: timestamp})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--users', help='Number of users in the system', type=int, default=100)
    parser.add_argument('-rs', '--redis_server', help='Redis URL', type=str, default='redis://127.0.0.1:6379')

    args = parser.parse_args()

    # Get number of users
    users = args.users
    # Set up redis connection
    url = urlparse(args.redis_server)
    conn = redis.Redis(host=url.hostname, port=url.port)
    if not conn.ping():
        raise Exception('Redis unavailable')
    # Read csv file
    df = pd.read_csv("data/creditcard.csv")
    # Remove classification
    del df['Class']
    dg = DataGenerator(conn, df)

    while True:
        # Generate a sample by random sampling each column of the data set samples.
        user_id = randrange(users)
        dg.generate_data(user_id)
