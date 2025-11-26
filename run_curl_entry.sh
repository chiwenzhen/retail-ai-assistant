# 获取thread_id
#curl --request POST \
#  --url localhost:8100/threads/create \
#  --header 'Content-Type: application/json' \
#  --data '{}'
#
# 请求agent
curl --no-buffer --request POST \
    --url "localhost:8100/threads/runs/stream" \
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
        }
    }'

curl --request POST \
  --url "localhost:8100/threads/runs/wait" \
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
      }
  }'

