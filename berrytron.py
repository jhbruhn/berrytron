import pygame
from pygame.midi import *
from pygame.locals import *

import os
from optparse import OptionParser

class NoteConverter:
    def __init__(self, base=5):
        self.base = base
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.notes = {}
        for note in range(128):
            name = names[note % 12]
            octave = int(note / 12) - base
            key = '%s%i' % (name, octave)
            self.notes[note] = key
            if octave == 0:
                self.notes[note] = name

    def __call__(self, note):
        return self.notes.get(str(note).upper(), note)

_sound_library = {}

def play_sound(path):
  global _sound_library
  sound = _sound_library.get(path)
  if sound == None:
    canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    sound = pygame.mixer.Sound(canonicalized_path)
    _sound_library[path] = sound
  sound.play()

def set_volume_sound(path, vol):
  global _sound_library
  sound = _sound_library.get(path)
  if sound == None:
    canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    sound = pygame.mixer.Sound(canonicalized_path)
    _sound_library[path] = sound
  sound.set_volume(vol)

def stop_sound(path):
  global _sound_library
  sound = _sound_library.get(path)
  if sound != None:
  	sound.fadeout(100)

parser = OptionParser("berrytron.py [options]")
parser.add_option("-i", "--instrument", default="brass", dest="instrument", help="Desired Instrument (see samples/ for all instruments)")
parser.add_option("-l", "--list-inputs", action="store_true", default=False, dest="list_inputs", help="List all available Midi-Inputs")
parser.add_option("-I", "--input", default=0, type="int", dest="input", help="The Midi-Input that should be used (list all via --list-inputs)") 
(options, args) = parser.parse_args() 

selected_instrument = options.instrument

pygame.mixer.pre_init(44100, -16, 1, 2048)

pygame.init()

pygame.midi.init()

if options.list_inputs:
	print "Available Midi Inputs:"
	for id in range(0, pygame.midi.get_count()):
		interf, name, input, output, opened = pygame.midi.get_device_info(id)
		if input == 1:
			print str(id) + ": " + name 
	pygame.midi.quit()
	pygame.quit()
	exit()

input_id = options.input
i = pygame.midi.Input(input_id)

note_converter = NoteConverter(1)

print "Berrytron started!"

running = True

try:
	while running:
		if i.poll():
			midi_events = i.read(10)
		
			midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

			for m_e in midi_evs:
				notename = note_converter.notes[m_e.data1]
			
				on  = m_e.status == 144
				off = m_e.status == 128
			
				sound_name = "samples/" + selected_instrument + "/" + notename + ".wav"
				set_volume_sound(sound_name, m_e.data2 / float(127))

				if on:
					play_sound(sound_name)
				else:
					stop_sound(sound_name)
except KeyboardInterrupt:
	print "Exiting Berrytron."
	del i
	pygame.midi.quit()
	pygame.quit()
	exit()
