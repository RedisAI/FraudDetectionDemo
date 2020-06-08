import redisAI


def test(record):
    tensors = redisAI.mgetTensorsFromKeyspace(["tensor"])

GearsBuilder('CommandReader').map(test).register(trigger='test_mget')
