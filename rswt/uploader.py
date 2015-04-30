import serial
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


class WavTriggerUploader(object):
    """
    A firmware upload utility for the RobertSonics WavTrigger
    """
    def __init__(self,device,timeout=0.25):
        """
        Opens a serial port to the device and reads the 
        hardware version info of the WavTrigger
        """
        self._wt=serial.Serial(port=device, baudrate=57600)
        self._wt.timeout=timeout
        self.version=self.contact()       
        if self.version is None:
            print 'Fail'

    def close(self):
        self._wt.close()

    def contact(self):
        if not self._wt.isOpen():
            return False
        con='\x7F'
        ok='\x79'
        connected=False
        for retries in xrange(50):
            self._wt.write(con)
            r=self._wt.read()
            if len(r)==1 and r==ok:
                connetced=True
                break
        if not connected:
            return None
        cmd='\x00\xFF'
        print self._wt.write(cmd)
        r=self._wt.read(2)
        print len(r)
        if len(r) !=2 :
            print 'no read'
            return None
        if r[0] != '\x79' :
            print 'invalid ok'
            return None
        cnt=ord(r[1])
        if cnt>64 :
            print 'count too big'
            return None
        r=self._wt.read(cnt)
        if r != cnt:
            print 'no version'
            return None
        print binascii.hexlify(r)
        return r
    

if __name__=='__main__':
    wtu=WavTriggerUploader('/dev/UsbSerial')

    wtu.close()

