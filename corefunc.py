
import pickle
from music21 import converter, instrument, note, chord, midi, stream
import numpy as np
import time
from tensorflow.keras.models import load_model
import pickle
import numpy
from music21 import instrument, note, stream, chord


def prepare_sequences1(notes, pitchnames, n_vocab):
    """ Prepare the sequences used by the Neural Network """
    # map between notes and integers and back
    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))

    sequence_length = 50
    network_input = []
    output = []
    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])
        output.append(note_to_int[sequence_out])

    n_patterns = len(network_input)

    # reshape the input into a format compatible with LSTM layers
    normalized_input = numpy.reshape(network_input, (n_patterns, sequence_length, 1))
    # normalize input
    normalized_input = normalized_input / float(n_vocab)

    return (network_input, normalized_input)


def generate_notes(model, network_input, int_to_note, n_vocab, note_len):
    """ Generate notes from the neural network based on a sequence of notes """
    # pick a random sequence from the input as a starting point for the prediction
    start = numpy.random.randint(0, len(network_input)-1)

    

    pattern = network_input[start]
    prediction_output = []

    
    for note_index in range(note_len):
        prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(n_vocab)

        prediction = model.predict(prediction_input, verbose=0)

        index = numpy.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)

        pattern.append(index)
        pattern = pattern[1:len(pattern)]

    return prediction_output

def gen_midi(prediction_output, genre, instrmt):
    """ convert the output from the prediction to notes and create a midi file
        from the notes """
    offset = 0
    output_notes = []

    # create note and chord objects based on the values generated by the model
    for pattern in prediction_output:
        # pattern is a chord
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                new_note.storedInstrument = instrmt
                notes.append(new_note)
            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        # pattern is a note
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        # increase offset each iteration so that notes do not stack
        offset += 0.5

    midi_stream = stream.Stream(output_notes)

    midi_stream.write('midi', fp= genre+'_output.mid')

    return genre+'_output.mid'


def generate(genre, instr, duration):
    duration = int(duration)
    
    note_len = int( 250/63 * duration )
    print(genre)
    
    model = load_model('./encoding/rock/'+genre+'_model.h5')
    notes_dir = './encoding/' + genre + '/notes'
    
    '''
    if genre == 'pop':
        model = load_model('./encoding/pop/pop_model.h5')
        notes_dir = './encoding/pop/notes'
    '''    

    if instr == 'guitar':
        instrmt = instrument.ElectricGuitar()
    elif instr == 'violin':
        instrmt = instrument.Violin()
    elif instr == 'piano':
        instrmt = instrument.Piano()
    else:
        instrmt = instrument.BassDrum()

    with open(notes_dir, 'rb') as filepath:
        notes = pickle.load(filepath)

    # Get all pitch names
    pitchnames = sorted(set(item for item in notes))
    # Get all pitch names
    n_vocab = len(set(notes))

    #sa = time.time()
    network_input, normalized_input = prepare_sequences1(notes, pitchnames, n_vocab)
    int_to_note = dict((number, note) for number, note in enumerate(pitchnames))

    #print(time.time() - sa)    
    #sb = time.time()
    prediction_output = generate_notes(model, network_input, int_to_note, n_vocab, note_len)
    #print(time.time() - sb)

    #sc = time.time()
    retmd = gen_midi(prediction_output, genre, instrmt)

    #print(time.time() - sc)
    return retmd
    
