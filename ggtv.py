#!/usr/bin/python3

import argparse
import json
import os
import pychromecast
import re
import requests
import sys
import time
import datetime


def findChromecast(receiver):
    cast = None

    while cast == None:
        print('Searching for chromecast:', receiver)
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[
                                                                   receiver])
        if not chromecasts or len(chromecasts) != 1:
            print(f'No chromecast with name "{receiver}" discovered')
        else:
            cast = chromecasts[0]

    # Start socket client's worker thread and wait for initial status update
    cast.wait()
    return cast


def getListOfFiles(base_url):
    links = []

    result = requests.head(base_url)

    if result.status_code == 200 and (result.headers.get('Content-Type') == 'text/html'):
        result = requests.get(base_url)

        if result.status_code == 200:
            for line in result.text.splitlines():
                match = re.search('href="([^"]*)"', line)
                if match and match.group(1) != '../':
                    for link in getListOfFiles(base_url + match.group(1)):
                        links.append(link)
            return links
    else:
        return [base_url]


def playVideo(cast, url):
    time.sleep(2)

    print("Sending URL:", url)
    cast.media_controller.play_media(url, 'video/mp4')
    time.sleep(10)

    cast.media_controller.block_until_active(15)
    cast.media_controller.update_status()
    print('Playing', cast.media_controller.status.content_id,
          ' (', str(datetime.timedelta(seconds=cast.media_controller.status.duration)), ')')
    while (cast.media_controller.is_playing or
           cast.media_controller.is_paused):
        time.sleep(15)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        help='Specifies the config.json file.',
                        required=False,
                        default=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                                             'config.json'))
    parser.add_argument('-r', '--receiver',
                        help='Specifies the Chromecast receiver. (required)',
                        required=True)
    args = parser.parse_args()

    receiver = args.receiver

    with open(args.config, 'r') as config_file:
        config = json.load(config_file)


    while True:
        cast = findChromecast(receiver)

        print("Using Chromecast:", cast.name)

        while True:
            print("Creating video list.")
            listOfFiles = getListOfFiles(config.get('base_url', 'http://172.16.1.35:5080'))

            if len(listOfFiles) == 0:
                print('No files to stream.')
                break

            for video in listOfFiles:
                print("\n\nStarting:", video)

                try:
                    playVideo(cast, video)
                except:
                    print("\n\nReconnecting.")
                    cast = findChromecast(receiver)
                    cast.wait()

        time.sleep(30)


if __name__ == '__main__':
    main()
