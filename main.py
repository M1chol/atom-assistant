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
            response_part = part['message']['content']
            tts.speak(response_part)
            streamed_response.append(response_part)
            print(response_part, end='', flush=True)
        print("")
        messages.append({'role': 'assistant', 'content': ''.join(streamed_response)})
except KeyboardInterrupt:
    pass