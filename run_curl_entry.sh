# 获取thread_id
curl --request POST \
  --url localhost:8100/threads/create \
  --header 'Content-Type: application/json' \
  --data '{}'

# 请求agent
curl --request POST \
    --url "localhost:8100/threads/7c8ff98f-666f-4320-ad50-a7d985ce4cc3/runs/stream" \
    --header 'Content-Type: application/json' \
    --data '{
        "assistant_id": "agent",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": "中国第一个皇帝是谁?"
                }
            ]
        },
        "stream_mode": [
            "updates"
        ]
    }'