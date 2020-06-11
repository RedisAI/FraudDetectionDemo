# FraudDetectionDemo

This demo combines several [Redis](https://redis.io) data structures and [Redis Modules](https://redis.io/topics/modules-intro)
to showcase the advantage of data locality during transaction scoring .

It uses:

* [RedisGears](https://oss.redislabs.com/redisgears/) to orchestrate the transactions and preprocessing the data
* [RedisAI](https://oss.redislabs.com/redisai/) to preproces the data and run several AI models

## Architecture
### Flow 1: Updating reference data
![Architecture](/flow1.png)
### Flow 2: Transaction scoring
![Architecture](/flow2.png)


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

Open a second terminal for the video capturing:
```
$ pip install -r example_client/requirements.txt
$ python example_client/client.py
```
Explore all data and RedisGears functions with RedisInsight

https://localhost:8001
