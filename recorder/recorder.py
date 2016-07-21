import pyaudio
import wave

## to show second to h:m:s format
import datetime

class Recorder:
    """
    This class help to record audio in RAW format
    (WAVE) format.
    """
    def __init__(self, format=pyaudio.paInt16,
                 channels=1,
                 rate=44100):
        """
        Initialize default values(specifications)
        of recording audio_file
        """
        self.CHUNK = 1024
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = rate

    def record_audio(self, outfilename, record_seconds):
        self.wave_output_filename = outfilename
        p = pyaudio.PyAudio()
        self.stream = p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK)
        print('>> recording...')
        
        frames = []
        for i in range(0, int(self.RATE / self.CHUNK * record_seconds)):
            data = self.stream.read(self.CHUNK)
            curr_sec = int(i/self.RATE * self.CHUNK)
            percent = curr_sec / record_seconds * 100
            print("\r %s / %s (%f%%)"
                  % (str(datetime.timedelta(seconds=curr_sec)),
                     str(datetime.timedelta(seconds=(record_seconds-1))),
                     percent), end='')
            
            frames.append(data)
        
        print('\n>> done!')

        self.stream.stop_stream()
        self.stream.close()
        p.terminate()

        wf = wave.open(outfilename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        print('>> file %s saved!!' % outfilename)
        wf.close()

    def remove_noise(self, filename, noise_amp=3000):
        wf = wave.open(filename, 'rb')
        frames  = wf.readframes(self.CHUNK)
        frames_nonoise = []
        for frame in frames:
            if abs(frame) <= noise_amp:
                frame = 0
            frames_nonoise.append(frame)
        wf.close()
        
        p = pyaudio.PyAudio()
        
        wf = wave.open(filename+'-nonoise', 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames_nonoise))
        print('>> file %s saved!' % (filename+'-nonoise'))
        wf.close()
