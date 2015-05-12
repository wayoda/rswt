# rswt.py

The [RobertSonics WavTrigger](http://robertsonics.com/wav-trigger/) is an audio
player for wave files. Audio playback can be controlled through a serial port. 

`rswt.py` is a python library for the WavTrigger that uses the python `serial`
library to control the audio player.

The library works on Python 2.7 as well as Python 3.

##Documentation

Documentation for the library is [here](http://wayoda.github.io/rswt/)

[RobertSonics](http://robertsonics.com/) published a [users
guide](http://robertsonics.com/wav-trigger-online-user-guide/) for the
WavTrigger.

##Install from PyPI

`pip install rswt`

or 

`pip3 install rswt`


##Install from github

The `rswt` library consists of just a single file `rwst.py`.  The [PySerial
library](http://pyserial.sourceforge.net/) must be installed too.  The latest
official release is always on the [rswt release
pages](https://github.com/wayoda/rswt/releases).

##Run 

Drop the `rswt.py` file into your code folder and start using it

```
>>>import rswt 
>>>wt=rswt.WavTrigger('/dev/UsbSerial') 
>>>wt.version
'WAV Trigger v1.10'
>>> wt.close()
``` 

