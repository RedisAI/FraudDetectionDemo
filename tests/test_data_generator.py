import unittest
import redis
import pandas as pd
from app.demo import DataGenerator


class DataGeneratorTest(unittest.TestCase):
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

    def tearDown(self):
        self.redis_conn.flushall()

    def test_data_generator_hashes(self):
        self.dg.generate_data(1)
        assert (self.redis_conn.exists(1))
        keys = self.redis_conn.zrange(1, 0, 1)
        assert (len(keys) == 1)
        hash = self.redis_conn.hgetall(keys[0])
        hash_keys = list(hash.keys())
        for i in range(len(hash_keys)):
            assert (hash_keys[i].decode() == self.df.columns[i])

    def test_data_generator_sorted_sets(self):
        self.dg.generate_data(1)
        self.dg.generate_data(1)
        keys = self.redis_conn.zrange(1, 0, 2)
        assert (len(keys) == 2)
        time_0 = self.redis_conn.hget(keys[0], 'Time')
        time_1 = self.redis_conn.hget(keys[1], 'Time')
        assert (time_0 > time_1)


if __name__ == '__main__':
    unittest.main()
