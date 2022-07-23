from copy import deepcopy

from music21 import converter
from music21.note import Note
from music21.pitch import Pitch
from music21.duration import Duration
from music21.chord import Chord
from music21.clef import Clef
from music21.key import Key
from music21.meter.base import TimeSignature

from abstract_parser import AbstractParser


class Music21Parser(AbstractParser):

    data_kind = 'music21'

    def open(self, fname):
        return converter.parse(fname)
    
    def write(self, stream, fname, kind='xml'):
        stream.write(kind, fp=fname)

    def _cloneNote(self, note, quarterLength, pitchName):

        if quarterLength is not None:
            duration = Duration(quarterLength)
        else:
            duration = Duration(note.duration.quarterLength)

        if pitchName is not None:
            pitch = Pitch(pitchName)
        else:
            pitch = Pitch(note.pitch.nameWithOctave)

        new = deepcopy(note)
        new.pitch = pitch
        new.duration = duration
        return new

    def cloneItem(self, item, quarterLength=None, pitchName=None): #FIXME handle chords and rests

        if not item.isChord:
            out = self._cloneNote(item, quarterLength, pitchName)
        elif item.isChord:
            l = []
            for note in item:
                l.append(self._cloneNote(note, quarterLength, pitchName))
            out = Chord(l)
        else:
            raise ValueError('should not get here')#FIXME
        return out

    def replaceItem(self, stream, old, new):
        off = old.offset
        stream.remove(old)
        stream.insert(off, new)
        new.offset = off

    def parse(self, stream):
        self.handleMetaData(stream, stream[0])
        for part in stream[1:]:
            if not hasattr(part, 'iter'):
                self.handleOtherThanMeasure(stream, part)
            else:
                for measure in part:
                    if hasattr(measure, 'iter'):
                        self._handleMeasure(measure)
                        self.handleMeasure(stream, measure)
                    else:
                        self.handleOtherThanMeasure(stream, measure)
        return stream

    def _handleMeasure(self, measure):
        for item in measure:
            if hasattr(item, 'isNote'):
                #rests
                if item.isRest:
                    self.handleRest(measure, item)
                else:
                    #notes
                    self.handleChordOrNote(measure, item)
                    if item.isNote:
                        self.handleNote(measure, item)
                    #chords
                    elif item.isChord:
                        self.handleChord(measure, item)
                        for note in item:
                            self.handleNote(measure, note)
            else:
                if isinstance(item, Clef):
                    self.handleClef(measure, item)
                elif isinstance(item, Key):
                    self.handleKey(measure, item)
                elif isinstance(item, TimeSignature):
                    self.handleTimeSignature(measure, item)
                else:
                    self.handleOtherThanNote(measure, item)

    #public functions for overiding

    def handleTimeSignature(self, measure, clef):
        pass

    def handleClef(self, measure, clef):
        pass

    def handleKey(self, measure, key):
        pass

    def handleMetaData(self, stream, meta):
        pass

    def handlePart(self, stream, part):
        pass

    def handleMeasure(self, stream, measure):
        pass

    def handleOtherThanMeasure(self, stream, other):
        pass

    def handleChord(self, measure, chord):
        pass

    def handleNote(self, measure, note):
        pass
    
    def handleChordOrNote(self, measure, item):
        pass

    def handleRest(self, measure, rest):
        pass

    def handleOtherThanNote(self, measure, other):
        pass

# This is best probably to be done in musescore
# as it does not 'redo' the measures like it would in the gui.
# Seems to involved to really want to impliment.
'''
class TimeSignatureChangeHandler(Music21Parser):
    def __init__(self, change_to):
        self._change_to = change_to

    def handleTimeSignature(self, measure, signature):
        new = TimeSignature(self._change_to)
        #self.replaceItem(measure, signature, new)
        measure.timeSignature = new
        for item in measure.makeNotation():
            print(item.offset, item.duration.quarterLength)
'''


class NoteSplitHandler(Music21Parser):

    def __init__(self, times=2, min_ql=float('inf')):
        self._times = times
        self._min_ql = min_ql

    def handleChordOrNote(self, measure, item):

        if item.duration.quarterLength < self._min_ql:
            return None

        old_off = item.offset #XXX this will go to zero after note is removed
        old_ql = item.duration.quarterLength
        ql = old_ql / self._times
        measure.remove(item)

        out = []
        for idx in range(self._times):
            new = self.cloneItem(item, quarterLength=ql)
            out.append(new)
            off = old_off + (ql * idx)
            measure.insert(off, new)
        return out


class SplitToDroneHandler(NoteSplitHandler):

    def __init__(self, drone, idx=0, min_ql=float('inf')):
        super().__init__(min_ql=min_ql)
        self._drone = drone
        self._idx = idx

    def handleChordOrNote(self, measure, item):
        new_items = super().handleChordOrNote(measure, item)
        if new_items is None:
            return
        target = new_items[self._idx]
        drone = self.cloneItem(Note(self._drone), quarterLength=target.duration.quarterLength)
        self.replaceItem(measure, target, drone)
        new_items[self._idx] = drone
        return new_items


class ChordifyHandler(Music21Parser):

    def __init__(self, chord_picker):
        self._chord_picker = chord_picker

    def handleNote(self, measure, note):
        pitches = self._chord_picker(note)
        if pitches is None:
            return
        l = []
        for pitch in pitches:
            d = Duration(note.duration.quarterLength)
            p = Pitch(pitch.nameWithOctave)
            n = Note(pitch)
            n.duration = d
            l.append(n)
        chord = Chord(l)
        self.replaceItem(measure, note, chord)
        return chord

class ClampPitchRangeHandler(Music21Parser):

    def __init__(self, lowPitchName, highPitchName):
        self._low = Pitch(lowPitchName)
        self._high = Pitch(highPitchName)

    def _findOctave(self, pitch, step):
        n  = 0
        p = Pitch(pitch)
        while True:
            if n > 12:
                raise ValueError(
                        f'no suitable pitch for {pitch} in bounds for {self._low}-{self._high}')
            p.octave += step
            inbounds = self._low <= p <= self._high
            if inbounds:
                return p
            n += 1

    def handleChordOrNote(self, measure, item):
        if item.isChord:
            l = item
        else:
            l = [item]
        for note in l:
            p = note.pitch
            if p < self._low:
                p = self._findOctave(p, 1)
            elif p > self._high:
                p = self._findOctave(p, -1)
            note.pitch = p
        return item

class ChromaticTransposeHandler(Music21Parser):

    def __init__(self, halfsteps):
        self._halfsteps = halfsteps
    
    def handleNote(self, measure, note):
        new  = note.transpose(self._halfsteps)
        print(11, note, new)
        self.replaceItem(measure, note, new)
        return new


if __name__ == '__main__':
    from music21.interval import ChromaticInterval
    #parser = ChromaticTransposeHandler(3)
    parser = Music21Parser() 
    stream = parser.open('data/shady_claw.abc')
    stream = parser.parse(stream)
    stream.show()

    #parser.write(stream.transpose(3), 'data/test.xml')

