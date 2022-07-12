#!/usr/bin/python3

import argparse
import os
import pychromecast
import random
import time
import urllib.parse
import datetime

def createBaseUrl(ip, port):
    return 'http://' + ip + ':' + str(port) + '/'

def createUrl(baseurl, dirname, video):
    return baseurl + urllib.parse.quote(video[len(dirname):], safe='/')

def findChromecast(receiver):
    cast = None
    
    while cast == None:
        print('Searching for chromecast:', receiver)
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[receiver])
        if not chromecasts or len(chromecasts) != 1:
            print(f'No chromecast with name "{receiver}" discovered')

        cast = chromecasts[0]

    # Start socket client's worker thread and wait for initial status update
    cast.wait()
    return cast

def findHostname():
    return os.popen("hostname -I | cut -d' ' -f1").read().strip()

def getListOfFiles(dirname):
    print('Gathering list of files...', end =' ')

    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(dirname):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    random.shuffle(listOfFiles)

    print('found', len(listOfFiles), 'files.')

    return listOfFiles

def playVideo(cast, url):
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
    parser.add_argument('-d', '--directory', 
                        help='''Specifies the directory to stream.
                        Default is the current directory.''', 
                        default='.')
    parser.add_argument('-r', '--receiver', 
                        help='Specifies the Chromecast receiver. (required)', 
                        required=True)
    args = parser.parse_args()

    dirname = os.path.join(args.directory, '')
    receiver = args.receiver

    ip = findHostname()
    port = 5080
    baseurl = createBaseUrl(ip, port)

   
    while True:
        cast = findChromecast(receiver)

        print("Using Chromecast:", cast.name)

        while True:
            listOfFiles = getListOfFiles(dirname)

            if len(listOfFiles) == 0:
                print('No files to stream.')
                break

            for video in listOfFiles:
                print("\n\nStarting:", video, "\n")
                url = createUrl(baseurl, dirname, video)

                try:
                    playVideo(cast, url)
                except:
                    print("\n\nReconnecting.")
                    cast = findChromecast(receiver)
                    cast.wait()
                    
        time.sleep(30)


if __name__ == '__main__':
    main()
