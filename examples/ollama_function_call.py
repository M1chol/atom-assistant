from ollama import chat, list
from datetime import datetime
import json
from typing import Dict
from pprint import pprint

# Checking if ollama is installed
try:
    list()
except ConnectionError as e:
    print(e)
    quit()

model = 'gemma3:4b'
encourage_message = 'kontynuuj'

# Creating system message
system_prompt = 'Jesteś asystentem "Atom", odpowiadasz na pytania krótko, zwięźle oraz w języku polskim. Nie używaj znaków specjalnych\n'

tools = "NO TOOLS AVAILABLE"
with open("functions.json") as f:
    tools = f.read()

tool_call = f"""You have access to the following functions and are encouraged to use them when appropriate to fulfill user requests: {tools}
""" + """
**Function Invocation Guidelines:**

1.  **Prioritize Function Use:** If a user request can be best fulfilled or enhanced by using a function, you should invoke it.
2.  **Avoid Redundant Calls:** Do not call a function if its result is already present in a previous message.
3.  **Respond to Capability Inquiries:** If explicitly asked about your capabilities, list the functions you have access to.
4.  **Formatting:** When invoking a function, use the following JSON format: {"name": "function_name", "parameters": {"arg1": "value1", "arg2": "value2"}}
5.  **Be Truthfull:** When invoked function fail, clearly state that, or try to re-run the function
"""

messages = [
    {
        'role': 'system',
        'content': system_prompt + tool_call,
    },
]

# Tool definitions, function names and arguments need to match functions.json and return
# value must be of type Dictionary with at least one field "status" value of type string
class my_tools:
    @staticmethod
    def get_datetime():
        try:
            now = datetime.now()
            formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            return {"status": "success", "datetime": formatted_datetime}
        except Exception as e:
            return {"status": "error", "datetime": str(e)}
    
    @staticmethod
    def get_weekday(date: str):
        print("get_weekday called with parameter", date)
        format = "%Y-%m-%d"
        try:
            date_object = datetime.strptime(date, format)       
            weekday_name = date_object.strftime("%A")
            return {"status": "success", "weekday": weekday_name}
        except ValueError as e:
            return {"status": "fail", "error": e}

my_tools_obj = my_tools()

def get_json(text: str):
    if not text: return None
    start, end = None, None
    if text[0] == '{':
        return text
    else:
        try:
            start = text.index('{')
            end = text.rfind('}') + 1
        except:
            return None
        if start and end:
            text = text[start:end]
            return text


def parse_func_call(text: str) -> Dict[str, str] | None:
    try:
        get_json(text)
        parsed = json.loads(text)
    except:
        return None
    functions = json.loads(tools)
    for function in functions:
        try:
            if function['name'] not in parsed['name']:
                continue
            if not hasattr(my_tools_obj, function['name']):
                continue
            tool = getattr(my_tools_obj, function['name'])
            if not callable(tool):
                continue
            parameters = parsed['parameters']
            if parameters:
                result = tool(**parameters)
                return result #type: ignore
            else:
                result = tool()
                return result #type: ignore
        except:
            continue
    return None
    

print(f"Starting streamed chat with tools using {model}, Ctrl+C to exit")
try:
    while True:
        user_input = input("user: ")
        if user_input == "/logs":
            pprint(messages)
            continue
        messages.append({'role': 'user', 'content': user_input})
        streamed_response = []
        print("atom: ", end='')
        for part in chat(model, messages=messages, stream=True):
            streamed_response.append(part['message']['content'])
            print(part['message']['content'], end='', flush=True)
        response = ''.join(streamed_response)
        function_result = parse_func_call(response)
        if function_result is not None:
            response_json = get_json(response)
            if response_json:
                func_name = json.loads(response_json)['name']
            else:
                func_name = "unknown function"
            print(f"[SYSTEM] {func_name} called")
            messages[-1]['content'] += "\n" + func_name + " called. Result: " + str(function_result)[1:-1]
            # Respond again after getting the result
            print("atom: ", end='')
            for part in chat(model, messages=messages, stream=True):
                streamed_response.append(part['message']['content'])
                print(part['message']['content'], end='', flush=True)
        print("")
        messages.append({'role': 'assistant', 'content': response})


except KeyboardInterrupt:
    pass