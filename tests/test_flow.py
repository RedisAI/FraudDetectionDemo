import unittest
from redisai import Client
import pandas as pd
from dataloader.load import DataGenerator
from app.app import FraudDetectionApp


class DataGeneratorTest(unittest.TestCase):
    n_samples = None
    redis_conn = None

    @classmethod
    def setUpClass(cls):
        # Set up redis connection
        cls.redis_conn = Client(host='localhost', port=6379)
        if not cls.redis_conn.ping():
            raise Exception('Redis unavailable')
        
        cls.n_samples = 1000
        cls.dg = DataGenerator(cls.redis_conn, "../dataloader/data/creditcard.csv", cls.n_samples)

    def tearDown(self):
        self.redis_conn.flushall()

    def test_data_generator_from_csv(self):
        # Load 1000 rows from the data csv
        self.dg.generate_data()
        assert (self.redis_conn.dbsize() == self.n_samples + 1)  # key for every sample + the references sorted set

        # Expect all hash keys to be stored in the sorted set
        references_key = 'references{tag}'
        all_keys = self.redis_conn.zrange(references_key, 0, 1001)
        assert (len(all_keys) == self.n_samples)

        # Expect 2 keys with with score=0 (which correspond to transactions in t = 0)
        keys = self.redis_conn.zrange(references_key, 0, 1)
        assert (len(keys) == 2)

        # Assert the keys of the hash are the columns names
        first_hash = self.redis_conn.hgetall(keys[0])
        hash_keys = list(first_hash.keys())
        assert (len(hash_keys) == len(self.dg._df.columns))
        for i in range(len(hash_keys)):
            assert (hash_keys[i].decode() == self.dg._df.columns[i])

        # Assert the values of the hash are the first row values
        for key in hash_keys:
            assert (first_hash[key].decode() == str(self.dg._df[key.decode()][0]))

    def test_hash_to_blob(self):
        app = FraudDetectionApp(self.redis_conn)

        # Set the script in Redis
        script_key = 'helper_script{tag}'
        app.set_script('../app/script.py', script_key)

        # Create a tensor from the first 10 hashes by using the script (store it in redis)
        self.dg.generate_data()
        references_key = 'references{tag}'
        hashes_keys = self.redis_conn.zrange(references_key, 0, 9)
        assert (len(hashes_keys) == 10)
        output_key = 'out_tensor{tag}'
        self.redis_conn.scriptexecute(script_key, 'hashes_to_tensor', keys=hashes_keys, outputs=[output_key])

        # get the result and verify it's meta data
        result = self.redis_conn.tensorget(output_key, meta_only=True)
        assert (result['dtype'] == 'FLOAT')
        assert (result['shape'] == [1, 256])

    def test_entire_flow_multiple_clients(self):


if __name__ == '__main__':
    unittest.main()
