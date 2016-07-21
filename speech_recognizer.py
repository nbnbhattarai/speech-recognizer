import recorder
import sys


def usage():
    print('Usage: python speech_recognizer [options] [filename]')


def print_help():
    print(
        "Help"+
        "==============="+
        "Options."+
        "-r  --record       record and translate audio"+
        "-f  --file         translate from audio file"+
        "-h  --help         print help."
        )


def speech_recognizer_rec():
    """
    Record Speech First and Recognize that speech
    """
    pass


def speech_recognizer_file(filename):
    """
    Recognize speec in given audio file
    Valid Audio Files : 'wave',
    """
    pass


if __name__ == '__main__':
    argv = sys.argv
    argc = len(argv)
    if '-f' in argv or '--file' in argv:
        if '-f' in argv:
            f_index = argv.index('-f')
        else:
            f_index = argv.index('--file')
        filename = argv[f_index+1]
        file_flag = True
    else:
        file_flag = False

    if '-r' in argv or '--record' in argv:
        record_flag = True
    else:
        record_flag = False

    if '-h' in argv or '--help' in argv:
        help_flag = True
    else:
        help_flag = False

    if record_flag:
        speech_recognizer_rec()

    if file_flag:
        speech_recognizer_file(filename)

    if help_flag:
        print_help()
