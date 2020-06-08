import unittest
import redis
import numpy as np

class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up redis connection
        cls.redis_conn = redis.Redis(host="localhost", port="6379")
        if not cls.redis_conn.ping():
            raise Exception('Redis unavailable')
        with open('mget_gear.py', 'rb') as f:
            gear = f.read()
            res = cls.redis_conn.execute_command('RG.PYEXECUTE', gear)

    def test_something(self):
        tensor = np.random.randn(1, 30).astype(np.float32)
        res = self.redis_conn.execute_command('AI.TENSORSET', 'tensor', 'FLOAT', '1', '30', 'BLOB',
                                              tensor.tobytes())
        for i in range(10000):
            self.redis_conn.execute_command('RG.TRIGGER', 'test_mget')



if __name__ == '__main__':
    unittest.main()
