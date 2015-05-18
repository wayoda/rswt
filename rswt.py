"""A library to control a RobertSonics WavTrigger through a serial port
"""

from __future__ import absolute_import, division, print_function

from os import errno
import serial
import struct

__version__ = '0.1.1'
__author__ = 'Eberhard Fahle'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Eberhard Fahle'

#Constants for the commands a wavtrigger understands

# Reading data back from a WavTrigger
# Firmware version
_WT_GET_VERSION = bytearray([0xF0,0xAA,0x05,0x01,0x55])
# Number of polyphonic voices and number of tracks on sd-card
_WT_GET_SYS_INFO =  bytearray([0xF0,0xAA,0x05,0x02,0x55])

# List of currently playing tracks
_WT_GET_STATUS =  bytearray([0xF0,0xAA,0x05,0x07,0x55])
# Timeout when waiting for the data from the Get-Status command
_WT_GET_STATUS_TIMEOUT = 0.25

# Playing individual tracks
_WT_TRACK_SOLO = bytearray([0xF0,0xAA,0x08,0x03,0x00,0x00,0x00,0x55])
_WT_TRACK_PLAY = bytearray([0xF0,0xAA,0x08,0x03,0x01,0x00,0x00,0x55])
_WT_TRACK_PAUSE = bytearray([0xF0,0xAA,0x08,0x03,0x02,0x00,0x00,0x55])
_WT_TRACK_RESUME = bytearray([0xF0,0xAA,0x08,0x03,0x03,0x00,0x00,0x55])
_WT_TRACK_STOP = bytearray([0xF0,0xAA,0x08,0x03,0x04,0x00,0x00,0x55])
_WT_TRACK_LOOP_ON = bytearray([0xF0,0xAA,0x08,0x03,0x05,0x00,0x00,0x55])
_WT_TRACK_LOOP_OFF = bytearray([0xF0,0xAA,0x08,0x03,0x06,0x00,0x00,0x55])
_WT_TRACK_LOAD = bytearray([0xF0,0xAA,0x08,0x03,0x07,0x00,0x00,0x55])

# Stopping and resuming several tracks at once
_WT_STOP_ALL = bytearray([0xF0,0xAA,0x05,0x04,0x55])
_WT_RESUME_ALL = bytearray([0xF0,0xAA,0x05,0x0B,0x55])

# Mixer settings and fader
_WT_VOLUME = bytearray([0xF0,0xAA,0x07,0x05,0x00,0x00,0x55])
_WT_TRACK_VOLUME = bytearray([0xF0,0xAA,0x09,0x08,0x00,0x00,0x00,0x00,0x55])
_WT_FADE = bytearray([0xF0,0xAA,0x0C,0x0A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x55])

# Pitch bending
_WT_SAMPLERATE = bytearray([0xF0,0xAA,0x07,0x0C,0x00,0x00,0x55])

# Switching the Power amp on or off (not implemented!)
_WT_AMP_POWER = bytearray([0xF0,0xAA,0x06,0x09,0x00,0x55])

