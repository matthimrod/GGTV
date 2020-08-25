#!/usr/bin/python3

import argparse
import http.server
import os
import pychromecast
import random
import socketserver
import threading
import time
import urllib.parse
import socket
from contextlib import closing

def createBaseUrl(ip, port):
    return 'http://' + ip + ':' + str(port) + '/'

def createUrl(baseurl, dirname, video):
    return baseurl + urllib.parse.quote(video[len(dirname):], safe='/')

def findChromecast(receiver):
    print('Searching for chromecast:', receiver)
    services, browser = pychromecast.discovery.discover_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    chromecasts, browser = pychromecast.get_chromecasts()
    cast = None
    print('Found chromecasts:')
    for cc in chromecasts:
        print('  ', cc.device.friendly_name)
        if cc.device.friendly_name == receiver:
            cast = cc
    return cast

def findFreePort():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

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
            ' (', cast.media_controller.status.duration, ' seconds )')
    while(cast.media_controller.is_playing or 
        cast.media_controller.is_paused):
        time.sleep(5)

def startServer(dirname, port):
    os.chdir(dirname)
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(('', port), Handler) as httpd:
        print("Starting HTTP server on port", port)
        httpd.serve_forever()

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

    dirname = args.directory
    receiver = args.receiver

    ip = findHostname()
    port = findFreePort()
    baseurl = createBaseUrl(ip, port)

    daemon = threading.Thread(name='daemon_server', 
                              target=startServer, 
                              daemon=True, 
                              args=(dirname, port))
    daemon.start()

    cast = findChromecast(receiver)
    if cast is not None:
        cast.wait()
        print("Using Chromecast:", cast.device.friendly_name)

        while True:
            listOfFiles = getListOfFiles(dirname)

            if len(listOfFiles) == 0:
                print('No files to stream.')
                break

            for video in listOfFiles:
                print("Starting:", video)
                url = createUrl(baseurl, dirname, video)

                playVideo(cast, url)
    else:
        print('Could not find chromecast', receiver)

if __name__ == '__main__':
    main()
