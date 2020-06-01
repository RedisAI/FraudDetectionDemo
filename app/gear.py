import io

import numpy as np
import re
def hashToTensor(record):
    hash_key = record['key']
    hash = record['value']
    values = np.empty((1, 30), dtype=np.float32)
    for i, key in enumerate(hash.keys()):
        values[0][i] = hash[key]
    execute('AI.TENSORSET', hash_key + '_tensor', 'FLOAT', '1', '30', 'BLOB', values.tobytes())


GearsBuilder('KeysReader').map(hashToTensor).register(prefix='*', eventType='Set', keyTypes=['hash'])
