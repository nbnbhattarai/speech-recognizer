import pyaudio
import wave
import sys

import audio
# to show second to h:m:s format
import datetime


class Recorder:
    """
    This class help to record audio in RAW format
    (WAVE) format.
    """

    def __init__(self, format=pyaudio.paInt16,
                 channels=1,
                 rate=16000):
        """
        Initialize default values(specifications)
        of recording audio_file
        """
        self.CHUNK = 400  # same chunk size is used as in Audio class
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = rate

    def record(self, record_seconds, outfilename=None):
        """
        It records audio and returns these data in Audio object format.
        if outfilename is given it also writes the data in disk with
        the given filename.
        """
        self.wave_output_filename=outfilename
        p=pyaudio.PyAudio()
        self.stream=p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK)
        print('>> recording...')

        frames=[]
        for i in range(0, int(self.RATE / self.CHUNK * record_seconds)):
            data=self.stream.read(self.CHUNK)
            curr_sec=int(i / self.RATE * self.CHUNK)
            percent=curr_sec / record_seconds * 100
            print("\r %s / %s (%f%%)"
                  % (str(datetime.timedelta(seconds=curr_sec)),
                     str(datetime.timedelta(seconds=(record_seconds - 1))),
                     percent), end='')

            frames.append(data)

        print('\n>> done!')

        self.stream.stop_stream()
        self.stream.close()
        p.terminate()

        sampdata_bytes = bytes(b''.join(frames))

        audio_data=audio.Audio()
        audio_data.loadfromsampdata(sampbytes=sampdata_bytes,
                                  framerate=self.RATE,
                                  channels=self.CHANNELS)

        # if outfilename if given, then write to that file
        # else only audio data is returned
        if outfilename:
            wf=wave.open(outfilename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            print('>> file %s saved!!' % outfilename)
            wf.close()
        return audio_data


def main(filename, duration):
    recorder=Recorder()
    recorder.record(filename, duration)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python recorder.py [filename] [duration in second]')
        sys.exit()
    main(sys.argv[1], int(sys.argv[2]))
