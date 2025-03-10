import mido
import numpy as np
import pyaudio
import threading
import time
from scipy.signal import iircomb, lfilter, sawtooth, convolve
import matplotlib.pyplot as plt

# Constants for the audio
SAMPLE_RATE = 44100  # Samples per second
BUFFER_SIZE = 1024  # Buffer size for audio output
DURATION = 0.06  # Duration for each buffer (in seconds)

# MIDI Note to frequency map (A4 = 440Hz)
MIDI_NOTE_FREQUENCIES = {
    21: 27.5, 22: 29.14, 23: 30.87, 24: 32.7, 25: 34.65, 26: 36.71, 27: 38.89, 28: 41.2, 29: 43.65,
    30: 46.25, 31: 49.0, 32: 51.91, 33: 55.0, 34: 58.27, 35: 61.74, 36: 65.41, 37: 69.3, 38: 73.42, 39: 77.78,
    40: 82.41, 41: 87.31, 42: 92.5, 43: 98.0, 44: 103.83, 45: 110.0, 46: 116.54, 47: 123.47, 48: 130.81,
    49: 138.59, 50: 146.83, 51: 155.56, 52: 164.81, 53: 174.61, 54: 185.0, 55: 196.0, 56: 207.65, 57: 220.0,
    58: 233.08, 59: 246.94, 60: 261.63, 61: 277.18, 62: 293.66, 63: 311.13, 64: 329.63, 65: 349.23, 66: 369.99,
    67: 392.0, 68: 415.3, 69: 440.0, 70: 466.16, 71: 493.88, 72: 523.25, 73: 554.37, 74: 587.33, 75: 622.25,
    76: 659.26, 77: 698.46, 78: 739.99, 79: 783.99, 80: 830.61, 81: 880.0, 82: 932.33, 83: 987.77, 84: 1046.5,
    85: 1108.73, 86: 1174.66, 87: 1244.51, 88: 1318.51, 89: 1396.91, 90: 1480.0, 91: 1567.98, 92: 1661.22,
    93: 1760.0, 94: 1864.66, 95: 1975.53, 96: 2093.0
}

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, output=True, frames_per_buffer=BUFFER_SIZE)

# Shared variables
active_notes = {}  # To store active frequencies and their phase
controls = [0,0,0,0,0,0]  #stores the controls used for the various filters
vibrato_phase = 0
active_notes_lock = threading.Lock()  # Lock for thread safety

# Function to generate a sine wave for a given frequency
def generate_sine_wave(frequency, duration, sample_rate, phase_offset=0):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * frequency * t + phase_offset)

def generate_saw_wave(frequency, duration, sample_rate, phase_offset=0):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return sawtooth(2*np.pi*frequency*t + phase_offset)

# Function to generate combined waveform for active notes
def generate_waveform():
    with active_notes_lock:
        if not active_notes:
            return np.zeros(int(SAMPLE_RATE * DURATION))
        
        combined_waveform = np.zeros(int(SAMPLE_RATE * DURATION))
        for freq, phase in active_notes.items():
            if not controls[5]:
                waveform = generate_sine_wave(freq, DURATION, SAMPLE_RATE, phase)
            else:
                waveform = generate_saw_wave(freq, DURATION, SAMPLE_RATE, phase)
            combined_waveform += waveform
            # Update the phase for the next iteration
            active_notes[freq] = (phase + 2 * np.pi * freq * DURATION) % (2 * np.pi)
            combined_waveform = combined_waveform/(combined_waveform.max())
        combined_waveform = np.clip(combined_waveform, -1, 1)  # Ensure the waveform stays within valid audio range
        return combined_waveform

# Audio playback thread
def audio_playback_thread():
    while True:
        waveform = generate_waveform()  # Get the combined waveform for active notes
        if controls[4]: #Add Pitch Shift if needed
            waveform = pitch_shift(waveform, controls[4]*(0.122462) + 1)
        if controls[2]: #Add Chorus if needed
            waveform = chorus(waveform)
        if controls[1]: #Add Distortion if needed
            waveform *= (controls[1])*20
            waveform = np.clip(waveform, -1, 1)
        if controls[0]:#Add Vibrato if needed
            waveform = add_vibrato(waveform)
        if controls[3]: #Add reverb if needed
            waveform = bit_crush(waveform)

        samples = (waveform * 32767).astype(np.int16)  # Convert waveform to 16-bit PCM
        stream.write(samples.tobytes())  # Play the waveform

