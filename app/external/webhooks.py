import json
from flask import Flask, request
import logging
from sys import stdout

app = Flask(__name__)
logger = logging.getLogger('webhooks_logs')
logger.setLevel(logging.INFO) # set logger level

logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

# Webhook destination number 1
@app.route('/webhook1', methods=['POST'])
def webhook1():
    if request.method == 'POST':
        data = request.json
        userId = data['userId']
        payload = data['payload']
        logger.info("Recieved Data in webhook 1: "+json.dumps(data))
        return "Recieved Data in webhook 1: "+ str(userId) + ': ' + str(payload) 

# Webhook destination number 2
@app.route('/webhook2', methods=['POST'])
def webhook2():
    if request.method == 'POST':
        data = request.json
        userId = data['userId']
        payload = data['payload']
        logger.info("Recieved Data in webhook 2: "+json.dumps(data))
        return "Recieved Data in webhook 2: "+ str(userId) + ': ' + str(payload) 

        
app.run(debug= False, host= '0.0.0.0', port= 5000)

