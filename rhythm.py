from random import randint
from math import floor
from pydub import AudioSegment, playback
from pydub.effects import low_pass_filter

class Bar:
    def __init__(self, pattern):
        self.pattern = pattern
    
    @property
    def length(self):
        return len(self.pattern)

class Phrase:
    def __init__(self, bars, bpm):
        self.bars = bars
        self.bpm = bpm

    @property
    def length(self):
        length = 0
        
        for bar in self.bars:
            length += bar.length
        
        return length

    @property
    def length_ms(self):
        return self.length * (60000/self.bpm)

    @property
    def timings(self):
        timings = []
        time = 0

        for bar in self.bars:
            for beat in bar.pattern:
                if beat == 'x':
                    timings.append(time)

                time += 60000/self.bpm

        return timings

    def to_audio(self, effect, emphasis=0): # Effect should be a Pydub audiosegment
        audio = AudioSegment.silent(0)
        effects = []

        for bar in self.bars:
            beat_count = 0

            for beat in bar.pattern:
                if beat == 'x':
                    if beat_count == emphasis:
                        effects.append(effect)
                    else:
                        effects.append(low_pass_filter(effect, 6000) - 1)     

                beat_count += 1

        for i in range(0, len(effects)):
            audio = audio[:self.timings[i]]

            if len(audio) < self.timings[i]:
                audio = audio + AudioSegment.silent(self.timings[i]-len(audio))

            audio = audio + effects[i]

        if len(audio) < self.length_ms:
            audio = audio + AudioSegment.silent(self.length_ms - len(audio)) 

        return audio



def generate_pattern(length):
    pause_quota = randint(0, floor(length/2))
    pauses = []
    pattern = ['x'] * length

    if pause_quota != 0:
        for i in range(0, pause_quota):
            pattern[randint(1, length - 1)] = '-' # The first beat can't be a pause. There can be less pauses than the quota.

    return pattern


        
def generate_phrase(bpm, lengths):
    bars = []
    for i in lengths:
        bars.append(Bar(generate_pattern(i)))

    return Phrase(bars, bpm)

"""
phrase = generate_phrase(140, [4])
print(phrase.bars[0].pattern)
kick = AudioSegment.from_wav('kick.wav')
playback.play(phrase.to_audio(kick))
"""