def pitch_shift(waveform, shift_factor):
    freq_domain = np.fft.fft(waveform)
    num_bins = len(freq_domain)
    
    indices = np.arange(num_bins)
    new_indices = indices * shift_factor
    magnitudes = np.abs(freq_domain)
    phases = np.angle(freq_domain)

    new_magnitudes = np.interp(indices,new_indices, magnitudes)
    new_phases = np.interp(indices,new_indices, phases)
    new_freq_domain = new_magnitudes * np.exp(1j * new_phases)
    
    # Perform the inverse FFT to get the shifted waveform
    shifted_waveform = np.fft.ifft(new_freq_domain)
    np.clip(shifted_waveform,-1,1)
    return shifted_waveform

def chorus(waveform):
    
    mix = controls[2]
    delayed_waveform = pitch_shift(waveform,1.01)
    delayed_waveform = np.roll(delayed_waveform,2000)
    delayed_waveform2 = pitch_shift(waveform,1.03)
    delayed_waveform2 = np.roll(delayed_waveform2,500)
    output_waveform = waveform * (1-mix) + delayed_waveform * (mix/2) + delayed_waveform2 * (mix/2)
    return output_waveform

def bit_crush(waveform):
   # Calculate the number of bits based on the knob value
    min_bits = 1  
    max_bits = 8
    bits = int(min_bits + (max_bits - min_bits) * (1-controls[3]))

    # Determine the number of quantization levels
    levels = 2 ** bits

    # Quantize the waveform
    quantized_waveform = np.round(waveform * (levels / 2)) / (levels / 2)

    return quantized_waveform

def add_vibrato(waveform):
    global vibrato_phase
    t = np.arange(len(waveform)) / SAMPLE_RATE
    vibrato_frequnecy = 2 ** (8*(controls[0]))
    lfo = 0.001 * np.sin(2 * np.pi * vibrato_frequnecy * t + vibrato_phase)
    vibrato_phase = (vibrato_phase + 2 * np.pi * DURATION * vibrato_frequnecy) % (2*np.pi)
    return np.interp(t + lfo, t, waveform)  # Interpolates the waveform to apply pitch shift
    
# MIDI processing thread
def midi_input_thread():
    global active_notes
    global controls
    try:
        with mido.open_input(mido.get_input_names()[1]) as midi_in:  # Adjust device index as needed
            for msg in midi_in:
                print(msg)
                if msg.type == 'note_on' and msg.velocity > 0:
                    with active_notes_lock:
                        frequency = MIDI_NOTE_FREQUENCIES.get(msg.note)
                        if frequency and frequency not in active_notes:
                            active_notes[frequency] = 0  # Add the note with initial phase 0
                elif msg.type == 'note_off':
                    with active_notes_lock:
                        frequency = MIDI_NOTE_FREQUENCIES.get(msg.note)
                        if frequency in active_notes:
                            del active_notes[frequency]  # Remove the note
                elif msg.type == 'control_change':
                    if msg.control == 1:
                        print("Not implemented yet")
                    elif msg.control == 64:
                        if msg.value == 127:
                            controls[5] = 1
                        else:
                            controls[5] = 0
                    else:
                        controls[msg.control-14] = msg.value/127
                elif msg.type =='pitchwheel':
                    controls[4] = msg.pitch/8192
                print(f"Notes Pressed: {list(active_notes.keys())}")
                print(f"Control Signals {list(controls)}")

    except Exception as e:
        print(f"Error in MIDI processing: {e}")

# Start threads
audio_thread = threading.Thread(target=audio_playback_thread, daemon=True)
audio_thread.start()

midi_thread = threading.Thread(target=midi_input_thread, daemon=True)
midi_thread.start()

# Main loop
try:
    while True:
        time.sleep(0.01)  # Keep main thread alive
except KeyboardInterrupt:
    print("Exiting...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
