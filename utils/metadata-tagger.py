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
    with open('metadata-tagger-log.txt', 'a', encoding = 'utf-8') as f:
        f.write(msg + '\n')

# for sanitizing MiniGPT-4 output
def sanitize_title(title):
    if '"' in title:
        temp = title.split('"', 1)[1]
        if '"' in temp:
            title = temp.split('"', 1)[0]
    if '>' in title:
        temp = title.split('>', 1)[1]
        if '<' in temp:
            title = temp.split('<', 1)[0]
    if title.startswith('Image of a '):
        title = title.replace('Image of a ', '')
    if title.startswith('Title: '):
        title = title.replace('Title: ', '')
    title = title.strip()
    if title.endswith('.'):
        title = title[:-1]
    return title

def sanitize_description(description):
    description = description.strip()
    if description.startswith('"') and description.endswith('"'):
        description = description.replace('"', '')
    description = description.capitalize()

    # remove some common MiniGPT-4 extra wordiness
    if description.startswith('The image shows '):
        description = description.replace('The image shows ', '')
    if description.startswith('The image depicts '):
        description = description.replace('The image depicts ', '')
    if description.startswith('The image is '):
        description = description.replace('The image is ', '')
    if description.startswith('This image shows '):
        description = description.replace('This image shows ', '')
    if description.startswith('This image depicts '):
        description = description.replace('This image depicts ', '')
    if description.startswith('This image is '):
        description = description.replace('This image is ', '')
    if description.startswith('The painting shows '):
        description = description.replace('The painting shows ', '')
    if description.startswith('The painting depicts '):
        description = description.replace('The painting depicts ', '')
    if description.startswith('The painting is '):
        description = description.replace('The painting is ', '')
    if description.startswith('This painting shows '):
        description = description.replace('This painting shows ', '')
    if description.startswith('This painting depicts '):
        description = description.replace('This painting depicts ', '')
    if description.startswith('This painting is '):
        description = description.replace('This painting is ', '')
    if description.startswith('This is an image of '):
        description = description.replace('This is an image of ', '')
    if description.startswith('This is a painting of '):
        description = description.replace('This is a painting of ', '')
    if description.startswith('This image features '):
        description = description.replace('This image features ', '')
    if description.startswith('Description: '):
        description = description.replace('Description: ', '')

    description = description.replace('<img>', '')
    description = description.replace('</img>', '')

    # capitalize every sentence
    sentences = description.split('. ')
    final = ''
    for sentence in sentences:
        final += sentence.capitalize()
        final += '. '
    final = final.strip()
    description = final

    if not description.endswith('.'):
        description += '.'
    else:
        while description.endswith('..'):
            description = description[:-1]

    description = description.capitalize()
    return description

def sanitize_keywords(keywords):
    keywords = answer.split(',')
    final_keywords = []
    for kw in keywords:
        if kw.endswith('.'):
            kw = kw[:-1]

        kw = kw.lower()
        kw = kw.replace('keywords: ', '')
        kw = kw.replace('keyword: ', '')
        kw = kw.replace('keywords', '')
        kw = kw.replace('keyword', '')
        kw = kw.replace('image metadata', '')
        kw = kw.replace('visual elements', '')
        kw = kw.replace('visual pattern', '')
        kw = kw.replace('intricate designs', '')
        kw = kw.replace('no other elements visible', '')
        kw = kw.replace('description', '')
        kw = kw.replace('descriptive words', '')
        kw = kw.replace('descriptive language', '')
        kw = kw.replace('visual interest', '')
        kw = kw.replace('additional information', '')
        kw = kw.replace('visually appealing', '')
        kw = kw.replace('</img>', '')
        kw = kw.replace('<img>', '')

        kw = kw.replace(' appearance', '')
        kw = kw.replace(' element', '')
        kw = kw.replace(' position', '')

        kw = kw.strip()

        if kw == 'image' or kw == 'metadata' or kw == 'appropriate':
            kw = ''

        if kw == 'descriptive' or kw == 'detail':
            kw = ''

        if kw != '':
            final_keywords.append(kw)
    final_keywords = [*set(final_keywords)]
    return final_keywords


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
            # create log file
            f = open('metadata-tagger-log.txt', 'w', encoding = 'utf-8')
            f.close()
            client = minigpt4.MiniGPT4_Client()
            r = client.server_reset()
            if response_success(r):
                initial_direction = 'You are a metadata generation machine designed to help describe images. Your responses will be used verbatim in image metadata and should not be conversational. '
                log('\nNote: The following initial direction is prepended to all server requests to help guide output: ')
                log(initial_direction)
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
                        r = client.ask(initial_direction + 'Generate an appropriate short title (just a few words) for this image. The title should accurately describe the most obvious visual elements of the image in as few words as possible. Avoid esoteric or abstract language.')
                        question = question_extract(r)
                        answer = answer_extract(r)
                        log('\nTitle Request >>> ' + question.replace(initial_direction, ''))
                        log('MiniGPT-4 >>> ' + answer)
                        title = answer
                        if (len(answer.split())) > 12:
                            # this is a very long title
                            r = client.ask('Shorten the title so that it is less than 10 words. Use plain descriptive language.')
                            question = question_extract(r)
                            answer = answer_extract(r)
                            log('\nTitle Request (shorten length) >>> ' + question)
                            log('MiniGPT-4 >>> ' + answer)
                            title = answer
                        title = sanitize_title(title)
                        log('Sanitized Title >>> ' + title)

                        r = client.ask(initial_direction + 'Write a short description (1-2 sentences) for this image. Stick to describing visual elements of the image without making comments about its origin or purpose.')
                        question = question_extract(r)
                        answer = answer_extract(r)
                        log('\nDescription Request >>> ' + question.replace(initial_direction, ''))
                        log('MiniGPT-4 >>> ' + answer)
                        description = sanitize_description(answer)
                        log('Sanitized Description >>> ' + description)
                        description = description.split('. ',)[0]
                        if not description.endswith('.'):
                            description += '.'
                        log('Sanitized Description (1st sentence) >>> ' + description)

                        r = client.ask(initial_direction + 'List at least 10 appropriate keywords for this image, separated by commas.')
                        question = question_extract(r)
                        answer = answer_extract(r)
                        log('\nKeyword Request >>> ' + question.replace(initial_direction, ''))
                        log('MiniGPT-4 >>> ' + answer)
                        if ',' not in answer:
                            r = client.ask('List the keywords on a single line, separated by commas.')
                            question = question_extract(r)
                            answer = answer_extract(r)
                            log('\nKeyword Request (commas) >>> ' + question)
                            log('MiniGPT-4 >>> ' + answer)
                        if ',' not in answer:
                            log('Error: keyword response does not appear to be comma-separated list after two attempts!')
                        else:
                            # sanitize & de-dupe keywords
                            final_keywords = sanitize_keywords(keywords)
                        log('Sanitized Keywords >>> ' + str(final_keywords))

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
