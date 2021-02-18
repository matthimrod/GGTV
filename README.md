# GGTV

Reads all of the files in a given directory into a list, randomizes the list, and plays each in an endless loop to the specified Chromecast receiver.

```
usage: ggtv.py [-h] [-d DIRECTORY] -r RECEIVER

optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Specifies the directory to stream. Default is the current directory.
  -r RECEIVER, --receiver RECEIVER
                        Specifies the Chromecast receiver. (required)
  --forever             Continuously loop, re-searching for the Chromecast if it disappears.
```

# Docker Build

Build the image with the following command:
```
docker build . -t ggtv
```

Start the image with the following command:
```
docker run --name ggtv --mount type=bind,source=<media_directory>,target=/media,readonly --network host ggtv
```

Outstanding issue:
* The script running in Docker is unable to find the receiver.
* The moount for media does not seem to work.