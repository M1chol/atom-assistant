from openai import OpenAI
from openaikey import apiKey
from datetime import datetime
client = OpenAI(api_key=apiKey)

thread = client.beta.threads.create()

while True:
    message_content = input("user: ")
    if message_content == "exit": break
    message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=message_content
    )

    run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id="asst_PbYXMz2StCR4wC5Jiq5ZbDdN",
    )

    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print("atom:", list(messages)[0].content[0].text.value)
    
    elif run.status == "requires_action":
        tool_outputs = []
        
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "music-on":
                print("system: music-on wywołane dla", tool.function.arguments)
                tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "ok"
                })
            elif tool.function.name == "music-off":
                print("system: music-off wywołane")
                tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "ok"
                })
            elif tool.function.name == "get-date":
                print("system: get-date wywołane")
                tool_outputs.append({
                "tool_call_id": tool.id,
                "output": datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
                })

        if tool_outputs:
            try:
                run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
                )
            except Exception as e:
                print("system: błąd podczas przekazania funkcji", e)
            
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            print("atom:", list(messages)[0].content[0].text.value)
    else:
        print(run.status)