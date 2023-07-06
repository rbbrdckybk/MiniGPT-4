# Copyright 2021 - 2023, Bill Kennedy (https://github.com/rbbrdckybk/MiniGPT-4)
# SPDX-License-Identifier: MIT
# adapted from api-client-example.py

import requests
import json
from os.path import exists

class MiniGPT4_Client:
    def __init__(self, debug=False):
        self.url = 'http://localhost:5000'
        self.debug = debug

    # reset the MiniGPT-4 session
    def server_status(self):
        if self.debug:
            print('\nRequesting server status...')
        url = self.url + '/api/v1/status'
        r = requests.request("GET", url)
        return r.text

    # reset the MiniGPT-4 session
    def server_reset(self):
        if self.debug:
            print('\nRequesting server reset...')
        url = self.url + '/api/v1/reset'
        r = requests.request("GET", url)
        return r.text

    # send an image to MiniGPT-4
    # img is the image filename including path
    def upload(self, img):
        if self.debug:
            print('\nUploading image to server (' + img + ')...')
        if exists(img):
            url = self.url + '/api/v1/upload'
            payload = {}
            mime = 'image/jpeg'
            if img.lower().endswith('.png'):
                mime = 'image/png'
            files = [ ('file', (img, open(img,'rb'), mime)) ]
            r = requests.request("POST", url, data=payload, files=files)
            return r.text
        else:
            print('Error: attempt to upload image that does not exist: ' + img)
            return ''

    # ask the MiniGPT-4 server a question
    def ask(self, message):
        if self.debug:
            print('\nSending query to server ("' + message + '")...')
        url = self.url + '/api/v1/ask'
        payload = {"message": message}
        r = requests.request("POST", url, data=payload)
        return r.text

    # tell the MiniGPT-4 server to shut down
    def server_shutdown(self):
        url = self.url + '/api/v1/shutdown'
        r = requests.request("GET", url)
        return r.text

    # r is a reponse from the MiniGPT-4 server
    def debug_response(self, r):
        if r != None and r != '':
            parsed = json.loads(r)
            print('Server response:')
            print(json.dumps(parsed, indent=4))
        else:
            print('Empty response!')
