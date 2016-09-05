import audio
import recorder
import os

# roll_no = input('enter your roll no (eg.522):')
aud = audio.Audio()
while True:
    sec = int(2)
    sec2 = input('enter second to record(default=2sec):')
    if sec2.isnumeric():
        sec = int(sec2)
    rec = recorder.Recorder()

    while True:
        input('Hit Enter and speak.')
        aud = rec.record(sec)
        aud.play()
        yn = input('is this correct (y/n)?')
        if yn == 'n' or yn == 'N':
            break

        txt = input('enter spoken word.')
        i = 0
        fname = ''
        while True:
            # fname = txt + '_' + str(roll_no) + '_' + str(i) + '.wav'
            fname = txt + '_' + str(i) + '.wav'
            if not os.path.isfile('data/audio/training/' + fname):
                break
            i = i + 1
        print('filename:', fname)
        aud.write('./data/audio/training/' + fname)
        yn = input('record again (y/n) ?:')
        if yn == 'n' or yn == 'N':
            break
