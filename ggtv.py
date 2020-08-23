#!/usr/bin/python3

import http.server
import os
import pychromecast
import random
import socketserver
import threading
import time
import urllib.parse

DIRNAME = '/home/matthimrod/GGTV/'
PORT = 8000
RECEIVER = 'Outside TV'

ip = os.popen("hostname -I | cut -d' ' -f1").read().strip()

BASEURL = 'http://' + ip + ':' + str(PORT) + '/'

def getListOfFiles(dirName):
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    return listOfFiles

def start_server():
    os.chdir(DIRNAME)
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Starting HTTP server on port", PORT)
        httpd.serve_forever()

def main():
    print("Gathering list of files.")
    listOfFiles = getListOfFiles(DIRNAME)
    print("Found ", len(listOfFiles), " files.")
    random.shuffle(listOfFiles)

    print("Base URL: ", BASEURL)

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
    print("Using Chromecast:", cast.device.friendly_name)

    for elem in listOfFiles:
        time.sleep(2)

        print("Starting file:", elem)
        url = BASEURL + urllib.parse.quote(elem[len(DIRNAME):], safe='/')

        print("Sending URL:", url)
        cast.media_controller.play_media(url, 'video/mp4')

        time.sleep(10)

        cast.media_controller.block_until_active(15)
        cast.media_controller.update_status()
        print('Playing ', cast.media_controller.status.content_id,
                  ' (', cast.media_controller.status.duration, ')')
        while(cast.media_controller.is_playing or 
              cast.media_controller.is_paused):
            time.sleep(5)
    

if __name__ == '__main__':
    main()
