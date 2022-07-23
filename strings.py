from music21.pitch import Pitch

class PitchList(list):

    TOO_LOW = 1000000

    def __init__(self, pitches):
        super().__init__(pitches)

    def _distance(self, first, second):
        m = second.midi - first.midi
        if m < 0:
            return self.TOO_LOW
        else:
            return m

    def minDistance(self, pitch):
        if not self:
            raise ValueError('list is empty')

        l = [self._distance(p, pitch) for p in self]
        m = min(l)
        if m == self.TOO_LOW:
            return None
        return m

    def indexMinDistance(self, pitch):
        m = self.minDistance(pitch)
        if m is None:
            lowest = sorted(self)[0]
            raise ValueError(f'pitch {pitch} is lower than lowest string {lowest}')
        for idx, p in enumerate(self):
            if self._distance(p, pitch) == m:
                return idx


class Strings:

    def __init__(self, pitches):
        self._pitches = pitches
        self._max = max(pitches)

    def __repr__(self):
        cls = self.__class__.__name__
        pitches = [p.nameWithOctave for p in self.pitches()]
        return f'<{cls} {pitches}>'

    @property
    def letters(self):
        l = self._pitches[:]
        l.reverse()
        txt = ''
        for p in l:
            if p.octave > 3:
                txt += p.name.lower()
            else:
                txt += p.name.upper()
        return txt

    def transpose(self, step):
        l = []
        for p in self._pitches:
            l.append(p.transpose(step))
        self._pitches = l

    def pitches(self, use_strings=[], same_octave=False):

        if same_octave:
            getter = lambda p : Pitch(p.name + '4')
        else:
            getter = lambda p : Pitch(p.nameWithOctave)

        l = []
        for i, p in enumerate(self._pitches):
            if not use_strings:
                l.append(getter(p))
            elif i+1 in use_strings:
                l.append(getter(p))
        return PitchList(list(l))



    def pitchesFromNote(self, note, use_strings=[], pitch_range=[]): #TODO
        if hasattr(note, 'pitch'):
            pitch = note.pitch
        else:
            pitch = note

        if pitch.octave is None:
            same_octave = True
            getter = lambda p : Pitch(p.name)
        else:
            same_octave = False
            getter = lambda p : Pitch(p.nameWithOctave)

        pitches = self.pitches(use_strings, same_octave=same_octave)
        idx = pitches.indexMinDistance(pitch)
        l = []
        found = False
        for i, _ in enumerate(pitches):
            if i == idx:
                found = True
                l.append(getter(pitch))
            else:
                l.append(getter(pitches[i]))
        if not found:
            raise KeyError(idx)
        return l


class FiveStringBanjo(Strings):

    tunings = {
            'open_g': 'gdGBD',
            'modal_g': 'gdGCD',
            #'open_d': 'adF#AD', #FIXME need a parser for sharps
            'double_c': 'gcGCD',
            'single_c': 'gCGBD',
    }
    # e phrygian?  # e a b (sus2)
    tunings['sawmill'] = tunings['modal_g']
    tunings['standard'] = tunings['open_g']

    @classmethod
    def _fromTuning(cls, letters):
        #TODO add checks for valid notes

        def _toPitch(letter):
            octave = '4' if letter.islower() else '3'
            return Pitch(letter + octave)

        pitches = [_toPitch(k) for k in letters[-1::-1]]
        return cls(pitches)

    @classmethod
    def fromTuning(cls, letters='gDGBD'):
        return cls._fromTuning(letters)

    @classmethod
    def fromNamedTuning(cls, name='standard'):
        return cls._fromTuning(cls.tunings[name])



if __name__ == '__main__':

    from music21.note import Note
    from music21.chord import Chord
    from music21 import converter
    #stream = converter.parse('data/shady.abc')

    '''
    for name in FiveStringBanjo.tunings:
        banjo = FiveStringBanjo.fromNamedTuning(name)
        print(name, banjo)
        chord = Chord(banjo.pitches(use_strings=[1,2,3]))
        print(chord.commonName)
    '''

    banjo = FiveStringBanjo.fromNamedTuning('open_g')
    print(banjo)
    use = [1,2,3]
    #print(banjo.pitches(use_strings=use, same_octave=True, ))
    pitches = banjo.pitchesFromNote(Note('g4'), use)
    print(pitches)

    #banjo.transpose(2)
    print(banjo)
    print(banjo.letters)


