import tempfile
import os

from music21_parser import Music21Parser


class Logger: #TODO add real logger
    def debug(self, msg):
        print(msg)
logger = Logger()


class Sequencer:

    class TransposeHandler(Music21Parser):
        def __init__(self, halfsteps):
            self._halfsteps = halfsteps
        def parse(self, stream):
            return stream.transpose(self._halfsteps)

    def __init__(self):
        self._handlers = []

    def addHandler(self, handler):
        if handler.data_kind is None:
            raise ValueError(f'data_kind attribute must set for {handler}')
        self._handlers.append(handler)

    def sequence(self, in_fname, out_fname, 
            transpose=0,
            keep_scratch_files=False,
        ):
        def isThereMore(i):
            return len(self._handlers) > i+1

        # we dont want to permantly change handlers for method options
        handlers = self._handlers[:]
        if transpose:
            handlers.insert(0, self.TransposeHandler(transpose))

        first_fname = in_fname # keep track of the first file name
        last_kind = None
        last_out = None
        for idx, handler in enumerate(handlers):
            # if first or data is incompatible we need a scratch file
            if last_kind != handler.data_kind:
                data = handler.open(in_fname)

            data = handler.parse(data)

            # if were on the last one use the given filename
            if handler is self._handlers[-1]:
                out = out_fname
            # else create a scratch file for chaining
            else:
                #XXX we may not alway need to write but we need to know next handler
                out = tempfile.NamedTemporaryFile().name + '.musicxml' #FIXME This needs to be thought out better!

            # remove intermediate file
            if last_out and last_out != first_fname and not keep_scratch_files:
                os.remove(last_out)

            handler.write(data, out)
            logger.debug(f'parsed {in_fname} with {handler.__class__.__name__} to {out}')

            last_kind = handler.data_kind
            last_out = out
            in_fname = out

        return out_fname


if __name__ == '__main__':

        from music21_parser import SplitToDroneHandler
        from xml_parser import InstrumentHandler
        from xml_parser import ClefHandler
        from xml_parser import ClefHandler
        from xml_parser import ArpeggioHandler
        from banjo import ClawHammerHandler

        sequencer = Sequencer()
        '''
        sequencer.addHandler(SplitToDroneHandler('e3', idx=0, min_ql=1))
        sequencer.addHandler(InstrumentHandler('Organ', 'Og.'))
        sequencer.sequence('data/merry_it_is.xml', 'data/test.xml',
                keep_scratch_files=False,
                )
        '''

        sequencer.addHandler(ClawHammerHandler('g3', 'g4', min_ql=1))
        sequencer.addHandler(InstrumentHandler('Banjo', 'Bj.'))
        sequencer.addHandler(ClefHandler(octave_change=-1))
        sequencer.addHandler(ArpeggioHandler())
        sequencer.sequence('data/shady.abc', 'data/test2.xml',
                transpose=-2-12, # A->G then down an octave
                keep_scratch_files=False,
                )

