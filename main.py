from tts import ttsWrapper
from ollama import chat, list
import json

try:
    list()
except ConnectionError as e:
    print(e)
    quit()

with open("config.json") as f:
    config = json.load(f)

tts = ttsWrapper()

messages = [
    {
        'role': 'system',
        'content': config['ollama_system_prompt'],
    },
]

model = config['ollama_model_name']

try:
    print(f"Starting streamed chat (tts) with {model}, Ctrl+C to exit")
    while True:
        user_input = input("user: ")
        messages.append({'role': 'user', 'content': user_input})
        streamed_response = []
        print("atom: ", end='')
        for part in chat(model, messages=messages, stream=True):
            streamed_response.append(part['message']['content'])
            print(part['message']['content'], end='', flush=True)
        print("")
        response = ''.join(streamed_response)
        tts.speak(response)
        messages.append({'role': 'assistant', 'content': response})
except KeyboardInterrupt:
    pass