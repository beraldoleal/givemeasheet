#!/usr/bin/env python
from flask import Flask
from flask import render_template
from flask import request

from random import randrange

from mingus.containers.Composition import Composition
from mingus.containers.Track import Track
from mingus.containers.Bar import Bar
from mingus.containers.Instrument import Piano, Guitar
from mingus.containers.Note import Note
from mingus.midi import MidiFileOut
import mingus.core.scales as scales
import mingus.extra.LilyPond as LilyPond

import uuid
import os

app = Flask(__name__)

def get_possibles(bar):
    possibles = []
    types = [1,2,4]
    for possible in types:
        if (1.0 / possible) <= bar.space_left():
            possibles.append(possible)
    return possibles
    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        meters = [(2,2), (2,4), (3,4), (4,4)]
        bars = int(request.form['bars'])
	key = keys[int(request.form['key'])]
        meter = meters[int(request.form['meter'])]
        scale = int(request.form['scale'])

        composition = Composition()
        composition.set_author("by givemeasheet.com", "admin@givemeasheet.com")
        composition.set_title("%d bars exercise in %s" % (bars, key))
        
        track = Track(Guitar())
       
        dificulty = 3
        if scale == 0:
            scale = scales.diatonic(key)
            scale_name = "Natural Major"
        elif scale == 1:
            scale = scales.natural_minor(key)
            scale_name = "Natural Minor"
        elif scale == 2:
            scale = scales.harmonic_minor(key)
            scale_name = "Minor Harmonic"
        elif scale == 3:
            scale = scales.melodic_minor(key)
            scale_name = "Minor Melodic"
        
        composition.subtitle = scale_name

        for bar in range(0,bars):
            bar = Bar(key, meter)
        
            while not bar.is_full():
                # Random note
                index = randrange(dificulty)
                note = Note(scale[index])
                possibles = get_possibles(bar)
                bar.place_notes(note, possibles[randrange(len(possibles))])
        
            track.add_bar(bar)
        
        composition.add_track(track)
        
        l = LilyPond.from_Composition(composition)
        u = uuid.uuid1()
        file_name = "/var/www/givemeasheet/givemeasheet/static/sheets/%s" % u.hex
        LilyPond.save_string_and_execute_LilyPond(l, file_name, "-fpng")
        sheet="/static/sheets/%s.png" % os.path.basename(file_name)
        midi="/static/sheets/%s.midi" % os.path.basename(file_name)
        MidiFileOut.write_Composition("%s.midi" % file_name, composition)

        return render_template('index.html', sheet=sheet, midi=midi)
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.debug = True
    app.run()
