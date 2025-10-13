from tts import ttsWrapper
from stt import sttWrapper
import sys
import model_tools
from ollama import chat, list, show
import json
from time import sleep
from datetime import datetime


# Note: functions should return {"status": <value>, "arg": <value>}
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


try:
    list()
except ConnectionError as e:
    print(e)
    quit()

with open("config.json") as f:
    config = json.load(f)

_current_line = ""
_run_prompt = False


def runner(text: str, run_prompt: bool):
    global _current_line
    global _run_prompt
    if _run_prompt:
        return
    clean = text.replace("\n", " ")
    pad_len = max(0, len(_current_line) - len(clean))
    pad = " " * pad_len
    sys.stdout.write("\ruser: " + clean + pad)
    if run_prompt:
        sys.stdout.write("\n")
        _run_prompt = True
    else:
        _current_line = clean
    sys.stdout.flush()


tts = ttsWrapper()
stt = sttWrapper(runner)

tool_call_message, tools = model_tools.build_message(config)

messages = [
    {
        "role": "system",
        "content": config["ollama_system_prompt"] + tool_call_message,
    },
]

model = config["ollama_model_name"]
try:
    show(model)
except:
    print("It looks like the ollama model you specified is not available")
    quit()

try:
    print(f"Starting speach to speach chat with {model}, Ctrl+C to exit")
    while True:
        while not _run_prompt:
            sleep(0.01)
        messages.append({"role": "user", "content": _current_line})
        _current_line = ""
        streamed_response = []
        print("atom: ", end="")
        for part in chat(model, messages=messages, stream=True):
            response_part = part["message"]["content"]
            tts.speak(response_part)
            streamed_response.append(response_part)
            print(response_part, end="", flush=True)
        if config["ollama_use_tools"]:
            response = "".join(streamed_response)
            if not tools:
                raise ValueError("tools empty")
            function_result = model_tools.parse_func_call(response, tools, my_tools)
            if function_result is not None:
                response_json = model_tools.get_json(response)
                if response_json:
                    func_name = json.loads(response_json)["name"]
                else:
                    func_name = "unknown function"
                print(f"[SYSTEM] {func_name} called")
                messages[-1]["content"] += (
                    "\n" + func_name + " called. Result: " + str(function_result)[1:-1]
                )
                # Respond again after getting the result
                print("atom: ", end="")
                for part in chat(model, messages=messages, stream=True):
                    response_part = part["message"]["content"]
                    streamed_response.append(response_part)
                    tts.speak(response_part)
                    print(part["message"]["content"], end="", flush=True)
        print("")
        tts.speak(None)
        messages.append({"role": "assistant", "content": "".join(streamed_response)})
        _run_prompt = False

except KeyboardInterrupt:
    pass
