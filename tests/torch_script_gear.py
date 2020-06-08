import redisAI

def addTensors(x):
    tensors = redisAI.mgetTensorsFromKeyspace(['tensor_a'])
    tensors.append(redisAI.getTensorFromKey('tensor_b'))
    log(str(redisAI.tensorGetDims(tensors[0])))
    log(str(redisAI.tensorGetDims(tensors[1])))
    scriptRunner = redisAI.createScriptRunner('my_script', 'concat_tensors')
    redisAI.scriptRunnerAddInputList(scriptRunner, tensors)
    redisAI.scriptRunnerAddOutput(scriptRunner)
    script_reply = redisAI.scriptRunnerRun(scriptRunner)
    redisAI.setTensorInKey('script_reply', script_reply[0])
    redisAI.msetTensorsInKeyspace({'script_reply_1': script_reply[0]})


gb = GB('CommandReader')
gb.map(addTensors)
gb.register(trigger='addTensors')
