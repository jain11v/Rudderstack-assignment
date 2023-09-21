import redis
from env import *
from rq import Queue
from internal.destination.destinationController import startConsuming

# Class to connect with redis server and the redis queue
class RedisForwarder:
    def __init__(self):
        self.channel_name = REDIS_CHANNEL_NAME
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.redis_conn = redis.Redis(host= self.host, port= self.port)
        self.queue = Queue(connection=self.redis_conn)
    
    # Pushes data to redis queue 
    def publishData(self, data):
        try:
            jobId = self.queue.enqueue(startConsuming, data)
            if not jobId:
                return "failed to push the event in the MQ"
            return None
        except Exception as e:
            return str(e)  
    