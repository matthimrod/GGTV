# GGTV

Reads all of the files in a given directory into a list, randomizes the list, and plays each in an endless loop to the specified Chromecast receiver.

```
usage: ggtv.py [-h] [-d DIRECTORY] -r RECEIVER

optional arguments:
  -h, --help            show this help message and exit
  -r RECEIVER, --receiver RECEIVER
                        Specifies the Chromecast receiver. (required)
  --forever             Continuously loop, re-searching for the Chromecast if it disappears.
```
