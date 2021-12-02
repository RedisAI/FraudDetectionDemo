import unittest
from multiprocessing import Process
import numpy as np

from redisai import Client
from dataloader import load
from app import app_runner


class FraudDetectionDemoTest(unittest.TestCase):
    redisai_conn = Client(host='localhost', port=6379)
    n_samples = 1000
    dg = load.DataGenerator(redisai_conn, "dataloader/data/creditcard.csv", n_samples)

    model_key = 'fraud_detection_model{tag}'
    script_key = 'helper_script{tag}'
    references_key = 'references{tag}'

    def tearDown(self):
        self.redisai_conn.flushall()

    def test_data_generator_from_csv(self):
        # Load 1000 rows from the data csv
        self.dg.generate_data()
        assert (self.redisai_conn.dbsize() == self.n_samples + 1)  # key for every sample + the references sorted set

        # Expect all hash keys to be stored in the sorted set
        all_keys = self.redisai_conn.zrange(self.references_key, 0, 1001)
        assert (len(all_keys) == self.n_samples)

        # Expect 2 keys with with score=0 (which correspond to transactions in Time=0)
        keys = self.redisai_conn.zrange(self.references_key, 0, 1)
        assert (len(keys) == 2)

        # Assert the keys of the hash are the columns names
        first_hash = self.redisai_conn.hgetall(keys[0])
        hash_keys = list(first_hash.keys())
        assert (len(hash_keys) == len(self.dg._df.columns))
        for i in range(len(hash_keys)):
            assert (hash_keys[i].decode() == self.dg._df.columns[i])

        # Assert the values of the hash are the first row values
        for key in hash_keys:
            assert (first_hash[key].decode() == str(self.dg._df[key.decode()][0]))

    def test_hashes_to_tensor(self):
        app = app_runner.FraudDetectionApp(self.redisai_conn)

        # Set the script in Redis
        app.set_script('app/script.py', self.script_key)

        # Create a tensor from the first 10 hashes by using the script (store it in redis)
        self.dg.generate_data()
        hashes_keys = self.redisai_conn.zrange(self.references_key, 0, 9)
        assert (len(hashes_keys) == 10)
        output_key = 'out_tensor{tag}'
        self.redisai_conn.scriptexecute(self.script_key, 'hashes_to_tensor', keys=hashes_keys, outputs=[output_key])

        # get the result and verify it's meta data
        result = self.redisai_conn.tensorget(output_key, meta_only=True)
        assert (result['dtype'] == 'FLOAT')
        assert (result['shape'] == [1, 256])

    def test_entire_flow_multiple_clients(self):
        app = app_runner.FraudDetectionApp(self.redisai_conn)
        app.set_script('app/script.py', 'helper_script{tag}')
        app.set_model('app/models/creditcardfraud.pb', 'fraud_detection_model{tag}')
        self.dg.generate_data()

        def run_demo(output_key_name):
            # Create a random transaction tensor in Time=100
            transaction_tensor = np.random.randn(1, 30).astype(np.float32)
            transaction_tensor[0] = 100

            # Find the relevant reference data (transaction that occurred within the past 60 seconds)
            ref_data_keys = self.redisai_conn.zrangebyscore(self.references_key, 40, 100)

            # Create a DAG (execution plan) for RedisAI. First, use the helper script to convert the reference data
            # within the hashes into a tensor. Then run the model twice and obtain 2 outputs,
            # and finally use the helper script to take their average to be the result (and persist it in key space)
            dag = self.redisai_conn.dag(persist=[output_key_name])
            dag.tensorset('transaction', transaction_tensor)
            dag.scriptexecute(self.script_key, 'hashes_to_tensor', keys=ref_data_keys, outputs=['reference'])
            dag.modelexecute(self.model_key+'_CPU', inputs=['transaction', 'reference'], outputs=['out_1'])
            dag.modelexecute(self.model_key+'_CPU:1', inputs=['transaction', 'reference'], outputs=['out_2'])
            dag.scriptexecute(self.script_key, 'post_processing', inputs=['out_1', 'out_2'], outputs=[output_key_name])
            dag.execute()

        # run the demo scenario from multiple clients
        n_clients = 10
        clients = []
        for i in range(n_clients):
            client_output = 'result{tag}' + str(i)
            p = Process(target=run_demo(client_output))
            p.start()
            clients.append(p)
        # Wait for all clients to finish
        [c.join() for c in clients]

        # assert valid results
        for i in range(n_clients):
            client_output = 'result{tag}' + str(i)
            result = np.reshape(self.redisai_conn.tensorget(client_output), -1)
            assert (result.shape == (2,))
            assert ((0 <= result.all()) & (result.all() <= 100))


if __name__ == '__main__':
    unittest.main()
