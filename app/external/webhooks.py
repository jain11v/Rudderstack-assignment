import json
from flask import Flask, request
import logging

app = Flask(__name__)

# Webhook destination number 1
@app.route('/webhook1', methods=['POST'])
def webhook1():
    if request.method == 'POST':
        data = request.json
        userId = data['userId']
        payload = data['payload']
        logging.info("Recieved Data in webhook 1: "+json.dumps(data))
        return "Recieved Data in webhook 1: "+ str(userId) + ': ' + str(payload) 

# Webhook destination number 2
@app.route('/webhook2', methods=['POST'])
def webhook2():
    if request.method == 'POST':
        data = request.json
        userId = data['userId']
        payload = data['payload']
        logging.info("Recieved Data in webhook 2: "+json.dumps(data))
        return "Recieved Data in webhook 2: "+ str(userId) + ': ' + str(payload) 

        
app.run(debug= False, host= '0.0.0.0', port= 5000)

