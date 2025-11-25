import asyncio
from langgraph_sdk import get_client, get_sync_client

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

# asyncio.run(main())
# sync_main()
asyncio.run(run_prod_rec_agent())