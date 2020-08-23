#!/usr/bin/python3

import os
import random
import time
import pychromecast

DIRNAME = '/home/matthimrod/GGTV'
RECEIVER = 'ChromecastName'


def getListOfFiles(dirName):
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    return listOfFiles

def main():
#    listOfFiles = getListOfFiles(DIRNAME)
#    random.shuffle(listOfFiles)

#    for elem in listOfFiles:
#        print(elem)

    services, browser = pychromecast.discovery.discover_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Bing-TV"])
    cast = chromecasts[0]
    cast.wait()
    print(cast.device)
    mc = cast.media_controller
    mc.update_status()
    print(cast.media_controller.status)
    

if __name__ == '__main__':
    main()
