import redisAI
import numpy as np
import time


def is_fraud(record):
    start = time.time()
    ref_data_keys = execute("ZRANGEBYSCORE", "transactions", record[1], record[2], "LIMIT", "0", "100")
    log('ZRANGEBYSCORE=' + str(time.time() - start))
    keys = [x + "_tensor" for x in ref_data_keys]
    keys.append(record[3])
    tensors = redisAI.mgetTensorsFromKeyspace(keys)
    log('mget=' + str(time.time() - start))
    ref_data = tensors[:len(tensors) - 2]
    new_sample = tensors[len(tensors) - 1]
    scriptRunner = redisAI.createScriptRunner('concat_script', 'concat_tensors')
    redisAI.scriptRunnerAddInputList(scriptRunner, ref_data)
    redisAI.scriptRunnerAddOutput(scriptRunner)
    ref_data = redisAI.scriptRunnerRun(scriptRunner)[0]
    log('script done=' + str(time.time() - start))
    modelRunner = redisAI.createModelRunner('model')
    redisAI.modelRunnerAddInput(modelRunner, 'transaction', new_sample)
    redisAI.modelRunnerAddInput(modelRunner, 'reference', ref_data)
    redisAI.modelRunnerAddOutput(modelRunner, 'output')
    output = redisAI.modelRunnerRun(modelRunner)[0]
    redisAI.setTensorInKey('model_result', output)
    log('model done=' + str(time.time() - start))


def hashToTensor(record):
    hash_key = record['key']
    hash = record['value']
    values = np.empty((1, 30), dtype=np.float32)
    for i, key in enumerate(hash.keys()):
        values[0][i] = hash[key]
    tensor = redisAI.createTensorFromBlob('FLOAT', values.shape, values.tobytes())
    redisAI.setTensorInKey(hash_key + '_tensor', tensor)


GearsBuilder('KeysReader').map(hashToTensor).register(prefix='*', eventType='Set', keyTypes=['hash'])

GearsBuilder('CommandReader').map(is_fraud).register(trigger='is_fraud')
