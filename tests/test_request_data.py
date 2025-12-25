# Usage:
# python3 -m unittest -v test_request_data.py

import json
import unittest
import os
import sys

# Set the Python search path...
CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.request_data import RequestData, RequestMessage

class RequestDataTest(unittest.TestCase):

    def test_from_dict(self):
        data = {
            'positions': [0, 1],
            'messages': [{ 'role': 'system', 'content': 'p1' },
                         { 'role': 'user',   'content': 'p2' }]
        }
        request_data = RequestData.from_dict(data)
        self.assertEqual(request_data.positions, data['positions'])
        for i in range(len(request_data.messages)):
            assert isinstance(request_data.messages[i], RequestMessage)
            self.assertEqual(request_data.messages[i].role, data['messages'][i]['role'])
            self.assertEqual(request_data.messages[i].content, data['messages'][i]['content'])

    def test_from_json(self):
        data = {
            'positions': [0, 1],
            'messages': [{ 'role': 'system', 'content': 'p1' },
                         { 'role': 'user',   'content': 'p2' }]
        }
        json_data = json.dumps(data)
        request_data = RequestData.from_json(json_data)
        self.assertEqual(request_data.positions, data['positions'])
        for i in range(len(request_data.messages)):
            assert isinstance(request_data.messages[i], RequestMessage)
            self.assertEqual(request_data.messages[i].role, data['messages'][i]['role'])
            self.assertEqual(request_data.messages[i].content, data['messages'][i]['content'])

    def test_to_dict(self):
        data = {
            'positions': [0, 1],
            'messages': [{ 'role': 'system', 'content': 'p1' },
                         { 'role': 'user',   'content': 'p2' }]
        }
        request_data = RequestData.from_dict(data)
        request_dict = request_data.to_dict()
        self.assertDictEqual(request_dict, data)


if __name__ == '__main__':
    unittest.main()
