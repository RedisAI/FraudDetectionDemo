[![license](https://img.shields.io/github/license/RedisAI/FraudDetectionDemo.svg)](https://github.com/RedisAI/FraudDetectionDemo)
[![Action](https://github.com/RedisAI/FraudDetectionDemo/workflows/Docker-CI/badge.svg)](https://github.com/RedisAI/FraudDetectionDemo/actions?query=workflow%3ADocker-CI)
[![Forum](https://img.shields.io/badge/Forum-RedisAI-blue)](https://forum.redislabs.com/c/modules/redisai)
[![Gitter](https://badges.gitter.im/RedisLabs/RedisAI.svg)](https://gitter.im/RedisLabs/RedisAI?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

# FraudDetectionDemo

This demo combines several [Redis](https://redis.io) data structures and [Redis Modules](https://redis.io/topics/modules-intro)
to showcase the advantage of data locality during transaction scoring .

It uses:

* [RedisGears](https://oss.redislabs.com/redisgears/) to orchestrate the transactions and preprocessing the data
* [RedisAI](https://oss.redislabs.com/redisai/) to preproces the data and run several AI models

## Architecture
### Flow 1: Updating reference data
The user reference data is represented by a Redis sorted set mapping between reference transactions timestamps and the
reference transaction key names. The reference transactions themselves, each stored as a Redis hash. 

A gear is registered to listen to `SET` events of the `hash` type. This gear is mapping the hash into a tensor and sets
it in the keyspace using `hashToTensor` function. Using `numpy`, this function serlizes the values of the hash into an
`ndarray` with shape `(1, 30)`, creates a tensor object and sets it into the keyspace.


![Updating reference data](./flow1.png "Updating reference data")


### Flow 2: Transaction scoring
![High level architecture](./flow2.png "High level architecture")

Once a transation needs to be evaluated, we set it as a tensor in the keyspace with a shape of `(1, 30)` and trigger a gear with the tensor key name
and a time range, represented by two timestamps. The gear then executes a range query over the sorted set (`ZRANGEBYSCORE`) 
and retrieve a list of hash names (recall that each hash has a corresponding tensor).

![Architecture](./flow3.png)

From this list it extracts a list of tensor from the keyspace and sends it to a Torch script. This torch script creates a
new tensor with the shape `(1, 256)` out of the list, by concatenating the tensors and either pad the remaining space or trimming it.
The new tensor is the reference data for the models which expect a reference data with shape of `(1, 256)` and transaction data 
with shape of `(1, 30)`. Onc the models are done, the gear uses `numpy` to aggregate the results and save them to a tensor
with shape `(1, 2)` that contains the probability for the transaction to be a fraud.

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
