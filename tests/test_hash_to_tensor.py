import io
import unittest
from time import sleep

import redis
import pandas as pd
import numpy as np
from app.ref_data_generator import DataGenerator


class TestHashToTensor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up redis connection
        cls.redis_conn = redis.Redis(host="localhost", port="6379")
        if not cls.redis_conn.ping():
            raise Exception('Redis unavailable')
        # Read csv file
        cls.df = pd.read_csv("../app/data/creditcard.csv")
        # Remove classification
        del cls.df['Class']
        cls.dg = DataGenerator(cls.redis_conn, cls.df)
        with open('../app/gear.py', 'rb') as f:
            gear = f.read()
            res = cls.redis_conn.execute_command('RG.PYEXECUTE', gear, 'REQUIREMENTS', 'numpy')

    # def tearDown(self):
    #     self.redis_conn.flushall()

    def test_hashblob(self):
        self.dg.generate_data(1)
        keys = self.redis_conn.zrange(1, 0, 1)
        hash = self.redis_conn.hgetall(keys[0])
        print(keys[0].decode())
        tensor = self.redis_conn.execute_command("AI.TENSORGET", (keys[0].decode())+"_tensor", "BLOB")
        nparray = np.frombuffer(tensor, dtype=np.float32)
        assert(pd.Series(nparray).isin(np.array(list(hash.values()), dtype=np.float32)).any())
if __name__ == '__main__':
    unittest.main()
