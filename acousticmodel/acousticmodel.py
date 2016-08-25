import audio

class AcousticModel:
    def __init__(self, audio=None):
        if audio:
            self.audio = audio
