import threading
import time

import pymongo
import redis
import requests
import logging
import json
from sys import stdout
from env import *
from rq import Connection, Queue, Worker



logger = logging.getLogger('router_logs')
logger.setLevel(logging.INFO) # set logger level

logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

# Class to connect with redis server and the redis queue
class RedisClient:
    def __init__(self):
        self.channel_name = REDIS_CHANNEL_NAME
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.redis_conn = redis.Redis(host= self.host, port= self.port)
        self.queue = Queue(connection=self.redis_conn)

redis_cli = RedisClient()

# MongoDB client ## This has a collection "events" which stores the event payload
myclient = pymongo.MongoClient(f'mongodb://{MONGO_HOST}:27017')
mydb = myclient["rudderData"]
mycol = mydb["events"]

# Destination type 2 - Call to webhook 
def sendDataWebhook(url, data, delay = 2):          # delay inc exponentially and is limited to 30 (no. of tries = 4)
    if(delay > 30):
        logger.error("error sending data to: " + url + " with data: " + json.dumps(data))
    try:
        logger.info("Making call to webhook: " + url + " with data: " + json.dumps(data))
        requests.post(url=url, json=data)
        logger.info("Successfully called webhook: " + url + " with data: " + json.dumps(data))
    except:
        # sleep and then retry
        time.sleep(delay)
        delay = delay + delay
        sendDataWebhook(url, data, delay)

# Destination type 1 - MongoDB (stores the incoming payload and userID)
def addDataToDB(data, delay = 2):          # delay inc exponentially and is limited to 30 (no. of tries = 4)
    if(delay > 30):
        logger.error("error adding data to DB: " + json.dumps(data))
    try:
        logger.info("request to add data to db: " + json.dumps(data))
        mycol.insert_one({"userId": str(data['userId']), "payload": data['payload']})
        logger.info("inserted to db: " + json.dumps(data))
    except:
        # sleep and then retry
        time.sleep(delay)
        delay = delay + delay
        addDataToDB(data, delay)

# Listen for messages
def startConsuming(json_data):
    webhook1 = threading.Thread(target = sendDataWebhook, args = ['http://' + WEBHOOK_HOST + ':' + WEBHOOK_PORT + '/webhook1', json_data])
    webhook2 = threading.Thread(target = sendDataWebhook, args = ['http://' + WEBHOOK_HOST + ':' + WEBHOOK_PORT + '/webhook2', json_data])
    mongodb = threading.Thread(target = addDataToDB, args = [json_data])
    webhook1.start()
    webhook2.start()
    mongodb.start()
    webhook1.join()
    webhook2.join()
    mongodb.join()


def start_dequeue():
    with Connection(redis_cli.redis_conn):
        worker = Worker([redis_cli.queue])          # Redis worker that listens to new messages in queue (FIFO)
        worker.work()                               # executes the event handler
        

