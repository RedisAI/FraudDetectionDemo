import argparse
from urllib.parse import urlparse

from redisai import Client


class FraudDetectionApp:
    def __init__(self, con_):
        self.con = con_

    def set_script(self, path, script_key):
        with open(path, 'rb') as f:
            script = f.read()
            self.con.scriptstore(script_key, 'CPU', script, entry_points=['hashes_to_tensor', 'post_processing'])

    def set_model(self, path, model_key):
        with open(path, 'rb') as f:
            model = f.read()
            self.con.modelstore(model_key+'_CPU', 'TF', 'CPU', data=model, inputs=['transaction', 'reference'], outputs=['output'])
            self.con.modelstore(model_key+'_CPU:1', 'TF', 'CPU', data=model, inputs=['transaction', 'reference'], outputs=['output'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-rs', '--redis_server', help='Redis URL', type=str, default='redis://127.0.0.1:6379')
    args = parser.parse_args()

    # Set up redis connection
    url = urlparse(args.redis_server)
    conn = Client(host=url.hostname, port=url.port)
    if not conn.ping():
        raise Exception('Redis unavailable')

    app = FraudDetectionApp(conn)
    # Set script
    app.set_script('script.py', 'helper_script{tag}')
    # Set models
    app.set_model('../app/models/creditcardfraud.pb', 'fraud_detection_model{tag}')
