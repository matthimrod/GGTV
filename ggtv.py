#!/usr/bin/python3

import argparse
import datetime
import os
import pidfile
import pychromecast
import random
import re
import requests
import time

def create_base_url(ip, port):
    return 'http://' + ip + ':' + str(port) + '/'

def find_chromecast(receiver):
    cast = None
    
    while cast == None:
        print('Searching for chromecast:', receiver)
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[receiver])
        if not chromecasts or len(chromecasts) != 1:
            print(f'No chromecast with name "{receiver}" discovered')
        else:
            cast = chromecasts[0]

    # Start socket client's worker thread and wait for initial status update
    cast.wait()
    return cast

def get_hostname():
    return os.popen("hostname -I | cut -d' ' -f1").read().strip()

def get_list_of_files(base_url):
    links = [ ]
    
    result = requests.head(base_url)
    
    if result.status_code == 200 and (result.headers.get('Content-Type') == 'text/html'):
        result = requests.get(base_url)
        
        if result.status_code == 200:
            for line in result.text.splitlines():
                match = re.search('href="([^"]*)"', line)
                if match and match.group(1) != '../':
                    for link in get_list_of_files(base_url + match.group(1)):
                        links.append( link )
            return links
    else:
        return [ base_url ]

def play_video(cast, url):
    time.sleep(2)

    print("Sending URL:", url)
    cast.media_controller.play_media(url, 'video/mp4')
    time.sleep(10)

    cast.media_controller.block_until_active(15)
    cast.media_controller.update_status()
    print('Playing', cast.media_controller.status.content_id,
            ' (', str(datetime.timedelta(seconds=cast.media_controller.status.duration)), ')')
    while(cast.media_controller.is_playing or 
        cast.media_controller.is_paused):
        time.sleep(15)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--receiver', 
                        help='Specifies the Chromecast receiver. (required)', 
                        required=True)
    args = parser.parse_args()

    receiver = args.receiver

    ip = get_hostname()
    port = 5080
    baseurl = create_base_url(ip, port)

   
    while True:
        cast = find_chromecast(receiver)

        print("Using Chromecast:", cast.name)

        while True:
            print("Creating video list.")
            list_of_files = get_list_of_files(baseurl)
            random.shuffle(list_of_files)

            if len(list_of_files) == 0:
                print('No files to stream.')
                break

            for video in list_of_files:
                print("\n\nStarting:", video)

                try:
                    play_video(cast, video)
                except:
                    print("\n\nReconnecting.")
                    cast = find_chromecast(receiver)
                    cast.wait()
                    
        time.sleep(30)


if __name__ == '__main__':
    try:
        pid_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.pid')
        with pidfile.PIDFile(pid_file):
            main()
    except pidfile.AlreadyRunningError:
        print("GGTV is already running. :)")

