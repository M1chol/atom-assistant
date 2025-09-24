import queue
import sys
import sounddevice as sd
import json

from vosk import Model, KaldiRecognizer

q = queue.Queue()
config = None
with open("config.json") as f:
    config = json.load(f)
if not config:
    raise FileNotFoundError("Conifg not found")

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


try:
    model = Model(lang="pl")
    samplerate = config['microphone_samplerate']
    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=sd.default.device,
            dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                print(rec.Result())
            else:
                print(rec.PartialResult())

except KeyboardInterrupt:
    print("\nDone")