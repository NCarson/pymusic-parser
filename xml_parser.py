import uuid
import xml.etree.ElementTree as ET

from abstract_parser import AbstractParser

class MusicXmlParser(AbstractParser):

    data_kind = 'music_xml'

    def write(self, root, fname):
        b_xml = ET.tostring(root)
        with open(fname, "wb") as f:
            f.write(b_xml)

    def open(self, fname):
        iterator = ET.iterparse(fname)
        # XXX we have to iterate through once to get the root element materialized
        #     then we can keep re-using root. iterator gets only one go ;/
        for kind, el, in iterator:
            pass
        return iterator.root

    def _toCamel(self, name):
        l = []
        capitalize = True
        for letter in name:
            if letter == '-':
                capitalize = True
                continue
            if capitalize:
                letter = letter.upper()
                capitalize = False
            l.append(letter)

        return ''.join(l)

    def _init(self):
        self._last_note = None
        self._chord_notes = []

    def parse(self, root):

        self._init()
        for el in root.iter():

            if el.tag == 'measure':
                self._init()
            if el.tag == 'note':
                self._handleNote(el)

            name = 'handle' + self._toCamel(el.tag)
            if hasattr(self, name):
                getattr(self, name)(el)
        return root


    def _handleNote(self, note):
        # XXX 
        #   we need a lot of logic as chord is a self closing tag in the second note!!!!
        #   That makes SENSE!!! DumbASSES

        chord_found = False
        for item in note:
            if item.tag == 'chord':
                if not self._chord_notes:
                    self._chord_notes.append(self._last_note)
                    self._chord_notes.append(note)
                    chord_found = True
                else:
                    self._chord_notes.append(note)

        if not chord_found:
            if self._chord_notes:
                self.handleChord(self._chord_notes) 
                self._chord_notes = []

        self._last_note = note


    def handleChord(self, notes):
        pass


class ClefHandler(MusicXmlParser):

    def __init__(self, octave_change=0):
        super().__init__()
        self._octave_change = octave_change

        '''
        <clef>
          <sign>G</sign>
          <line>2</line>
          <clef-octave-change>-1</clef-octave-change>
        </clef>
        '''

    def handleClef(self, clef):

        if not self._octave_change:
            return

        for item in clef:
            if item.tag == 'clef-octive-change':
                clef.remove(item)

        change = ET.SubElement(clef, 'clef-octave-change')
        change.text = str(self._octave_change)


class InstrumentHandler(MusicXmlParser):

    def __init__(self, name, abbr=''):
        super().__init__()
        self._name = name
        self._abbr = abbr

        '''
        <part-name>Banjo</part-name>
        <part-abbreviation>Bj.</part-abbreviation>
        <score-instrument id="P1-I1">
          <instrument-name>Banjo</instrument-name>
        </score-instrument>
        '''

    def handleScorePart(self, score_part):

        remove = ['part-name', 'part-abbreviation', 'score-instrument', 'intrument-name']
        for el in score_part:
            if el.tag in remove:
                score_part.remove(el)

        partname = ET.SubElement(score_part, 'part-name') #XXX BUG: Musescore does not seem to want to update this unless you change the instrument your self in the staff part config window. The proper names are showed in the config window. The behavior is the same when changing the text with the gui changing the instrument name label.
        partname.text = self._name
        partname.set('print-object', 'yes')
        if self._abbr:
            abbr = ET.SubElement(score_part, 'part-abbreviation')
            abbr.text = self._abbr
        inst = ET.SubElement(score_part, 'score-instrument')
        # make xml happy with id type
        id = 'a' + str(uuid.uuid4())
        inst.set('id', id)

        name = ET.SubElement(inst, 'instrument-name')
        name.text = self._name


class ArpeggioHandler(MusicXmlParser):

    def handleChord(self, notes):
        for note in notes:
            el = ET.SubElement(note, 'notations')
            ET.SubElement(el, 'arpeggiate')



if __name__ == '__main__':
    pass
