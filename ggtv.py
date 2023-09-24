#!/usr/bin/python3

import argparse
import json
import logging
import os
import posixpath

import pychromecast
import re
import requests
import sys
import time
import datetime

from pychromecast import Chromecast


def find_chromecast(device_name: str) -> Chromecast:
    logger = logging.getLogger(__name__)
    cast = None

    while not cast:
        logger.info('Searching for chromecast: %s', device_name)
        devices, _ = pychromecast.get_listed_chromecasts(friendly_names=[device_name])
        if devices and len(devices) == 1:
            logger.info('Found device Name: %s', devices[0].cast_info.friendly_name)
            logger.info('Found device Model: %s %s',
                        devices[0].cast_info.manufacturer, devices[0].cast_info.model_name)
            logger.info('Found device Host: %s', devices[0].cast_info.host)
            logger.info('Found device UUID: %s', devices[0].cast_info.uuid)
            cast = devices[0]

    # Start socket client's worker thread and wait for initial status update
    cast.wait()
    return cast


def get_list_of_files(base_url: str) -> list[str]:
    logger = logging.getLogger(__name__)
    logger.info('Building URL list: %s', base_url)
    links = []

    result = requests.head(base_url)
    if result.ok and result.headers.get('Content-Type') != 'text/html':
        return [base_url]

    result = requests.get(base_url)
    if result.ok:
        for line in result.text.splitlines():
            match = re.search('href="([^"]*)"', line)
            if match and match.group(1) != '../':
                for link in get_list_of_files(posixpath.join(base_url, match.group(1))):
                    links.append(link)
        return links
    logger.error('Unable to build playlist.')
    raise RuntimeError('Unable to build playlist.')


def play_video(cast: Chromecast, url: str) -> None:
    logger = logging.getLogger(__name__)
    time.sleep(2)

    logger.info("Sending URL: %s", url)
    cast.media_controller.play_media(url, 'video/mp4')
    time.sleep(10)

    cast.media_controller.block_until_active(15)
    cast.media_controller.update_status()
    logger.info('Playing %s (%s)',
                cast.media_controller.status.content_id,
                str(datetime.timedelta(seconds=cast.media_controller.status.duration)))
    while cast.media_controller.is_playing or cast.media_controller.is_paused:
        time.sleep(15)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        help='Specifies the config.json file.',
                        required=False,
                        default=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                                             'ggtv.json'))
    parser.add_argument('-r', '--receiver',
                        help='Specifies the Chromecast receiver. (required)',
                        required=True)
    args = parser.parse_args()

    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.name = 'GGTV'

    console_log_handler = logging.StreamHandler()
    console_log_handler.setLevel(logging.INFO)
    console_log_handler.setFormatter(log_formatter)
    logger.addHandler(console_log_handler)

    log_file_handler = logging.FileHandler(
        os.path.join(os.path.dirname(
            os.path.abspath(sys.argv[0])), 'ggtv.log'), encoding='utf-8')
    log_file_handler.setLevel(logging.INFO)
    log_file_handler.setFormatter(log_formatter)
    logger.addHandler(log_file_handler)
    logger.info('Starting.')

    receiver = args.receiver
    with open(args.config, 'r') as config_file:
        config = json.load(config_file)

    while True:
        cast = find_chromecast(receiver)

        logger.info("Using Chromecast: %s (%s %s/%s)", cast.cast_info.friendly_name,
                    cast.cast_info.manufacturer, cast.cast_info.model_name, cast.cast_info.host)
        while True:
            logger.info("Creating video list.")
            list_of_files = get_list_of_files(config.get('base_url', 'http://172.16.1.35:5080'))

            if not list_of_files:
                logger.info('No files to stream.')
                break

            for video in list_of_files:
                logger.info("Starting: %s", video)
                play_video(cast, video)

        time.sleep(30)


if __name__ == '__main__':
    main()
