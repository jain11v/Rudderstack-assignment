import unittest
import sys
sys.path.append('../')
from internal.receiver.httpServer import app
from internal.receiver.eventForwarder import RedisForwarder
import json
from unittest.mock import patch
from fakeredis import FakeStrictRedis


class FlaskAPITestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('internal.receiver.eventForwarder.RedisForwarder', FakeStrictRedis())
    def test_correct_input(self):
        data = {
            'userId': 'abc',
            'payload': 'some_payload'
        }
        res = {
            "success": True,
            "message": "Event published successfully."
        }

        response = self.app.post('/publish', json=data)
        if RedisForwarder().publishData(data = data):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.data.decode('utf-8')), res)
        else:
            self.assertEqual(response.status_code, 500)
            

    def test_no_payload(self):
        data = {
            'userId': 'abc'
        }
        res = {
            "success": False,
            "message": 'payload not present'
        }
        response = self.app.post('/publish', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data.decode('utf-8')), res)

    def test_no_userId(self):
        data = {
            'payload': 'some_payload'
        }
        res = {
            "success": False,
            "message": 'userId not present'
        }
        response = self.app.post('/publish', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data.decode('utf-8')), res)

    def test_wrong_endpoint(self):
        data = {
            'userId': 'abc',
            'payload': 'some_payload'
        }
        res = {
            "success": True,
            "message": "Event published successfully."
        }
        response = self.app.post('/wrong', json=data)
        self.assertEqual(response.status_code, 404)

    def test_correct_input_webhook1(self):
        data = {
            'userId': 'abc',
            'payload': 'some_payload'
        }
        res = "Recieved Data in webhook 1: abc: some_payload"
        response = self.app.post('/webhook1', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), res)

    def test_correct_input_webhook2(self):
        data = {
            'userId': 'abc',
            'payload': 'some_payload'
        }
        res = "Recieved Data in webhook 2: abc: some_payload"
        response = self.app.post('/webhook2', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), res)
    
if __name__ == '__main__':
    unittest.main()