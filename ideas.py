
# filters
sIter = s.iter()
restFilter = stream.filters.ClassFilter('Rest')
restIterator = sIter.addFilter(restFilter)
for el in restIterator:
    print(el, el.quarterLength)

sIter2 = s.iter()
offsetFilter = stream.filters.OffsetFilter(offsetStart=0.5, offsetEnd=4.0)
offsetIterator = sIter2.addFilter(offsetFilter)
for el in offsetIterator:
    print(el, el.offset)

#p.octave -= 1
#p.midi -= 6

# keys
#key = stream.analyze('key')
#print(key.correlationCoefficient)
#print(key.tonalCertainty())
#print(key.alternateInterpretations)

#plots
from music21 import graph
#stream.flatten().plot('pianoroll')
#pl = graph.plot.HistogramPitchSpace(stream) #with ocatve
#pl = graph.plot.HistogramPitchClass(stream) #without octave
pl = graph.plot.HistogramQuarterLength(stream)
pl.run()
pl.write(fp='tmp.png')
