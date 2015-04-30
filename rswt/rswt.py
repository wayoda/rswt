import time
import serial
import array
import struct
import binascii


#Constants for the commands a wavtrigger understands

# Reading data back from a WavTrigger
_WT_GET_VERSION = bytearray([0xF0,0xAA,0x05,0x01,0x55])
_WT_GET_SYS_INFO =  bytearray([0xF0,0xAA,0x05,0x02,0x55])
_WT_GET_STATUS =  bytearray([0xF0,0xAA,0x05,0x07,0x55])

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
    """
    A controller for a RobertSonics WavTrigger
    """
    def __init__(self,device, baud=57600, timeout=5.0):
        """
        Opens a serial port to the device and reads the 
        hardware version info of the WavTrigger.
        """
        self._wt=serial.Serial(port=device, baudrate=baud)
        self._wt.timeout=timeout
        if self._wt.isOpen():
            self._version=self._getVersion()
            self._voices,self._tracks=self._getSysInfo()

    def close(self):
        """
        Stops all playing track and closes the port to the WavTrigger.
        It's save to call this method even if the port is already closed
        """
        if self._wt.isOpen():
            self.stopAll()
            self._wt.close()

    @property
    def version(self):
        """
        Gets the version string of the WavTrigger firmeware
        """
        return self._version
    @property
    def voices(self):
        """
        Gets the number of polyphonic voices the WavTrigger can play
        """
        return self._voices

    @property
    def tracks(self):
        """
        Gets the number of tracks stored on the WavTrigger
        """
        return self._tracks

    def play(self,track):
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_PLAY,track)
            print binascii.hexlify(t)
            self._wt.write(t)

    def solo(self,track):
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_SOLO,track)
            print binascii.hexlify(t)
            self._wt.write(t)

    def stop(self,track):
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_STOP,track)
            print binascii.hexlify(t)
            self._wt.write(t)

    def pause(self,track):
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_PAUSE,track)
            print binascii.hexlify(t)
            self._wt.write(t)

    def resume(self,track):
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_RESUME,track)
            print binascii.hexlify(t)
            self._wt.write(t)

    def load(self,track):
        if self._isValidTrackNumber(track):
            t=self._setTrackForCommand(_WT_TRACK_LOAD,track)
            print binascii.hexlify(t)
            self._wt.write(t)

    def loop(self,track,status):
        if self._isValidTrackNumber(track):
            if status:
                t=self._setTrackForCommand(_WT_TRACK_LOOP_ON,track)
            else:
                t=self._setTrackForCommand(_WT_TRACK_LOOP_OFF,track)
            print binascii.hexlify(t)
            self._wt.write(t)

    def stopAll(self):
        self._wt.write(_WT_STOP_ALL)

    def resumeAll(self):
        self._wt.write(_WT_RESUME_ALL)

    def masterVolume(self,volume):
        vol=_WT_VOLUME
        vol[4],vol[5]=self._intToLsb(self._volumeToDb(volume))
        print binascii.hexlify(vol)
        self._wt.write(vol)

    def trackVolume(self,track,volume):
        tvol=_WT_TRACK_VOLUME
        tvol[4],tvol[5]=self._intToLsb(track)
        tvol[6],tvol[7]=self._intToLsb(self._volumeToDb(volume))
        print binascii.hexlify(tvol)
        self._wt.write(tvol)

    def pitch(self,offset):
        if offset>32767 :
            offset=32767
        if offset < -32767:
            ofset = -32767
        pitch=_WT_SAMPLERATE
        pitch[4],pitch[5]=self._intToLsb(offset)
        print binascii.hexlify(pitch)
        self._wt.write(pitch)

    def fade(self,track,volume,time):
        f=_WT_FADE
        f[4],f[5]=self._intToLsb(track)
        f[6],f[7]=self._intToLsb(self._volumeToDb(volume))
        f[8],f[9]=self._intToLsb(time)
        f[10]=0x00
        print binascii.hexlify(f)
        self._wt.write(f) 

    def fadeOut(self,track, time):
        f=_WT_FADE
        f[4],f[5]=self._intToLsb(track)
        f[6],f[7]=self._intToLsb(self._volumeToDb(0))
        f[8],f[9]=self._intToLsb(time)
        f[10]=0x01
        print binascii.hexlify(f)
        self._wt.write(f) 

    def playing(self):
        self._wt.write(_WT_GET_STATUS)
        time.sleep(0.25)
        n=self._wt.inWaiting()
        print n
        r=self._wt.read(n)
        print binascii.hexlify(r)


    def _isValidTrackNumber(self,track):
        if track>0 and track<1000:
            return True
        return False

    def _lsbToInt(self,lsbValue):
        """
        Convert the track number from 2 bytes in lsb order to an int value
        """
        return struct.unpack('<h',lsbValue)[0]

    def _intToLsb(self,value):
        """
        Converts an int value to a 2 byte tuple in lsb order
        """
        return (value & 0xFF, (value >> 8) & 0xFF)

    def _setTrackForCommand(self,cmd,track):
        """
        All track commands need a track argument in the data sent
        to the WavTrigger
        """
        cmd[5],cmd[6]=self._intToLsb(track)
        return cmd

    def _volumeToDb(self, vol):
        if vol<0 or vol>100:
            raise ValueError('Volume level invalid : '+str(vol))
        if vol==0:
            return -70
        if vol==100:
            return 10
        return -70+int(vol/1.25)

    def _getVersion(self):
        """
        Read version number from device
        """
        if(self._wt.write(_WT_GET_VERSION) != len(_WT_GET_VERSION)):
            return ''
        v=self._wt.read(25)
        if len(v) != 25:
            return ''
        if(v[:4]!='\xF0\xAA\x19\x81' or v[-1]!='\x55'):
            return ''
        return str(v[4:-1])

    def _getSysInfo(self):
        """
        Read system info from device
        """
        if(self._wt.write(_WT_GET_SYS_INFO) != len(_WT_GET_SYS_INFO)):
            return (0,0)
        v=self._wt.read(8)
        if len(v) != 8:
            return (0,0)
        if(v[:4]!='\xF0\xAA\x08\x82' or v[-1]!='\x55'):
            return (0,0)
        return (ord(v[4]),self._lsbToInt(v[5:7]))
        
    def __delete__(self):
        """
        Close the port if we are deleted
        """
        self.close()


