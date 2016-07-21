#!/usr/bin/python3

import sys
from recorder import Recorder


def main(filename, seconds):
    recorder = Recorder()
    recorder.record_audio(filename, seconds)

    
if __name__ == '__main__':
    if(len(sys.argv) != 3):
        print ('Usage: ./recorder_test.py [output_filename] [record_seconds]')
        sys.exit()
    print('Filename: %s\nSeconds: %s' % (sys.argv[1], sys.argv[2]))
    sec = int(sys.argv[2])
    main(sys.argv[1], sec)
