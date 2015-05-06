# rswt.py
The [RobertSonics WavTrigger](http://robertsonics.com/wav-trigger/) is an audio player for wave files. Audio playback can be controlled through a serial port. 

`rswt.py` is a python library for the WavTrigger that uses the python `serial` library to control the audio player.

The library works on Python 2.7 as well as Python 3.

##Documentation
Documentation for the library is [here]()

[RobertSonics](http://robertsonics.com/) has a [users guide](http://robertsonics.com/wav-trigger-online-user-guide/)for the WavTrigger.

##Install
The `rswt` library consists of just a single file `rwst.py`.
The [PySerial library](http://pyserial.sourceforge.net/) must be installed too. 
The latest official release is always on the [rswt release pages](https://github.com/wayoda/rswt/releases).

Drop the `rswt.py` file into your code folder and start using it

```
import rswt

wt=rswt.WavTrigger('/dev/ttyACM0')
print(wt.version)

```

I will upload the module to [PyPI](https://pypi.python.org/pypi) as soon as I
figure out how to create a valid package.


