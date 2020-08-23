#!/usr/bin/python3

import http.server
import mimetypes
import os
import pychromecast
import random
import socketserver
import threading
import time
import urllib.parse

DIRNAME = '/home/matthimrod/GGTV/'
BASEURL = 'http://192.168.86.45:8000/'
PORT = 8000
RECEIVER = 'Bing-TV'


def getListOfFiles(dirName):
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    return listOfFiles

def start_server():
    os.chdir(DIRNAME)
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

def main():
    listOfFiles = getListOfFiles(DIRNAME)
    random.shuffle(listOfFiles)

    daemon = threading.Thread(name='daemon_server',
                              target=start_server,
                              daemon=True,
                              args=())
    daemon.start()

    services, browser = pychromecast.discovery.discover_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[RECEIVER])
    cast = chromecasts[0]
    cast.wait()
    print("Using Chromecast:")
    print(cast.device)

    for elem in listOfFiles:
        print("Starting file:", elem)
        mime = mimetypes.guess_type(elem)
        mime = "video/mp4"
        url = BASEURL + urllib.parse.quote(elem[len(DIRNAME):], safe='/')
        print("Sending URL:", url)

        time.sleep(1)
        cast.media_controller.play_media(url , mime)
        time.sleep(5)
        cast.media_controller.update_status()
#        cast.media_controller.block_until_active()
        print(cast.media_controller.status)
        while(cast.media_controller.is_playing or cast.media_controller.is_paused):
            time.sleep(15)
    

if __name__ == '__main__':
    main()
