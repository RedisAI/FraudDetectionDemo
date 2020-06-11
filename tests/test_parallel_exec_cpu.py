import unittest
import redis
import math
import time

class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up redis connection
        cls.redis_conn = redis.Redis(host="localhost", port="6379")
        if not cls.redis_conn.ping():
            raise Exception('Redis unavailable')
        with open('../app/models/creditcardfraud.pb', 'rb') as f:
            model = f.read()
            for i in range(2):
                res = cls.redis_conn.execute_command('AI.MODELSET', 'model_'+str(i), 'TF', 'CPU', 'INPUTS', 'transaction',
                                                     'reference', 'OUTPUTS', 'output', 'BLOB', model)
                assert ('OK' == res.decode())

        with open('parallel_cpu_gear.py', 'rb') as f:
            gear = f.read()
            res = cls.redis_conn.execute_command('RG.PYEXECUTE', gear, "REQUIREMENTS", "numpy")
            assert ('OK' == res.decode())

    def tearDown(self):
        self.redis_conn.flushall()

    def test_cpu_parallel(self):
        for i in range(20):
            start = time.time()
            res = self.redis_conn.execute_command('RG.TRIGGER', 'parallel_models')
            print(time.time() - start)
            assert (math.isclose(float(res[0].decode()), 1.0, rel_tol=1e-5))


if __name__ == '__main__':
    unittest.main()
