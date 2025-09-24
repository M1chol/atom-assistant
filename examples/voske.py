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

_current_line = ""

def runner(text:str, run_prompt: bool):
    global _current_line
    global _run_prompt
    clean = text.replace("\n", " ")
    pad_len = max(0, len(_current_line) - len(clean))
    pad = " " * pad_len
    sys.stdout.write("\ruser: " + clean + pad)
    if run_prompt:
        sys.stdout.write("\n")
        _current_line = ""
        _run_prompt = True
    else: _current_line = clean
    sys.stdout.flush()

try:
    model = Model(lang=config["stt_config"]['model'])
    samplerate = config["stt_config"]['microphone_samplerate']
    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=sd.default.device,
            dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())['text']
                if result.strip():
                    runner(result, True)
            else:
                partial = json.loads(rec.PartialResult())['partial']
                if partial.strip():
                    runner(partial, False)

except KeyboardInterrupt:
    print("\nDone")