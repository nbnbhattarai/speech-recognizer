import wave
import pyaudio
import datetime
import sys

class Audio:
    """
    This class open data from wave file and stores
    in convenient way for processing.
    """

    def __init__(self, filename=False):
        """
        loadfile if filename is provided
        """
        self.fileloaded = False
        self.CHUNK = 1024
        if filename:
            return self.loadfile(filename)
        return True
        
    def loadfile(self, filename):
        """
        Load Content from wave file 
        of given filename.
        if file loaded, it returns True
        else it returns False
        """
        print('>> loading file %s' % filename)
        wf = wave.open(filename, 'rb')
        if wf:
            self.filename = filename
            
            self.frames = []
            data = wf.readframes(self.CHUNK)
            while len(data) > 0:
                data = wf.readframes(self.CHUNK)
                self.frames.append(data)

            self.framerate = wf.getframerate()
            self.channels = wf.getnchannels()
            self.samplewidth = wf.getsampwidth()
            self.nframes = wf.getnframes()
            self.filesize = self.nframes * self.samplewidth + 44
            self.duration = float(self.nframes / self.framerate)
            self.fileloaded = True
            return True
        return False
    
    def print_details(self):
        """
        print details of audio data
        """
        if self.fileloaded:
            print(
                "filename    : " + self.filename + '\n' +
                "filesize    : " + str(self.filesize) + '\n' +
                "framerate   : " + str(self.framerate) + '\n' +
                "len(frames) : " + str(len(self.frames)) + '\n' +
                "channels    : " + str(self.channels) + '\n' +
                "samplewidth : " + str(self.samplewidth) + '\n' +
                "duration    : " + str(self.duration)
                )
        
    def play(self):
        """
        Play audio file
        """
        if not self.fileloaded:
            print('>> no audio file loaded!!')
        else:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(self.samplewidth),
                            channels=self.channels,
                            rate=self.framerate,
                            output=True)
            
            for i in range(0, len(self.frames)):
                data = self.frames[i]
                percent = i/len(self.frames)
                curr_sec = percent * self.duration
                print("\r %s / %s (%f%%)"
                      % (str(datetime.timedelta(seconds=int(curr_sec))),
                         str(datetime.timedelta(seconds=int(self.duration))),
                         percent * 100), end='')
                stream.write(data)
            print('\n')
            stream.stop_stream()
            stream.close()
            p.terminate()

    def remove_noise(self, noise_max_amp=3000):
        """
        Return New instance of Audio class which has frames value
        with removed noise value (make amplitude of noise i.e.3000 to 
        zero.
        info: the audio sample is of 16 bit (2 bytes), there is 1024
        samples in one frame. Byte are stored in Little Endian format
        so get equivalent of 2byte in decimal format and if the equivalent
        value is lesser than noise_max_amp(3000) then make these value zero.
        """
        count = 0
        new_self = self
        print(len(self.frames[0]))
        for i in range(0, len(self.frames)):
            for j in range(0, int(len(self.frames[i])), 2):
                if self.frames[i][j:j+2].hex() <= hex(noise_max_amp):
                    print(self.frames[i][j:j+2].hex(), end='/')
        print('count:', count)
        return new_self
    

def main(filename):
    audio = Audio(filename=filename)
    audio.print_details()
    audio.play()
    #new_audio = audio.remove_noise()
    #new_audio.play()

if __name__ == '__main__':
    """
    for testing purpose
    """
    if len(sys.argv) < 2:
        print('Usage: python audio.py [filename]')
        sys.exit()
    filename = sys.argv[1]
    main(filename)
