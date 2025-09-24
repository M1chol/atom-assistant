from tts import ttsWrapper
from stt import sttWrapper
import sys
from ollama import chat, list
import json
from time import sleep

try:
    list()
except ConnectionError as e:
    print(e)
    quit()

with open("config.json") as f:
    config = json.load(f)

_current_line = ""
_run_prompt = False

def runner(text:str, run_prompt: bool):
    global _current_line
    global _run_prompt
    if _run_prompt: return
    clean = text.replace("\n", " ")
    pad_len = max(0, len(_current_line) - len(clean))
    pad = " " * pad_len
    sys.stdout.write("\ruser: " + clean + pad)
    if run_prompt:
        sys.stdout.write("\n")
        _run_prompt = True
    else: _current_line = clean
    sys.stdout.flush()


tts = ttsWrapper()
stt = sttWrapper(runner)

messages = [
    {
        'role': 'system',
        'content': config['ollama_system_prompt'],
    },
]

model = config['ollama_model_name']

try:
    print(f"Starting speach to speach chat with {model}, Ctrl+C to exit")
    while True:
        while not _run_prompt:
            sleep(0.01)
        messages.append({'role': 'user', 'content': _current_line})
        _current_line = ""
        streamed_response = []
        print("atom: ", end='')
        for part in chat(model, messages=messages, stream=True):
            response_part = part['message']['content']
            tts.speak(response_part)
            streamed_response.append(response_part)
            print(response_part, end='', flush=True)
        print("")
        tts.speak(None)
        messages.append({'role': 'assistant', 'content': ''.join(streamed_response)})
        _run_prompt = False

except KeyboardInterrupt:
    pass