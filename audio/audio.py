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
        Load file content if filename
        is provided
        """
        self.fileloaded = False
        self.CHUNK = 1024
        if filename:
            self.loadfile(filename)
            
    def loadfile(self, filename):
        """
        Load Content from wave file 
        of given filename
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
    
    def print_details(self):
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


def main(filename):
    audio = Audio(filename=filename)
    audio.print_details()
    audio.play()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit()
    filename = sys.argv[1]
    main(filename)
