from ollama import chat, list
from datetime import datetime
import json
from typing import Dict
from pprint import pprint
import serial
from serial.tools import list_ports

# Checking if ollama is installed
try:
    list()
except ConnectionError as e:
    print(e)
    quit()

model = "gemma3:4b"

# Creating system message
system_prompt = 'Jesteś asystentem "Atom", odpowiadasz na pytania krótko, zwięźle oraz w języku polskim. Nie używaj znaków specjalnych\n'

tools = "NO TOOLS AVAILABLE"
with open("functions_servo.json") as f:
    tools = f.read()

tool_call = (
    f"""You have access to the following functions and are encouraged to use them when appropriate to fulfill user requests: {tools}
"""
    + """
**Function Invocation Guidelines:**

1.  **Prioritize Function Use:** If a user request can be best fulfilled or enhanced by using a function, you should invoke it.
2.  **Avoid Redundant Calls:** Do not call a function if its result is already present in a previous message.
3.  **Respond to Capability Inquiries:** If explicitly asked about your capabilities, list the functions you have access to.
4.  **Formatting:** When invoking a function, use the following message format: {"name": "function_name", "parameters": {"arg1": "value1", "arg2": "value2"}}
"""
)

SERVO_VID = 4292
SERVO_PID = 60000

serialServo = None


def openSerial() -> bool:
    global serialServo
    ports = list_ports.comports()
    for _port in ports:
        if _port.vid == SERVO_VID and _port.pid == SERVO_PID:
            serialServo = _port.device
    if not serialServo:
        print("[STEER] failed to find some hardware")
        return False
    serialServo = serial.Serial(
        serialServo, baudrate=115200, timeout=1, dsrdtr=False, rtscts=False
    )
    print("Servo connected")
    return True


openSerial()

# SERVO_FBK_FREQ_MS = 40
# def servoSetup() -> bool:
#     print("[STEER] Starting servo setup")
#     serialServo.reset_input_buffer()
#     serialServo.reset_output_buffer()
#     command = "BEG" + str()
#     serialServo.write(command.encode() + b"\n")
#     if not serialServo.readline():
#         print("[STEER] Servo setup failed")
#         return False
#     print("[STEER] Finished servo setup")
#     return True
#

messages = [
    {
        "role": "system",
        "content": system_prompt + tool_call,
    },
]

# def writeSerialServo(self) -> None:
#     print("[STEER] writeSerialServo worker started")
#     lastAngle = self._currentAngle
#     while not self._stopEvent.is_set():
#         if self._currentAngle != lastAngle:
#             command = f"CMD{self._currentAngle:.2f};{180 - self._currentAngle:.2f}"
#             self._serialServo.write(command.encode() + b"\n")
#         lastAngle = self._currentAngle
#         sleep(0.1)


# Tool definitions, function names and arguments need to match functions.json and return
# value must be of type Dictionary with at least one field "status" value of type string
class my_tools:
    # @staticmethod
    # def get_angle():
    #     try:
    #         return {"status": "success", "angle": None}
    #     except Exception as e:
    #         return {"status": "error", "angle": str(e)}

    @staticmethod
    def set_angle(angle: int):
        print(f"get_angle called with {angle}", angle)
        try:
            command = f"CMD{angle};{180 - angle}"
            serialServo.write(command.encode() + b"\n")
            return {"status": "success", "angle": angle}
        except ValueError as e:
            return {"status": "fail", "error": e}


my_tools_obj = my_tools()


def get_json(text: str):
    if not text:
        return None
    start, end = None, None
    if text[0] == "{":
        return text
    else:
        try:
            start = text.index("{")
            end = text.rfind("}") + 1
        except:
            return None
        if start and end:
            text = text[start:end]
            return text


def parse_func_call(text: str) -> Dict[str, str] | None:
    try:
        text = get_json(text)
        parsed = json.loads(text)
    except:
        return None
    functions = json.loads(tools)
    for function in functions:
        try:
            if function["name"] not in parsed["name"]:
                continue
            if not hasattr(my_tools_obj, function["name"]):
                continue
            tool = getattr(my_tools_obj, function["name"])
            if not callable(tool):
                continue
            parameters = parsed["parameters"]
            if parameters:
                result = tool(**parameters)
                return result  # type: ignore
            else:
                result = tool()
                return result  # type: ignore
        except:
            continue
    return None


print(f"Starting streamed chat with tools (servo) using {model}, Ctrl+C to exit")
try:
    while True:
        user_input = input("user: ")
        if user_input == "/logs":
            pprint(messages)
            continue
        messages.append({"role": "user", "content": user_input})
        streamed_response = []
        print("atom: ", end="")
        for part in chat(model, messages=messages, stream=True):
            streamed_response.append(part["message"]["content"])
            print(part["message"]["content"], end="", flush=True)
        response = "".join(streamed_response)
        function_result = parse_func_call(response)
        if function_result is not None:
            response_json = get_json(response)
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
                streamed_response.append(part["message"]["content"])
                print(part["message"]["content"], end="", flush=True)
        print("")
        messages.append({"role": "assistant", "content": response})


except KeyboardInterrupt:
    pass
