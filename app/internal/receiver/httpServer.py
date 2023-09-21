import json

from flask import Flask, request

from env import *
from internal.receiver import eventForwarder
from sys import stdout
import logging

app = Flask(__name__)
redisForwarder = eventForwarder.RedisForwarder()

logger = logging.getLogger('gateway_logs')
logger.setLevel(logging.INFO) # set logger level

logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

class HttpResponse:
    def __init__(self):
        self.response = {
            "success" : True,
            "message" : ""
        }
        self.status_code = 200

    def checkValidData(self, data):
        if('userId' in data):               # check for field "userID"
            if('payload' in data):          # check for field "payload"
                pass
            else:
                self.response['message'] = 'payload not present'
                self.response['success'] = False
                self.status_code = 400
        else:
            self.response['message'] = 'userId not present'
            self.response['success'] = False
            self.status_code = 400

    def handlePublishResponse(self, error):
        if not error:                       # if there is no error 
            self.response['success'] = True
            self.response['message'] = "Event published successfully."
        else:                               # if there is some error then error and response 500 is returned
            self.response['success'] = False
            self.response['message'] = "error publishing event: " + error
            self.status_code = 500

@app.route('/publish', methods=['POST'])
def handle_publish():
    if request.method == 'POST':
        res = HttpResponse()
        data = request.json
        logger.info("received HTTP request with event: " + json.dumps(data))
        # check if incoming data is valid
        res.checkValidData(data)
        if(res.response['success']):
            # push data to the redis queue
            redisResponse = redisForwarder.publishData(data = data)
            res.handlePublishResponse(redisResponse)
        logger.info(res.response)
        return res.response, res.status_code
        
class HttpServer:
    def __init__(self):
        self.host = GATEWAY_HOST
        self.port = GATEWAY_PORT
    def start(self):
        # starts flask app which will accept incoming requests and will push event to the redis queue
        app.run(debug= False, host= '0.0.0.0', port= self.port)