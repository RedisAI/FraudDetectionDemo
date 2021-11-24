import unittest

import numpy as np
from redisai import Client
import pandas as pd
from dataloader.load import DataGenerator
from app.app import FraudDetectionApp


class DataGeneratorTest(unittest.TestCase):
    n_samples = None
    redis_conn = None
    model_key = 'fraud_detection_model{tag}'
    script_key = 'helper_script{tag}'
    references_key = 'references{tag}'

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
        all_keys = self.redis_conn.zrange(self.references_key, 0, 1001)
        assert (len(all_keys) == self.n_samples)

        # Expect 2 keys with with score=0 (which correspond to transactions in t = 0)
        keys = self.redis_conn.zrange(self.references_key, 0, 1)
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
        app.set_script('../app/script.py', self.script_key)

        # Create a tensor from the first 10 hashes by using the script (store it in redis)
        self.dg.generate_data()
        hashes_keys = self.redis_conn.zrange(self.references_key, 0, 9)
        assert (len(hashes_keys) == 10)
        output_key = 'out_tensor{tag}'
        self.redis_conn.scriptexecute(self.script_key, 'hashes_to_tensor', keys=hashes_keys, outputs=[output_key])

        # get the result and verify it's meta data
        result = self.redis_conn.tensorget(output_key, meta_only=True)
        assert (result['dtype'] == 'FLOAT')
        assert (result['shape'] == [1, 256])

    def test_entire_flow_multiple_clients(self):
        app = FraudDetectionApp(self.redis_conn)
        app.set_script('../app/script.py', 'helper_script{tag}')
        app.set_model('../app/models/creditcardfraud.pb', 'fraud_detection_model{tag}')
        self.dg.generate_data()

        # Create a random transaction tensor in Time=100
        transaction_tensor = np.random.randn(1, 30).astype(np.float32)
        transaction_tensor[0] = 100

        # Find the relevant reference data (transaction that occurred within the past 60 seconds)
        ref_data_keys = self.redis_conn.zrangebyscore(self.references_key, 40, 100)

        # Create a DAG (execution plan) for RedisAI. First, use the helper script to convert the reference data
        # within the hashes into a tensor. Then run the model twice and obtain 2 outputs,
        # and finally use the helper script to take their average to be the result (and persist it in key space)
        output_key_name = 'result{tag}'
        dag = self.redis_conn.dag(persist=[output_key_name])
        dag.tensorset('transaction', transaction_tensor)
        dag.scriptexecute(self.script_key, 'hashes_to_tensor', keys=ref_data_keys, outputs=['reference'])
        dag.modelexecute(self.model_key, inputs=['transaction', 'reference'], outputs=['out_1'])
        dag.modelexecute(self.model_key, inputs=['transaction', 'reference'], outputs=['out_2'])
        dag.scriptexecute(self.script_key, 'post_processing', inputs=['out_1', 'out_2'], outputs=[output_key_name])
        dag.execute()

        # assert valid result
        result = self.redis_conn.tensorget(output_key_name)
        assert (len(result[0]) == 2)
        assert (0 <= result[0][0] <= 100 and 0 <= result[0][1] <= 100)


if __name__ == '__main__':
    unittest.main()
