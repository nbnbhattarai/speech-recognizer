import wave
import pyaudio
import datetime
import sys
import numpy.fft as fft


class Audio:
    """
    This class open data from wave file and stores
    in convenient way for processing.
    """

    def __init__(self, filename=False, frames=None):
        """
        loadfile if filename is provided
        """
        self.fileloaded = False
        # chunk value changed from 1024 to 400 to perform
        # Fourier transform and get phonems (for acoustic model)
        self.CHUNK = 400
        # it contains all sample values in decimal format
        self.frames_dec = []
        if filename:
            self.loadfile(filename)
        elif frames:
            self.loadfromframes(frames)

    def get_decimal_amps(self):
        """
        it calculates the decimal equivalent of all the samples
        and store it's value in self.framed_dec list object.
        It is used for further processing of audio signal.
        """
        for frame in self.frames:
                if frame:
                    for i in range(0, len(frame), 2):
                        self.frames_dec.append(int.from_bytes(
                            frame[i:i+2], byteorder='little')
                        )

    def loadfromframes(self, frames,
                       framerate=8000,
                       channels=1,
                       samplewidth=2):
        """
        Load audio data from list of frames data
        it is assumed to have chunk size of 400
        """
        self.frames = frames
        self.framerate = framerate
        self.channels = channels
        self.samplewidth = samplewidth
        self.nframes = len(frames)
        self.filesize = self.nframes * self.samplewidth + 44
        self.duration = float(self.nframes / self.framerate)
        self.loaded = True

        self.get_decimal_amps()

        return True

    def loadfromfile(self, filename):
        """
        Load Content from wave file of given filename.
        if file loaded, it returns True
        else it returns False
        """
        print('>> loading file %s' % filename, end='')
        wf = wave.open(filename, 'rb')
        if wf:
            print(' [ done ]')
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

            self.get_decimal_amps()

            return True
        print(' [ error ]')
        return False

    def fft(self):
        """
        return list containing result from the
        fast fourier transform of sample values of
        audio signal
        """
        result = []
        for i in range(0, len(self.frames_dec), 400):
            result.extend(list(fft.fft(self.frames_dec[i:i+400])))
        return result

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
        print('>> playing audio', end='')
        if not self.fileloaded:
            print(' [ error ]')
        else:
            print(' [ started ]')
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

    def get_noise_amp(self):
        """
        Get the amplitude of noise by seeing in all the sample values.
        Not quite good yet, need to implement.
        """
        all_values = []
        for i in range(0, len(self.frames)):
            for j in range(0, len(self.frames[i]), 2):
                all_values.append(self.frames[i][j+1]*(2**8)+self.frames[i][j])
        all_values.sort()
        sum_values = []
        n = 0
        for i in range(len(all_values)):
            if n > 1000:
                break
            if all_values[i] not in sum_values:
                sum_values.append(all_values[i])
                n += 1
        return float(sum(sum_values)/n)

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
        # noise_amp = self.get_noise_amp()
        # print('noise amp:', noise_amp)
        print('>> removing noise started', end='')
        count = 0
        new_self = self
        frame = []
        frames_size = len(self.frames)
        for i in range(0, frames_size):
            # print('len:', len(self.frames[i]))
            frame.append(list(self.frames[i]))

        for i in range(0, len(frame)):
            # print('len:', len(frame[i]))
            for j in range(0, len(frame[i]), 2):
                actual_value = frame[i][j+1]*(2**8)+frame[i][j]
                if actual_value <= noise_max_amp:
                    frame[i][j+1], frame[i][j] = 0, 0
                    count += 1

        new_self.frames.clear()
        for i in range(0, frames_size):
            new_self.frames.append(bytes(frame[i]))

        print(' [ done ]')
        print('size: ', len(frame[0]))
        print('count: ', count)
        return new_self

    def write(self, filename):
        """
        write the audio data to a file
        """
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.samplewidth)
        wf.setframerate(self.framerate)
        wf.writeframes(b''.join(self.frames))
        wf.close()


def main(filename, outfile=False):
    audio = Audio(filename=filename)
    audio.print_details()
    print('type:', type(audio.frames[0]), 'size: ', len(audio.frames[0]))
    audio.play()
    new_audio = audio.remove_noise()
    new_audio.play()
    if outfilename:
        print('>> writing to file %s.' % outfile, end='')
        new_audio.write(outfile)
        print(' [ done ]')

if __name__ == '__main__':
    """
    for testing purpose
    """
    if len(sys.argv) < 2:
        print('Usage: python audio.py [filename] [outputfilename-optional]')
        sys.exit()
    outfilename = False
    if len(sys.argv) == 3:
        outfilename = sys.argv[2]
    filename = sys.argv[1]
    main(filename, outfilename)
