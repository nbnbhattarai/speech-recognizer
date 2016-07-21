import wave
import pyaudio
import datetime


class Audio:
    """
    This class open data from wave file and stores
    in convenient way for processing.
    """

    def __init__(self, filename=False):
        """
        Load file content if filename
        is provided
        """
        if not filename:
            self.filename = filename
            self.loadfile(self.filename)
        self.CHUNK = 1024
            
    def loadfile(self, filename):
        """
        Load Content from wave file 
        of given filename
        """
        wf = wave.open(filename, 'rb')
        self.frames = wf.readframes(self.CHUNK)
        self.framerate = wf.getframerate()
        self.channels = wf.getchannels()
        self.samplewidth = wf.getsampwidth()
        self.duration = float(len(self.frames)/self.framerate)
        
    def play(self):
        """
        Play audio file
        """
        if len(self.frames) <= 0:
            print('>> no audio file loaded!!')
        else:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(self.samplewidth),
                            channels=self.channels,
                            rate=self.framerate,
                            output=True)
            
            for i in range(0, len(self.frames)):
                data = self.frames[i]
                percent = float(i/self.duration * 100)
                curr_sec = self.duration * percent
                print("\r %s / %s (%f%%)"
                      % (str(datetime.timedelta(seconds=int(curr_sec))),
                         str(datetime.timedelta(seconds=int(self.duration))),
                         percent), end='')
                stream.write(data)

            stream.stop_stream()
            stream.close()
            p.terminate()


def main():


if __name__ == '__main__':
    main()
