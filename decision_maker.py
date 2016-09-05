import numpy
import sys
import pickle
import feature_extractor
import audio


class DM:

    def __init__(self):
        self.feature_word = []

    def add_feature(self, feature, word):
        if (feature, word) in self.feature_word:
            print('Feature,word already stored.')
        else:
            self.feature_word.append((feature, word))

    def train_from_files(self, filename):
        """
        filename contains filename which stores audio file path
        and respective word in that audio file.
        """
        file = open(filename, 'r')
        lines = file.readlines()
        filename_word = []
        for l in lines:
            if len(l) <= 1:
                continue
            filename_word.append(tuple(l.split()))
        aud = audio.Audio()
        for f, w in filename_word:
            try:
                aud.loadfromfile(f)
                features = feature_extractor.mfcc_feat.get_features(aud)
                features = features.flatten()
                self.add_feature(list(features), w)
            except Exception as e:
                print('Exception(', str(e), ')')

    def rms(self, f1, f2):
        f1_a = numpy.array(f1)
        f2_a = numpy.array(f2)
        return numpy.sqrt((((f1_a - f2_a)**2).sum()) / len(f1_a))

    def get_near_word(self, feature):
        rms_w = []
        for f, w in self.feature_word:
            rms_w.append((self.rms(feature, f), w))
        return sorted(rms_w)[0][1]

    def save(self, filename):
        print('Writing to file.')
        try:
            file = open(filename, 'wb')
            file.write(pickle.dumps(self.__dict__))
            print('[done]')
        except Exception as e:
            print('[error :', str(e), ']')

    def load(self, filename):
        try:
            file = open(filename, 'rb')
            datapickle = file.read()
            file.close()
            self.__dict__ = pickle.loads(datapickle)
            print('[done]')
        except Exception as e:
            print('[error :', str(e), ']')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python decision_maker.py [filename]')
        sys.exit()
    fname = sys.argv[1]
    dm = DM()
    dm.train_from_files(fname)
    dm.save(fname + '_out')
