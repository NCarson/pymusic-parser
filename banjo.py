from music21_parser import Music21Parser
from music21_parser import ClampPitchRangeHandler
from music21_parser import SplitToDroneHandler
from music21_parser import ChordifyHandler
from xml_parser import MusicXmlParser
from xml_parser import InstrumentHandler
from xml_parser import ClefHandler
from xml_parser import ArpeggioHandler
from strings import FiveStringBanjo


class ClawHammerHandler(Music21Parser):

    def __init__(self, drone1, drone2, min_ql=float('inf')):

        # we want all the pitches to inclusively between the low and high drone
        self.clamp = ClampPitchRangeHandler(drone1, drone2)
        # our first split will halve the note and add a drone
        self.split1 = SplitToDroneHandler(drone1, idx=0, min_ql=min_ql)
        # our second split will end up quartering the remaining note and add a drone
        self.split2 = SplitToDroneHandler(drone2, idx=-1, min_ql=min_ql/2)

        # old time banjo likes to play custom tuning where you
        # can usually play open strings with perhaps one string noted
        banjo = FiveStringBanjo.fromNamedTuning('modal_g')
        def pickChord(note):
            # clawhammer style usually uses the first three strings for a brush (strum)
            use = [1,2,3]
            pitches = banjo.pitchesFromNote(note, use_strings=use)
            return pitches
        #pitchesFromNote will find the noted string and return the three pitches
        self.chordify = ChordifyHandler(pickChord)

    def handleChordOrNote(self, measure, item):

        result = self.clamp.handleChordOrNote(measure, item)
        # our first split
        result = self.split1.handleChordOrNote(measure, result)
        if not result:
            return
        # the first drone
        first = result[0]
        # the note is in the second half of the split
        result = self.split2.handleChordOrNote(measure, result[-1])
        # the last drone
        last = result[-1]
        # our quartered note. we want to change to it a chord
        target = result[0]
        if not target.isChord:
            result = self.chordify.handleNote(measure, target)
            result = self.clamp.handleChordOrNote(measure, result)
            second = result

        # we need to add beams or this will look really sloppy
        if first.duration.quarterLength <= 1.5:
            first.beams.append('start')
            second.beams.append('continue')
            last.beams.append('stop')
        return [first, second, last]


class BanjoHandler(MusicXmlParser):
        
        def parser(self, root):
            inst = InstrumentHandler('Banjo', 'Bj.')
            clef = ClefHandler(octave_change=-1)
            arp = ArpeggioHandler()

            root = inst.parse(root)
            root = clef.parse(root)
            root = arp.parse(root)

            return root


if __name__ == '__main__':
    from sequencer import Sequencer

    sequencer = Sequencer()
    sequencer.addHandler(ClawHammerHandler('g3', 'g4', min_ql=1))
    # you could also subclass Sequencer as 'BanjoSequencer' but I think 
    # this gives you better abstraction without having to call super() too much.
    sequencer.addHandler(BanjoHandler())
    sequencer.sequence('data/shady2.abc', 'data/modified.xml', 
        transpose=3-12) # transpose from e -> g and then down an octive


