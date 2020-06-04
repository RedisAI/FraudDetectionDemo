import redisAI
import numpy as np

def hashToTensor(record):
    hash_key = record['key']
    hash = record['value']
    values = np.empty((1, 30), dtype=np.float32)
    for i, key in enumerate(hash.keys()):
        values[0][i] = hash[key]
    tensor = redisAI.createTensorFromBlob('FLOAT', values.shape,  values.tobytes())
    redisAI.setTensorInKey(hash_key + '_tensor', tensor)


GearsBuilder('KeysReader').map(hashToTensor).register(prefix='*', eventType='Set', keyTypes=['hash'])
