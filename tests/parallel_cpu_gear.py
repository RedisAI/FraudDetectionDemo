import redisAI
import numpy as np
from concurrent.futures import ThreadPoolExecutor

executor = None


def execute_model(i, transaction_tensor, reference_tensor):
    modelRunner = redisAI.createModelRunner('model_'+str(i))
    redisAI.modelRunnerAddInput(modelRunner, 'transaction', transaction_tensor)
    redisAI.modelRunnerAddInput(modelRunner, 'reference', reference_tensor)
    redisAI.modelRunnerAddOutput(modelRunner, 'output')
    model_replies = redisAI.modelRunnerRun(modelRunner)
    return model_replies[0]

def parallel_models(x):
    global executor
    transaction_ndarray = np.random.randn(1, 30).astype(np.float32)
    reference_ndarray = np.random.randn(1, 256).astype(np.float32)
    transaction_tensor = redisAI.createTensorFromBlob('FLOAT', transaction_ndarray.shape,
                                                      transaction_ndarray.tobytes())
    reference_tensor = redisAI.createTensorFromBlob('FLOAT', reference_ndarray.shape,
                                                    reference_ndarray.tobytes())
    models_reply = [None]*2
    for i in range(2):
        models_reply[i] = executor.submit(execute_model, i, transaction_tensor, reference_tensor)

    reply_tensor_0 = models_reply[0].result()
    reply_tensor_1 = models_reply[1].result()
    # reply_tensor_0 = execute_model (transaction_tensor, reference_tensor)
    # reply_tensor_1 = execute_model (transaction_tensor, reference_tensor)
    shape = redisAI.tensorGetDims(reply_tensor_0)
    reply_ndarray_0 = np.frombuffer(redisAI.tensorGetDataAsBlob(reply_tensor_0), dtype=np.float32).reshape(shape)
    reply_ndarray_1 = np.frombuffer(redisAI.tensorGetDataAsBlob(reply_tensor_1), dtype=np.float32).reshape(shape)
    # reply_ndarray_1 = np.empty((1,2))

    res = (reply_ndarray_0 + reply_ndarray_1) / 2.0
    return (res[0][0]+res[0][1])

def init():
    global executor
    executor = ThreadPoolExecutor()

gb = GB('CommandReader')
gb.map(parallel_models)
gb.register(trigger='parallel_models', onRegistered=init)
