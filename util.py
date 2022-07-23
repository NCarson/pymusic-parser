from copy import deepcopy

from music21.note import Note
from music21.duration import Duration
from music21.pitch import Pitch


def iterNotes(items):
    for item in items:
        if not hasattr(item, 'isChord'):
            continue

        if item.isChord:
            for note in item.notes:
                yield (note, item)
        else:
            yield (item, None)


def pitchesToChord(pitches):
    notes = [Note(p) for p in pitches]
    return Chord(notes)


class ChordOrNote:
    def __init__(self, measure, item):
        self._measure = measure
        self._item = item
        self._orig_offset = item.offset
        self._ql = item.quarterLength

    @property
    def measure(self): return self._measure

    @property
    def ql(self): return self._ql

    @property
    def orig_offset(self): return self._orig_offset

    @property
    def item(self): return self._item

    def clone(self, offset=None, pitch_name=None, duration_fact=None):
        if self.item.isChord:
            new = self._cloneChord(self.item, offset, pitch_name, duration_fact)
        else:
            new = self._cloneNote(self.item, offset, pitch_name, duration_fact)
        return new

    def replace(self, item):
        self.measure.remove(self.item)
        self.measure.insert(self.orig_offset, item)
        item.offset = self.orig_offset
        item.duration = Duration(self.ql)


    def _cloneChord(self, chord, offset=None, pitch_name=[], duration_fact=1):
        c =  Chord()
        for idx, note in enumerate(chord):
            if pitch_name:
                p = pitch_name[idx]
            else:
                p = None
            d = note.duration.quarterLength * duration_fact
            new = self._cloneNote(note, pitch_name=p, duration_fact=d)
            c.add(new)
        d = chord.duration.quarterLength * duration_fact
        c.quarterLength = d

        return c

    def _cloneNote(self, note, offset=None, pitch_name=None, duration_fact=1):
        d = note.duration.quarterLength * duration_fact
        if pitch_name is not None:
            p = pitch_name
        else:
            p = note.nameWithOctave

        if offset == None:
            o = note.offset
        else:
            o = offset

        note = Note(pitchName=p, duration=Duration(d))
        note.offset = o
        return note

