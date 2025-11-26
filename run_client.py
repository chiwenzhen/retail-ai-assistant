import asyncio
from langgraph_sdk import get_client, get_sync_client
import requests
import json
from typing import Any
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

async def main():
    # Connect to your self-hosted Aegra instance
    client = get_client(url="http://localhost:8000")

    # Create thread
    thread = await client.threads.create()
    thread_id = thread["thread_id"]

    # Stream responses (identical to LangGraph Platform)
    questions = [
        "中国第一个皇帝是谁？直接回答，不用解释。",
        "他的父亲是谁？直接回答，不用解释。",
        "请给我推荐一些理财产品",
    ]
    for question in questions:
        print("User:", end="")
        print(question)
        print("AI:", end="")

        stream = client.runs.stream(
            thread_id=thread_id,
            assistant_id="retail_agent",
            input={
                "messages": [
                    {"role": "user", "content": question}
                ]
            },
            stream_mode=["messages-tuple"],
            on_disconnect="cancel",
        )

        async for chunk in stream:
            if chunk.event != "messages":
                continue
            res = chunk.data[0]
            if res["type"] in ["AIMessageChunk", "ai"]:
                print(res["content"], end="")
        print()


def sync_main():
    # Connect to your self-hosted Aegra instance
    client = get_sync_client(url="http://localhost:8000")

    # Create thread
    thread = client.threads.create()
    thread_id = thread["thread_id"]

    # Stream responses (identical to LangGraph Platform)
    questions = [
        "中国第一个皇帝是谁？",
        "他的父亲是谁？",
    ]
    for question in questions:
        print("User:", end="")
        print(question)
        print("AI:", end="")

        response = client.runs.wait(
            thread_id=thread_id,
            assistant_id="agent",
            input={
                "messages": [
                    {"role": "user", "content": question}
                ]
            },
        )
        print(response["messages"][-1]["content"])

async def run_prod_rec_agent():
    # Connect to your self-hosted Aegra instance
    client = get_client(url="http://localhost:8000")

    # Create thread
    thread = await client.threads.create()
    thread_id = thread["thread_id"]

    # Stream responses (identical to LangGraph Platform)
    questions = [
        "请给我推荐一些理财产品",
    ]
    for question in questions:
        print("User:", end="")
        print(question)
        print("AI:", end="")

        stream = client.runs.stream(
            thread_id=thread_id,
            assistant_id="prod_rec_agent",
            input={"user_id": "123456"},
            stream_mode=["messages-tuple"],
            on_disconnect="cancel",
        )

        async for chunk in stream:
            if chunk.event != "messages":
                continue
            res = chunk.data[0]
            if res["type"] in ["AIMessageChunk", "ai"]:
                print(res["content"], end="")
        print()

async def run_prod_rec_agent_v2():
    # Connect to your self-hosted Aegra instance
    client = get_sync_client(url="http://localhost:8000")

    # Create thread
    thread = client.threads.create()
    thread_id = thread["thread_id"]

    # Stream responses (identical to LangGraph Platform)
    questions = [
        "请给我推荐一些理财产品",
    ]
    for question in questions:
        print("User:", end="")
        print(question)
        print("AI:", end="")

        stream = client.runs.stream(
            thread_id=thread_id,
            assistant_id="prod_rec_agent",
            input={"user_id": "123456"},
            stream_mode=["messages-tuple"],
            on_disconnect="cancel",
        )

        for chunk in stream:
            if chunk.event != "messages":
                continue
            res = chunk.data[0]
            if res["type"] in ["AIMessageChunk", "ai"]:
                print(res["content"], end="")
        print()

# asyncio.run(main())
# sync_main()
# asyncio.run(run_prod_rec_agent())

# client = get_sync_client(url='http://localhost:8000')
# thread = client.threads.create()
# thread_id = thread["thread_id"]
# data = {
#        "assistant_id": "agent",
#        "input": {
#            "messages": [
#                {
#                    "role": "user",
#                    "content": "中国第一个皇帝是谁？"
#                }
#            ]
#        },
#         "stream_mode": [
#             "messages"
#         ]
# }
# with requests.post(f"http://localhost:8000/threads/{thread_id}/runs/stream", data=json.dumps(data), stream=True) as res:
#     if res.status_code != 200:
#         print('error')
#     for line in res.iter_lines(decode_unicode=True, chunk_size=65535):
#         if not line.startswith("data:"):
#             continue
#         line = line.replace("data:", "")
#         obj = json.loads(line)
#         if not isinstance(obj, list):
#             continue
#         langgraph_node = obj[1]["langgraph_node"]
#         message_content = obj[0]["content"]
#         if langgraph_node in ["call_model"]:
#             print(message_content, end="")
#     print()



# class AgentRequest(BaseModel):
#     thread_id: str = ""
#     assistant_id: str
#     input: dict[str, Any]
#     config: dict[str, Any] | None = {}
#     context: dict[str, Any] | None = {}
#     user_id: str = ""
# request = AgentRequest(assistant_id="agent", input={"message":[{"type":"human", "content": "hello world"}]})
# print(request.model_dump(mode='json'))
#
# request = AgentRequest(assistant_id="agent", input={"messages":[{"role":"user", "content": "中国第一个皇帝是谁?"}]})
# AEGRA_URL = "http://localhost:8000"
# client = get_sync_client(url=AEGRA_URL)
# thread = client.threads.create()
# thread_id = thread["thread_id"]
# data=request.model_dump(mode='json')
# with requests.post(f"{AEGRA_URL}/threads/{thread_id}/runs/stream", data=data,
#                    stream=True) as res:
#     if res.status_code != 200:
#         print('error')
#     for line in res.iter_lines(decode_unicode=True, chunk_size=65535):
#         if not line.startswith("data:"):
#             continue
#         line = line.replace("data:", "")
#         obj = json.loads(line)
#         if not isinstance(obj, list):
#             continue
#         langgraph_node = obj[1]["langgraph_node"]
#         message_content = obj[0]["content"]
#         if langgraph_node in ["call_model"]:
#             print(message_content)

# data = {
#        "assistant_id": "agent",
#        "input": {
#            "messages": [
#                {
#                    "role": "user",
#                    "content": "中国第一个皇帝是谁？"
#                }
#            ]
#        }
# }
# with requests.post(f"http://localhost:8100/threads/runs/stream", data=json.dumps(data), stream=True) as res:
#     if res.status_code != 200:
#         print('error')
#     for line in res.iter_lines(decode_unicode=True, chunk_size=65535):
#         print(line)

AEGRA_URL = "http://localhost:8000"
class AgentRequest(BaseModel):
    thread_id: str = None
    assistant_id: str
    input: dict[str, Any]
    config: dict[str, Any] | None = {}
    context: dict[str, Any] | None = {}
    user_id: str = None
request = AgentRequest(assistant_id="agent", input={"messages":[{"role":"user", "content": "中国第一个皇帝是谁?"}]})
print(request.model_dump(mode='json'))

client = get_sync_client(url=AEGRA_URL)
thread_id = request.thread_id
if thread_id is None:
    thread = client.threads.create()
    thread_id = thread["thread_id"]

stream = client.runs.stream(
    thread_id=thread_id,
    assistant_id=request.assistant_id,
    input=request.input,
    stream_mode=["messages-tuple"],
)

for chunk in stream:
    if chunk.event != "messages":
        continue
    res = chunk.data[0]
    if res["type"] in ["AIMessageChunk", "ai"]:
        # yield {"content": res["content"]}
        print(res["content"])