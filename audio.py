import sounddevice as sd
import soundfile as sf

# basic setup for audio recording with sounddevice
sd.default.samplerate = 44100
sd.default.channels = 2

def record(duration, wait=False):
    samples = sd.rec(int(duration * sd.default.samplerate))
    if wait is True:
        sd.wait()
    return samples

def play(samples, wait=False):
    sd.play(samples)
    if wait is True:
        sd.wait()

def read(fname):
    samples, _ = sf.read(fname)
    return samples

def write(fname, samples):
    sf.write(fname, samples, sd.default.samplerate)

def stop():
    sd.stop()
