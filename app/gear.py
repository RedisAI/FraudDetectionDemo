import redisAI
import numpy as np


def is_fraud(record):
    # Retrive tensors from keyspace
    # Range query with limit 100. (Without limit it can return 100-150K results which reduce performance)
    ref_data_keys = execute("ZRANGEBYSCORE", "transactions", record[1], record[2], "LIMIT", "0", "100")
    # Set "_tensor" suffix for every returned key
    keys = [x + "_tensor" for x in ref_data_keys]
    # Append the new transaction tensor key
    keys.append(record[3])
    # Do mgetTensors from the keyspace
    tensors = redisAI.mgetTensorsFromKeyspace(keys)

    # Take the reference data tensors and the sample data
    ref_data = tensors[:len(tensors) - 2]
    new_sample = tensors[len(tensors) - 1]

    # Create a new reference tensor out the of the reference data from the keyspace, with a torch script
    scriptRunner = redisAI.createScriptRunner('concat_script', 'concat_tensors')
    redisAI.scriptRunnerAddInputList(scriptRunner, ref_data)
    redisAI.scriptRunnerAddOutput(scriptRunner)

    # Run two models over the reference data and the transaction
    ref_data = redisAI.scriptRunnerRun(scriptRunner)[0]
    modelRunner = redisAI.createModelRunner('model_1')
    redisAI.modelRunnerAddInput(modelRunner, 'transaction', new_sample)
    redisAI.modelRunnerAddInput(modelRunner, 'reference', ref_data)
    redisAI.modelRunnerAddOutput(modelRunner, 'output')
    output_1 = redisAI.modelRunnerRun(modelRunner)[0]
    modelRunner = redisAI.createModelRunner('model_2')
    redisAI.modelRunnerAddInput(modelRunner, 'transaction', new_sample)
    redisAI.modelRunnerAddInput(modelRunner, 'reference', ref_data)
    redisAI.modelRunnerAddOutput(modelRunner, 'output')
    output_2 = redisAI.modelRunnerRun(modelRunner)[0]

    # Average the results with numpy and set in keyspace
    shape = redisAI.tensorGetDims(output_1)
    reply_ndarray_0 = np.frombuffer(redisAI.tensorGetDataAsBlob(output_1), dtype=np.float32).reshape(shape)
    reply_ndarray_1 = np.frombuffer(redisAI.tensorGetDataAsBlob(output_2), dtype=np.float32).reshape(shape)
    res = (reply_ndarray_0 + reply_ndarray_1) / 2.0
    output = redisAI.createTensorFromBlob('FLOAT', res.shape, res.tobytes())
    redisAI.setTensorInKey('model_result', output)


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
