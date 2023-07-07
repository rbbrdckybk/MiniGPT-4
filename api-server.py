# Copyright 2021 - 2023, Bill Kennedy (https://github.com/rbbrdckybk/MiniGPT-4)
# SPDX-License-Identifier: MIT

# Simple MiniGPT-4 server
# requires Flask: pip install Flask
# start with: python api-server.py
# see api-client-example.py for client example

import argparse
import os
import random
import json
import signal
import threading
import shutil
from os.path import exists
from pathlib import Path

import numpy as np
import torch
import torch.backends.cudnn as cudnn

from minigpt4.common.config import Config
from minigpt4.common.dist_utils import get_rank
from minigpt4.common.registry import registry
from minigpt4.conversation.conversation import Chat, CONV_VISION

# imports modules for registration
from minigpt4.datasets.builders import *
from minigpt4.models import *
from minigpt4.processors import *
from minigpt4.runners import *
from minigpt4.tasks import *

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename


# MiniGPT-4 basic implementation
class MiniGPT4:
    def __init__(self):
        self.chat = self.init()
        self.chat_state = None
        self.img_list = []
        #self.num_beams = 1
        #self.temperature = 1
        self.busy = False

    # handle optional user-supplied command-line arguments
    def parse_args(self):
        parser = argparse.ArgumentParser(description="Demo")
        parser.add_argument("--cfg-path", default="eval_configs/minigpt4_eval.yaml", help="path to configuration file.")
        parser.add_argument("--gpu-id", type=int, default=0, help="specify the gpu to load the model.")
        parser.add_argument(
            "--options",
            nargs="+",
            help="override some settings in the used config, the key-value pair "
            "in xxx=yyy format will be merged into config file (deprecate), "
            "change to --cfg-options instead.",
        )
        args = parser.parse_args()
        return args

    # load model
    def init(self):
        print('Initializing...')
        args = self.parse_args()
        cfg = Config(args)

        model_config = cfg.model_cfg
        model_config.device_8bit = args.gpu_id
        model_cls = registry.get_model_class(model_config.arch)
        model = model_cls.from_config(model_config).to('cuda:{}'.format(args.gpu_id))

        vis_processor_cfg = cfg.datasets_cfg.cc_sbu_align.vis_processor.train
        vis_processor = registry.get_processor_class(vis_processor_cfg.name).from_config(vis_processor_cfg)
        chat = Chat(model, vis_processor, device='cuda:{}'.format(args.gpu_id))
        print('Initialization Finished')
        return chat

    def reset(self):
        if self.chat_state is not None:
            self.chat_state.messages = []
        self.img_list = []
        print('MiniGPT-4 session has been reset...')

    # send image to MiniGPT-4
    def upload_img(self, img):
        msg = ''
        if exists(img):
            self.chat_state = CONV_VISION.copy()
            self.img_list = []
            msg = self.chat.upload_img(img, self.chat_state, self.img_list)
        else:
            print('Error: upload image (' + img + ') does not exist!')
        return msg

    def ask(self, message):
        if len(message) > 0:
            self.chat.ask(message, self.chat_state)
        else:
            print('Error: call to ask with empty message!')

    def answer(self):
        msg = self.chat.answer(self.chat_state, self.img_list)[0]
        return msg


# used by shutdown handler to kill the server
def kill():
    os.kill(os.getpid(), signal.SIGINT)

# Flask setup
app = Flask('MiniGPT-4')
app.config['UPLOAD_FOLDER'] = 'temp'
# remove old temp images from previous session
if os.path.exists(app.config['UPLOAD_FOLDER']):
    shutil.rmtree(app.config['UPLOAD_FOLDER'])
# create upload dir if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    try:
        Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    except:
        print('Error creating temp directory for images!')
chat = None

# Flask routes & handlers
# get MiniGPT-4's current status
@app.route('/api/v1/status', methods=['GET'])
def status():
    if not chat.busy:
        return jsonify({ "success": True, "message": "MiniGPT-4 is ready for a new request!" })
    else:
        return jsonify({ "success": True, "message": "MiniGPT-4 is currently working on a request!" })

# shutdown MiniGPT-4 server
@app.route('/api/v1/shutdown', methods=['GET'])
def shutdown():
    print('Attempting to shut down...')
    # call kill fuction in 0.5 secs
    threading.Timer(0.5, kill).start()
    return jsonify({ "success": True, "message": "Attempting to shut down MiniGPT-4 server..." })

# reset MiniGPT-4 session
@app.route('/api/v1/reset', methods=['GET'])
def reset():
    chat.reset()
    return jsonify({ "success": True, "message": "MiniGPT-4 session has been reset..." })

# upload an image to MiniGPT-4
@app.route('/api/v1/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print('Error: upload attempt with no file found in POST request!')
        return jsonify({ "success": False, "message": "No file found in POST request..." })
    else:
        file = request.files['file']
        if file.filename == '':
            print('Error: upload attempt with empty file found in POST request!')
            return jsonify({ "success": False, "message": "Empty file found in POST request..." })
        else:

            filename = secure_filename(os.path.basename(file.filename))
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path)
            msg = chat.upload_img(full_path)
            if 'received' in msg.lower():
                return jsonify({ "success": True, "message": "Image received!" })
            else:
                return jsonify({ "success": False, "message": msg })

# ask MiniGPT-4 about the current image
@app.route('/api/v1/ask', methods=['POST'])
def ask():
    if not chat.busy:
        msg = request.form['message']
        if msg != None and msg != '':
            chat.busy = True
            chat.ask(msg)
            r = chat.answer()
            chat.busy = False
            return jsonify({ "success": True, "message": msg, "response": r })
        else:
            return jsonify({ "success": False, "message": "No message in POST request!" })
    else:
        return jsonify({ "success": False, "message": "MiniGPT-4 is currently working on another request!" })


# entry point
if __name__ == '__main__':
    chat = MiniGPT4()
    app.run()
