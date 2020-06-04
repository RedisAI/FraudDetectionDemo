import redisAI

def addTensors(x):
    tensor_a = redisAI.getTensorFromKey('tensor_a')
    tensor_b = redisAI.getTensorFromKey('tensor_b')
    scriptRunner = redisAI.createScriptRunner('my_script', 'concat_tensors')
    redisAI.scriptRunnerAddInputList(scriptRunner, [tensor_a, tensor_b])
    redisAI.scriptRunnerAddOutput(scriptRunner)
    script_reply = redisAI.scriptRunnerRun(scriptRunner)
    redisAI.setTensorInKey('script_reply', script_reply[0])


gb = GB('CommandReader')
gb.map(addTensors)
gb.register(trigger='addTensors')
