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
        with open('script.torch', 'rb') as f:
            script = f.read()
            res = cls.redis_conn.execute_command('AI.SCRIPTSET', 'my_script', 'CPU', 'SOURCE', script)
            assert ('OK' == res.decode())

        with open('torch_script_gear.py', 'rb') as f:
            gear = f.read()
            res = cls.redis_conn.execute_command('RG.PYEXECUTE', gear)
            assert ('OK' == res.decode())

    def test_script(self):
        tensor_a = np.random.randn(1, 30).astype(np.float32)
        tensor_b = np.random.randn(1, 30).astype(np.float32)
        res = self.redis_conn.execute_command('AI.TENSORSET', 'tensor_a', 'FLOAT', '1', '30', 'BLOB',
                                              tensor_a.tobytes())
        assert ('OK' == res.decode())
        res = self.redis_conn.execute_command('AI.TENSORSET', 'tensor_b', 'FLOAT', '1', '30', 'BLOB',
                                              tensor_b.tobytes())
        assert ('OK' == res.decode())
        self.redis_conn.execute_command('RG.TRIGGER', 'addTensors')
        script_reply = np.frombuffer(self.redis_conn.execute_command("AI.TENSORGET", "script_reply", "BLOB"),
                                     np.float32)

        assert (np.all(np.equal(script_reply[0:30], tensor_a[0])))
        assert (np.all(np.equal(script_reply[30:60], tensor_b[0])))

if __name__ == '__main__':
    unittest.main()