class WavTrigger(object):
    """A controller for a RobertSonics WavTrigger
    """

    def __init__(self,device, baud=57600, timeout=5.0):
        """Open a serial port to the device and read the 
        hardware version and info from the WavTrigger.

        :param device: The serial port where the WavTrigger is listening.
        :type device: str
        :param baud: The baudrate to be used on the port. The value must match
        the baudrate set in the init file of the WavTrigger. The default 
        value (57600) seems to be fast enough for all purposes
        :type baud: int
        :param timeout: A timeout for reading and writing on the port. 
        The default (5.0 seconds) is plenty. If this limit is reached
        you can be quite sure to have lost the connection.
        :type timeout: float

        """
        self._wt=serial.Serial(port=device, baudrate=baud)
        self._wt.timeout=timeout
        if self._wt.isOpen():
            self._version=self._getVersion()
            self._voices,self._tracks=self._getSysInfo()

    def close(self):
        """Closes the port to the WavTrigger. Does not stop playing tracks.

        """
        self._wt.close()

    def isOpen(self):
        """Test if a serial connection to the WavTrigger is established.

        :returns: bool -- True if the device is open, False otherwise

        """
        return self._wt.isOpen()

    @property
    def version(self):
        """Get the version string of the WavTrigger firmeware

        :returns: str -- A string with the firmware version that runs on the WavTrigger

        """
        return self._version

    @property
    def voices(self):
        """Get the number of polyphonic voices the WavTrigger can play simultanously. 

        :returns: int -- The number of voices that can be played simultanously

        """
        return self._voices

    @property
    def tracks(self):
        """Get the number of tracks stored on SD-Card of the WavTrigger.

        :returns: int -- The total number of tracks the WavTrigger found on the SD-Card.

        """
        return self._tracks

    def play(self,track):
        """Play a track

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int

        """
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_PLAY,track)
            self._wt.write(t)

    def solo(self,track):
        """Play a track solo. Stops all currently playing tracks
        and starts the solo track.

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int

        """
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_SOLO,track)
            self._wt.write(t)

    def stop(self,track):        
        """Stop a playing track.

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int

        """
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_STOP,track)
            self._wt.write(t)

    def pause(self,track):
        """Pause a track. Stops a playing track until 
        'resume' is called for the track.

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int

        """
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_PAUSE,track)
            self._wt.write(t)

    def resume(self,track):        
        """Resume playing a track that has been paused previously.

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int

        """
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_RESUME,track)
            self._wt.write(t)

    def load(self,track):        
        """Load a track into the memory of the WavTrigger and pause it.
        The track can than be played using the :meth:`resume` or :meth:`resumeAll` commands

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int

        """
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_LOAD,track)
            self._wt.write(t)

    def loop(self,track):        
        """Set loop flag for a track. When the track is started it is played 
        in a loop until it is stopped. But stopping it does not clear the loop flag.
        If the track is started again, it will still loop. Use :meth:`unLoop` to clear
        the loop flag

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int

        """
        if self._isValidTrackNumber(track):
            self._wt.write(self._setTrackForCommand(_WT_TRACK_LOOP_ON,track))


    def unLoop(self,track):        
        """Clear the loop flag for a track. see :meth:`loop`

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int

        """

        if self._isValidTrackNumber(track):
            self._wt.write(self._setTrackForCommand(_WT_TRACK_LOOP_OFF,track))

    def stopAll(self):        
        """Stop all playing tracks.

        """

        self._wt.write(_WT_STOP_ALL)

    def resumeAll(self):        
        """Restart all resumed tracks. 

        """
        self._wt.write(_WT_RESUME_ALL)

    def masterGain(self,gain):
        """
        Sets the gain for the WavTrigger output.

        :param gain: Gain for the WavTrigger output.
        The valid range for the gain argument is -70..+10  
        :type gain: int

        """
        if gain<-70 or gain>10:
            raise ValueError('Gain argument range is from -70 to +10') 
        g=_WT_VOLUME
        g[4],g[5]=self._intToLsb(gain)
        self._wt.write(g)

    def trackGain(self, track, gain):
        """ Set the gain for a specific track.

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int                      
        :param gain: Gain for the WavTrigger output.
        The valid range for the gain argument is -70..+10  
        :type gain: int

        """
        if gain<-70 or gain>10:
            raise ValueError('Gain argument range is from -70 to +10') 
        g=_WT_TRACK_VOLUME
        g[4],g[5]=self._intToLsb(track)
        g[6],g[7]=self._intToLsb(gain)
        self._wt.write(g)

    def masterVolume(self,volume):
        """Set the volume for the WavTrigger output. This method never
        amplifies the signal as the :meth:`masterGain` does when called
        with gain values > 0. This prevents distorsion in the output signal.
        Also most people are used to volume ranges from zero to 100 rather then 
        a gain value in dB.

        :param volume: Volume for the WavTrigger output.
        The valid range for the volume argument is 0..100  
        :type gain: int

        """
        vol=_WT_VOLUME
        vol[4],vol[5]=self._intToLsb(self._volumeToDb(volume))
        self._wt.write(vol)

    def trackVolume(self,track,volume):        
        """Set the volume for a track. This method never
        amplifies the track signal as the :meth:`trackGain` does when called
        with gain values > 0. This prevents distorsion in the output signal.
        Also most people are used to volume ranges from zero to 100 rather then 
        a gain value in dB.

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int                      
        :param volume: Volume for the track.
        The valid range for the volume argument is 0..100  
        :type gain: int

        """
        tvol=_WT_TRACK_VOLUME
        tvol[4],tvol[5]=self._intToLsb(track)
        tvol[6],tvol[7]=self._intToLsb(self._volumeToDb(volume))
        self._wt.write(tvol)

    def pitch(self,offset):
        """Set an offset for the samplerate that the WavTrigger uses. 
        A negative offset lowers the tone, a positive offset raises the tone
        value.

        :param offset: Offset to the samplerate. 
        The range of valid offset agrument values is -32767..+32767
        :type offset: int                      

        """
        if offset>32767 :
            offset=32767
        if offset < -32767:
            ofset = -32767
        pitch=_WT_SAMPLERATE
        pitch[4],pitch[5]=self._intToLsb(offset)
        self._wt.write(pitch)

    def fade(self,track,volume,time):
        """Fade the track volume from the current volume level to 
        a lower or higer volume

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int                      
        :param volume: The target volume for the track.
        The valid range for the volume argument is 0..100  
        :type volume: int
        :param time: The time in milliseconds for the fade from the current
        to the target level
        :type time: int                     

        """
        f=_WT_FADE
        f[4],f[5]=self._intToLsb(track)
        f[6],f[7]=self._intToLsb(self._volumeToDb(volume))
        f[8],f[9]=self._intToLsb(time)
        f[10]=0x00
        self._wt.write(f) 

    def fadeOut(self,track, time):        
        """Fade the track volume from the current volume level to zero,
        than stop the track.

        :param track: Number of the track. 
        The range of valid tracknumbers is 1..999
        :type track: int                      
        :param time: The time in milliseconds for the fade out from the current
        to silence
        :type time: int                     

        """
        f=_WT_FADE
        f[4],f[5]=self._intToLsb(track)
        f[6],f[7]=self._intToLsb(self._volumeToDb(0))
        f[8],f[9]=self._intToLsb(time)
        f[10]=0x01
        self._wt.write(f) 

    def playing(self):
        """ 
        Get a list of the currently playing tracks on the WavTrigger.

        :returns: list -- A list with the track numbers currently playing.
        If no tracks are playing the empty list is returned.
        If there is a problem reading the return value from the 
        WavTrigger `None` is returned.

        """
        self._wt.write(_WT_GET_STATUS)
        header=self._readFromPort(4)
        if header[:2]!=b'\xF0\xAA' or header[3:4]!=b'\x83':
            self._wt.flushInput()
            return None
        trackLen=ord(header[2:3])-4
        t=self._readFromPort(trackLen)
        if t[-1:]!=b'\x55':
            return None
        t=t[:-1]
        tracks=[t[i:i+2] for i  in range(0, len(t), 2)]
        trackList=[]
        for i in range(len(tracks)):
            trackList.append(self._lsbToInt(tracks[i]))
        return trackList 

    def _isValidTrackNumber(self,track):
        """Simple test for valid track numbers
        """
        if track>0:
            return True
        return False

    def _lsbToInt(self,lsbValue):
        """Convert track number from 2 bytes in lsb order to an int value
        """
        return struct.unpack('<h',lsbValue)[0]

    def _intToLsb(self,value):
        """Convert an int value to a 2 byte tuple in lsb order
        """
        return (value & 0xFF, (value >> 8) & 0xFF)

    def _setTrackForCommand(self,cmd,track):
        """All track commands need a track argument in the data sent
        to the WavTrigger. We update the command data array in place
        """
        cmd[5],cmd[6]=self._intToLsb(track)
        return cmd

    def _volumeToDb(self, vol):
        """Map a volume level of 0..100 to the gain level of -70..0 db
        which is used by the WavTrigger

        """
        if vol<0 or vol>100:
            raise ValueError('Volume argument range is from 0 to 100')
        return -70+int(vol/1.428)

    def _getVersion(self):
        """Read version number from device
        """
        if(self._wt.write(_WT_GET_VERSION) != len(_WT_GET_VERSION)):
            return ''
        v=self._readFromPort(25)
        if(v[:4]!=b'\xF0\xAA\x19\x81' or v[-1:]!=b'\x55'):
            return ''
        vstr=v[4:-1].decode('utf8')
        return vstr.strip()

    def _getSysInfo(self):
        """Read system info from device. The current firmware reports 
        the number of polyphonic voice and the number of tracks found on the SD-card.
        """
        if(self._wt.write(_WT_GET_SYS_INFO) != len(_WT_GET_SYS_INFO)):
            return (0,0)
        v=self._readFromPort(8)
        if(v[:4]!=b'\xF0\xAA\x08\x82' or v[-1:]!=b'\x55'):
            return (0,0)
        return (ord(v[4:5]),self._lsbToInt(v[5:7]))

    def _readFromPort(self, size):
        """Read data from the serial port. If the length of the data returned from 
        the WavTrigger does not match the requested size an OSError is raised 
        for the timeout condition.
        """
        result=self._wt.read(size)
        if len(result) != size:
            raise OSError(errno.ETIMEDOUT,"Connection timed out");
        return result

    def __delete__(self):
        """Close the serial port if the class instance goes out of scope.
        """
        self.close()


