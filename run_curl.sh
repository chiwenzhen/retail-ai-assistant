# 获取thread_id
curl --request POST \
  --url localhost:8000/threads \
  --header 'Content-Type: application/json' \
  --data '{}'

# 请求agent
curl --request POST \
    --url "localhost:8000/threads/de6c6aec-0172-4b20-9d70-00743530dea8/runs/stream" \
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
            "messages"
        ]
    }'