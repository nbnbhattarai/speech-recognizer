import audio
from feature_extractor.base import mfcc
import numpy

def get_features(audio_obj):
	return mfcc(numpy.array(audio_obj.sampdata_dec, dtype='int16'), audio_obj.framerate)