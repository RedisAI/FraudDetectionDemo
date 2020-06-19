[![license](https://img.shields.io/github/license/RedisAI/FraudDetectionDemo.svg)](https://github.com/RedisAI/FraudDetectionDemo)
[![Action](https://github.com/RedisAI/FraudDetectionDemo/workflows/Docker-CI/badge.svg)](https://github.com/RedisAI/FraudDetectionDemo/actions?query=workflow%3ADocker-CI)
[![Forum](https://img.shields.io/badge/Forum-RedisAI-blue)](https://forum.redislabs.com/c/modules/redisai)
[![Gitter](https://badges.gitter.im/RedisLabs/RedisAI.svg)](https://gitter.im/RedisLabs/RedisAI?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

# FraudDetectionDemo

This demo combines several [Redis](https://redis.io) data structures and [Redis Modules](https://redis.io/topics/modules-intro)
to showcase the advantage of data locality during transaction scoring.

It uses:

* [RedisGears](https://oss.redislabs.com/redisgears/) to orchestrate the transactions and preprocessing the data
* [RedisAI](https://oss.redislabs.com/redisai/) to preprocess the data and to run several DL/ML models

## Architecture
### Flow 1: Updating reference data
Raw reference data is kept in Redis that can be fed as input to DL/ML models.  In order to save processing time during inferencing, the raw reference data is converted into tensors on each update.

The reference data for the transaction scoring is modelled as Redis Hashes. A sorted set keeps track of the keynames of these hashes sorted by time.

A first RedisGears [function](https://oss.redislabs.com/redisgears/functions.html) is triggered on each update of the reference data. It registers to `SET` events of the type `hash`. This function itself is converting the hash into a tensor and stores it back into Redis (using the `hashToTensor` method).
`numpy` is used in the function to serialise the values of the hash into an
`ndarray` with a shape `(1, 30)` after which it's stored as a [RedisAI tensor](https://oss.redislabs.com/redisai/intro/#using-redisai-tensors).

![Updating reference data](./flow1.png "Updating reference data")


### Flow 2: Transaction scoring
![High level architecture](./flow2.png "High level architecture")

Once a transation needs to be evaluated, we set it as a tensor in the keyspace with a shape of `(1, 30)` and trigger a gear with the tensor key name
and a time range, represented by two timestamps. The gear then executes a range query over the sorted set (`ZRANGEBYSCORE`)
and retrieve a list of hash names (recall that each hash has a corresponding tensor).

![Gears<->Redis data gathering](./flow3.png "Gears<->Redis data gathering")

From this list it extracts a list of tensor from the keyspace and sends it to a Torch script. This torch script creates a
new tensor with the shape `(1, 256)` out of the list, by concatenating the tensors and either pad the remaining space or trimming it.
The new tensor is the reference data for the models which expect a reference data with shape of `(1, 256)` and transaction data
with shape of `(1, 30)`. Onc the models are done, the gear uses `numpy` to aggregate the results and save them to a tensor
with shape `(1, 2)` that contains the probability for the transaction to be a fraud.

![Gears<->AI execution](./flow4.png "Gears<->AI execution")
## Running the Demo
To run the demo:
```
$ git clone https://github.com/RedisAI/FraudDetectionDemo.git
$ cd FraudDetectionDemo
# If you don't have it already, install https://git-lfs.github.com/ (On OSX: brew install git-lfs)
$ git lfs install && git lfs fetch && git lfs checkout
$ docker-compose up
```
If something went wrong, e.g. you skipped installing git-lfs, you need to force docker-compose to rebuild the containers
```
$ docker-compose up --force-recreate --build
```
Explore all data and RedisGears functions with RedisInsight
https://localhost:8001

### Testing Flow 1


### Testing Flow 2
Open a second terminal to emulate the client connecting to redis:
```
$ pip install -r example_client/requirements.txt
$ python example_client/client.py
```
