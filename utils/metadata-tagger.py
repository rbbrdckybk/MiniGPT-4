# Copyright 2021 - 2023, Bill Kennedy (https://github.com/rbbrdckybk/MiniGPT-4)
# SPDX-License-Identifier: MIT

# Image Metadata Tagger
# Point this utility at a directory of .jpg images to have MiniGPT-4 write the IPTC metadata for each image!
# Tagged images will be written to a "tagged" sub-folder off of the image directory.

# requires iptcinfo3:
# pip install iptcinfo3

# usage:
# python metadata-tagger.py --imgdir <path containing images>

import argparse
import json
import logging
import minigpt4_client as minigpt4
import shutil
import time
import os
from os.path import exists
from pathlib import Path
from iptcinfo3 import IPTCInfo

logging.getLogger('iptcinfo').setLevel(logging.ERROR)

# write the supplied metadata to the specified filename
# metadata all str except keywords which is []
# pre-existing metadata will be overwritten!
# files will be written to a 'tagged' subdir
def write_iptc_info(filename, title, description, keywords, copyright):
    info = None
    try:
        info = IPTCInfo(filename)
    except:
        pass

    if info != None:
        info['object name'] = title
        info['caption/abstract'] = description
        info['copyright notice'] = copyright
        info['keywords'] = keywords

        dir = os.path.join(os.path.dirname(filename), 'tagged')
        if not os.path.exists(dir):
            Path(dir).mkdir(parents=True, exist_ok=True)

        output_file = os.path.join(dir, os.path.basename(filename))
        info.save_as(output_file)
        if os.path.exists(output_file + '~'):
            try:
                os.remove(output_file + '~')
            except:
                pass
        print('\nWrote metadata to output image (' + output_file + ')...')

# gets .jpg images found within specified dir, ignores subdirs
def get_images_from_dir(dir):
    images = []
    for f in os.scandir(dir):
        if f.path.lower().endswith(".jpg"):
            images.append(f.path)
    images.sort()
    return images

# checks a server response for the success/failure
def response_success(r):
    success = False
    response = json.loads(r)
    if 'success' in response:
        if response['success'] == True:
            success = True
    return success

# grabs the question that was posed to the server in an ask
def question_extract(r):
    resp = ''
    response = json.loads(r)
    if 'message' in response:
        resp = response['message']
    return resp

# grabs the server answer to an ask
def answer_extract(r):
    resp = ''
    response = json.loads(r)
    if 'response' in response:
        resp = response['response']
    return resp

# for logging to console & file
def log(msg):
    print(msg)

# entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--imgdir",
        type=str,
        required=True,
        help="the base directory containing images"
    )
    opt = parser.parse_args()

    if opt.imgdir != '' and exists(opt.imgdir):
        print('\nStarting...')
        count = 0
        images = get_images_from_dir(opt.imgdir)
        print('Found ' + str(len(images)) + ' images in ' + opt.imgdir + '...')
        if len(images) > 0:
            client = minigpt4.MiniGPT4_Client()
            r = client.server_reset()
            if response_success(r):
                # iterate through .jpg images in specified directory
                for img in images:
                    log('\n[' + str(count+1) + '] Now working on ' + img + '...')
                    # send image to MiniGPT-4 server
                    r = client.upload(img)
                    if response_success(r):
                        start_time = time.time()
                        log('Uploaded image (' + img + ') to MiniGPT-4 successfully!')
                        title = ''
                        desc = ''
                        keywords = []

                        # ask questions to generate image metadata
                        r = client.ask('Generate an appropriate short title (just a few words) for this image.')
                        question = question_extract(r)
                        answer = answer_extract(r)
                        log('\nTitle Request >>> ' + question)
                        log('MiniGPT-4 >>> ' + answer)
                        title = answer
                        if (len(answer.split())) > 12:
                            # this is a very long title
                            r = client.ask('Shorten the title so that it is less than 10 words.')
                            question = question_extract(r)
                            answer = answer_extract(r)
                            log('\nTitle Request (shorten length) >>> ' + question)
                            log('MiniGPT-4 >>> ' + answer)
                            title = answer
                        if title.endswith('.'):
                            title = title[:-1]

                        r = client.ask('Write a short description for this image.')
                        question = question_extract(r)
                        answer = answer_extract(r)
                        log('\nDescription Request >>> ' + question)
                        log('MiniGPT-4 >>> ' + answer)
                        description = answer

                        r = client.ask('List at least 10 appropriate keywords for this image, separated by commas.')
                        question = question_extract(r)
                        answer = answer_extract(r)
                        log('\nKeyword Request >>> ' + question)
                        log('MiniGPT-4 >>> ' + answer)
                        if ',' not in answer:
                            log('Error: keyword response does not appear to be in the form of a comma-delimited list!')
                        else:
                            # sanitize & de-dupe keywords
                            keywords = answer.split(',')
                            final_keywords = []
                            for kw in keywords:
                                if kw.endswith('.'):
                                    kw = kw[:-1]
                                kw = kw.strip()
                                final_keywords.append(kw)
                            final_keywords = [*set(final_keywords)]

                        # write metadata to image
                        write_iptc_info(img, title, description, final_keywords, '')

                        exec_time = time.time() - start_time
                        print("finished job #" + str(count+1) + " in " + str(round(exec_time, 2)) + " seconds.")
                    else:
                        log('Error attempting to upload image (' + img + '):')
                        client.debug_response(r)
                    count += 1
            else:
                print('Error attempting to reset MiniGPT-4:')
                client.debug_response(r)

        print('\nDone!')
    else:
        print('Error: specify a valid directory containing images (--imgdir <path>)!')
