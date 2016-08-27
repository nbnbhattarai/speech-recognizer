import wave
import pyaudio
import datetime
import sys
import numpy.fft as fft
import matplotlib.pyplot as plt
import numpy as np


class Audio:
    """
    This class open data from wave file and stores
    in convenient way for processing.
    """

    def __init__(self, filename=None, frames=None):
        """
        loadfromfile if filename is provided
        """
        self.fileloaded = False
        self.loaded = False

        self.frames_dec = []

        if filename:
            self.loadfromfile(filename)
        elif frames:
            self.loadfromframes(frames)

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

            self.sampdata_bytes = bytes(wf.readframes(wf.getnframes()))
            self.get_decimal_amps()  # get sample value in signed int format

            # get sample data in frame with
            self.frames_dec = self.get_frames()

            # basic information about audio file
            self.framerate = wf.getframerate()
            self.nchannels = wf.getnchannels()
            self.samplewidth = wf.getsampwidth()
            self.nframes = wf.getnframes()
            self.filesize = self.nframes * self.samplewidth + 44
            self.duration = float(self.nframes / self.framerate)
            self.fileloaded = True

            return True
        print(' [ error ]')
        return False

    def get_frames(self, framecount=400, overlap=240):
        """
        Return Frames of value.
        """
        frames = []
        for i in range(0, len(self.sampdata_dec), framecount - overlap):
            frames.append(self.sampdata_dec[i:i + framecount])
        return frames

    def get_decimal_amps(self):
        """
        Tested fine.. Working.

        it calculates the decimal equivalent of all the samples
        and store it's value in self.framed_dec list object.
        It is used for further processing of audio signal.
        """
        self.sampdata_dec = []
        for i in range(0, len(self.sampdata_bytes), 2):
            dt = []
            dt.append(self.sampdata_bytes[i])
            dt.append(self.sampdata_bytes[i + 1])
            bt_dt = bytes(dt)
            decimal_val = int.from_bytes(
                bt_dt, byteorder='little', signed=True)
            self.sampdata_dec.append(decimal_val)

    def loadfromsampdata(self, sampbytes=None,
                         sampdec=None,
                         framerate=16000,
                         channels=1,
                         samplewidth=2):
        """
        Load audio data from list of frames data
        it is assumed to have chunk size of 400
        """
        if sampbytes:
            self.sampdata_bytes = sampbytes
            self.get_decimal_amps()
            self.nframes = len(sampbytes)/2
        if sampdec:
            self.sampdata_dec = sampdec
            self.nframes = len(sampdata_dec)

        self.framerate = framerate
        self.channels = channels
        self.samplewidth = samplewidth
        self.filesize = self.nframes * self.samplewidth + 44
        self.duration = float(self.nframes / self.framerate)
        self.loaded = True

        return True

    def fft(self):
        """
        return list containing result from the
        fast fourier transform of sample values of
        audio signal
        """
        result = []
        # fourier transform are taken for each frames.
        # with sample of 400 in each frame
        # and 240 samples being overlapped

        frames_dec = self.get_frames()

        for frame in frames_dec:
            result.extend(list(fft.fft(frame)))
        return result

    def plot_amp(self):
        # N = len(fftdata)  # length of samples
        # T = 1.0/float(self.framerate)  # sample spacing
        self.samp_normalized = np.array(self.sampdata_dec)
        self.samp_normalized = self.samp_normalized / (2**15)
        # print(list(self.samp_normalized))
        x_time = np.array(range(0, len(self.sampdata_dec))) / self.framerate
        # print('nd:', self.samp_normalized[:10])
        fig, ax = plt.subplots()

        ax.plot(x_time, self.samp_normalized)

        plt.show()

    def plot_fftdata(self):
        fftdata = self.fft()
        # N = len(fftdata)  # length of samples
        # T = 1.0/float(self.framerate)  # sample spacing
        xf = np.array(range(0, len(fftdata)))
        # xf = np.linspace(0.0, float(self.framerate), len(self.sampdata_dec))
        print('len fftdata:', len(fftdata))
        print('len xf:', len(xf))

        fig, ax = plt.subplots()

        ax.plot(xf, np.abs(np.asarray(fftdata)[:]))

        plt.show()

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
        if not (self.fileloaded or self.loaded):
            print(' [ error ]')
        else:
            print(' [ started ]')
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(self.samplewidth),
                            channels=self.channels,
                            rate=self.framerate,
                            output=True)

            for i in range(0, len(self.sampdata_bytes), self.CHUNK):
                data = self.sampdata_bytes[i:i + self.CHUNK]
                percent = float(i / len(self.sampdata_bytes))
                curr_sec = float(percent * self.duration)
                print("\r %s / %s (%f%%)"
                      % (str(datetime.timedelta(seconds=int(curr_sec))),
                         str(datetime.timedelta(seconds=int(self.duration))),
                         percent * 100), end='')
                stream.write(data)
            print('\n')
            stream.stop_stream()
            stream.close()
            p.terminate()

    def write(self, filename):
        """
        write the audio data to a file.
        This is not tested because wont be a good use.
        """
        print('Writing Audio file .')
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.samplewidth)
            wf.setframerate(self.framerate)
            wf.writeframes(self.sampdata_bytes)
            wf.close()
            print(' [ Done ]')
        except Exception:
            print(' [ Error ]')


def main(filename, outfile=False):
    audio = Audio(filename=filename)
    audio.print_details()
    print('type:', type(audio.frames[0]), 'size: ', len(audio.frames[0]))
    audio.play()
    print('\n\n')
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
    aud = Audio()
    aud.loadfromfile('../data/audio/test/1_hello.wav')
    aud.get_decimal_amps()
    # aud.play()
    # print(aud.frames_dec)
    # aud.plot_amp()
    aud.plot_fftdata()
    if len(sys.argv) < 2:
        print('Usage: python audio.py [filename] [outputfilename-optional]')
        sys.exit()
    outfilename = False
    if len(sys.argv) == 3:
        outfilename = sys.argv[2]
    filename = sys.argv[1]
    main(filename, outfilename)
