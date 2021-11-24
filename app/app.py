from redisai import Client


class FraudDetectionApp:
    def __init__(self, con_):
        self.con = con_

    def set_script(self, path, script_key):
        with open(path, 'rb') as f:
            script = f.read()
            self.con.scriptstore(script_key, 'CPU', script, entry_points=['hashes_to_tensor', 'post_processing'])

    def set_models(self, path, model_key_prefix):
        with open(path, 'rb') as f:
            model = f.read()
            self.con.modelstore(model_key_prefix+'_1', 'TF', 'CPU', data=model, inputs=['transaction', 'reference'], outputs=['output'])
            self.con.modelstore(model_key_prefix+'_2', 'TF', 'CPU', data=model, inputs=['transaction', 'reference'], outputs=['output'])


if __name__ == '__main__':
    conn = Client(host='localhost', port=6379)
    if not conn.ping():
        raise Exception('Redis unavailable')

    app = FraudDetectionApp(conn)
    # Set script
    app.set_script('script.py', 'helper_script{tag}')
    # Set models
    app.set_models('../app/models/creditcardfraud.pb', 'fraud_detection_model{tag}')
