from ollama import chat, list

# Checking if ollama is installed
try:
    list()
except ConnectionError as e:
    print(e)
    quit()

model = 'gemma3:4b'

messages = [
    {
        'role': 'system',
        'content': 'Jesteś asystentem "Atom", odpowiadasz krótko i zwięźle w języku polskim',
    },
]

try:
    print(f"Starting streamed chat with {model}, Ctrl+C to exit")
    while True:
        user_input = input("user: ")
        messages.append({'role': 'user', 'content': user_input})
        streamed_response = []
        print("atom: ", end='')
        for part in chat(model, messages=messages, stream=True):
            streamed_response.append(part['message']['content'])
            print(part['message']['content'], end='', flush=True)
        print("")
        messages.append({'role': 'assistant', 'content': ''.join(streamed_response)})
except KeyboardInterrupt:
    pass