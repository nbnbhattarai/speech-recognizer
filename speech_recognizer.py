import recognition
import recorder
import sys
import audio
import feature_extractor
from decision_maker import DM
rec = recorder.Recorder()
aud = audio.Audio()


def print_usage():
    print('Usage: python speech_recognizer [options] [filename]')


def print_help():
    print_usage()
    print(
        "\nBasic Options:\n" +
        " -r  --record                  record and translate audio\n" +
        " -f  --file [filename]         translate from audio file\n" +
        " -h  --help                    print help.\n"
    )


def speech_recognize_aud(aud):
    """
    Given Audio data, recognize the speech and return
    the value
    """
    mfcc_features = feature_extractor.mfcc_feat.get_features(aud)
    feature_list = list(mfcc_features.flatten())
    dm = DM()
    dm.load('training_files_out')
    word = dm.get_near_word(feature_list)
    print('word recognized:', word)
    yn = input('is this correct?')
    if yn == 'n' or yn == 'N':
        wd = input('what is the actual word ?')
        dm.add_feature(feature_list, wd)
    else:
        dm.add_feature(feature_list, word)
    dm.save('training_files_out')


def speech_recognition_next():
    with recognition.recognition.Microphone() as source:
        print('Speck >>>')
        audio = recognition.recognizer.listen(source)
    try:
        print('Spoken word:', recognition.speech_rec(audio))
    except Exception as e:
        print('Error occured:', str(e))


def speech_recognizer_rec(second):
    """
    Record Speech First and Recognize that speech.
    second of record is predefined.
    """
    dm = DM()
    dm.load('training_files_out')
    print('words trained till now:', set([w[1] for w in dm.feature_word]))
    input('Press Enter to recognize word.')
    aud = rec.record(second)
    aud.play()
    features = feature_extractor.mfcc_feat.get_features(aud)
    features = list(features.flatten())
    word = dm.get_near_word(features)
    print('word recognized:', word)
    yn = input('is this correct ?')
    if yn == 'n' or yn == 'N':
        wd = input('what is the actual word ?')
        dm.add_feature(features, wd)
    else:
        dm.add_feature(features, word)
    dm.save('training_files_out')


def speech_recognizer_file(filename):
    """
    Recognize speec in given audio file
    Valid Audio Files : 'wave',
    """
    aud = audio.Audio()
    aud.loadfromfile(filename)
    speech_recognize_aud(aud)


if __name__ == '__main__':
    argv = sys.argv
    argc = len(argv)
    next_recog = False
    if argc < 2:
        print_usage()

    if '-n' in argv:
        next_recog = True

    if '-f' in argv or '--file' in argv:
        if '-f' in argv:
            f_index = argv.index('-f')
        else:
            f_index = argv.index('--file')
        filename = argv[f_index + 1]
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

    if next_recog:
        speech_recognition_next()

    if record_flag:
        speech_recognizer_rec(2)

    if file_flag:
        speech_recognizer_file(filename)

    if help_flag:
        print_help()
