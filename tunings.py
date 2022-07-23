from copy import deepcopy

from music21.note import Note
from music21.pitch import Pitch
from music21.chord import Chord

from util import pitchesToChord
from util import iterNotes



class Tune:

    def __init__(self, stream):

        self._pitches = set()
        self._keys = set()
        self._chords = set()
        self._stream = deepcopy(stream)

        for note, chord in iterNotes(stream.flatten().notes):
            #XXX make sure we copy as as hashes for pitch include more than just the name and octave
            self._pitches.add(Pitch(note.pitch.nameWithOctave))
            self._keys.add(note.pitch.name)

        for note in stream.flatten().notes:
            if note.isChord:
                self._chords.add(note.pitches)

    @property
    def stream(self): return self._stream

    @property
    def pitches(self): return sorted(self._pitches)

    @property 
    def keys(self): return sorted(set([p.name for p in self._pitches]))

    @property
    def chords(self): 
        l = []
        for pitches in self._chords:
            l.append(pitchesToChord(pitches))
        return l

    def _beats(self, number):
        l = []
        for measure in self.stream.recurse().getElementsByClass('Measure'):
            found = False
            for item in measure:
                if hasattr(item, 'isChord') and item.beat == number:
                    found = True
                    l.append(item)
            if not found:
                l.append(None)
        return l
    
    def beats(self, number): return self._beats(number)
        

class StringTune(Tune):

    def __init__(self, stream, strings):
        super().__init__(stream)
        self._strings = strings
        self._non_open_pitches = set()

    @property
    def strings(self): return self._strings

    def closed_pitches(self):

        l = []
        pitches = set([p.name for p in model_g_banjo.pitches])
        for measure in stream.recurse().getElementsByClass('Measure'):
            m = []
            l.append(m)
            for note, chord in iterNotes(measure):
                if note.pitch.name not in pitches:
                    m.append(note)
        return l


if __name__ == '__main__':

    open_g_banjo = Strings([ Note('d4'), Note('b3'), Note('g3'), Note('d3'), ], Note('g4'))
    model_g_banjo = Strings([ Note('d4'), Note('g3'), Note('c3'), Note('d3'), ], Note('g4'))
    # e phrygian?  # e a b (sus2)

    from music21 import converter
    from music21.stream import Stream
    #stream = converter.parse('data/shady.abc')

    stream = converter.parse('data/merry_it_is.xml')
    tune = StringTune(stream, model_g_banjo)
    print(tune.keys)

    '''
    stream = converter.parse('data/shady_grove_turknett.xml')
    tune = StringTune(stream, model_g_banjo)

    l = []
    for a, b in zip(tune.beats(1), tune.beats(2)):
        l.append(a)
        l.append(b)

    stream = Stream()
    for note in l:
        if note:
            note.duration.quarterLength = 1
            stream.append(note)
    #stream.show()
    print(' '.join([(n and n.pitch.name) or 'z' for n in l]))

    stream = converter.parse('data/shady.abc')
    tune = StringTune(stream, model_g_banjo)
    stream.show()

    l = []
    for a, b, c, d in zip(tune.beats(1), tune.beats(2), tune.beats(3), tune.beats(4)):
        l.append(a)
        l.append(b)
        l.append(c)
        l.append(d)

    stream = Stream()
    for note in l:
        if note:
            note.pitch.midi -= 2
            note.duration.quarterLength = 1
            stream.append(note)
    print(' '.join([(n and n.pitch.name) or 'z' for n in l]))
    stream.show()
    '''
