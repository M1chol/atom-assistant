from typing import Dict
import json


def get_json(text: str):
    if not text:
        return None
    start, end = None, None
    if text[0] == "{" and text[-1] == "}":
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


def build_message(config):
    if config["ollama_use_tools"]:
        tools = "NO TOOLS AVAILABLE"
        with open(config["ollama_function_file"]) as f:
            tools = f.read()
        with open(config["ollama_tool_message_file"]) as f:
            tools_message = f.read()

        tool_call_message = config["ollama_tool_use_encourage"] + tools + tools_message
        return tool_call_message, tools
    return "", None


def parse_func_call(text: str, tools: str, tools_obj: object) -> Dict[str, str] | None:
    try:
        parsed_text = get_json(text)
        if not parsed_text:
            return None
        parsed = json.loads(parsed_text)
    except:
        return None
    functions = json.loads(tools)
    for function in functions:
        try:
            if function["name"] not in parsed["name"]:
                continue
            if not hasattr(tools_obj, function["name"]):
                continue
            tool = getattr(tools_obj, function["name"])
            if not callable(tool):
                continue
            parameters = parsed.get("parameters", None)
            if parameters:
                try:
                    result = tool(**parameters)
                except Exception as e:
                    return {"error": str(e)}
                return result  # type: ignore
            else:
                try:
                    result = tool()
                except Exception as e:
                    return {"error": str(e)}
                return result  # type: ignore
        except:
            continue
    return None
