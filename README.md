# FraudDetectionDemo

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
