# 获取thread_id
curl --request POST \
  --url localhost:8000/threads \
  --header 'Content-Type: application/json' \
  --data '{}'

# 请求agent
curl --request POST \
    --url "localhost:8000/threads/919d8f39-7c37-44d0-9b5a-c9be9a00dbbc/runs/stream" \
    --header 'Content-Type: application/json' \
    --data '{
        "assistant_id": "asset_qa_agent",
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

  # asset_qa_agent
  curl --request POST \
    --url "localhost:8000/threads/919d8f39-7c37-44d0-9b5a-c9be9a00dbbc/runs/stream" \
    --header 'Content-Type: application/json' \
    --data '{
        "assistant_id": "asset_qa_agent",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": "互联互通资金累计流入情况如何？"
                }
            ]
        },
        "stream_mode": [
            "messages"
        ]
    }'