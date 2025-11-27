#保存python镜像
docker save -o python-3.11-slim-bookworm.tar python:3.11-slim-bookworm

#保存redis镜像
docker save -o redis-7-alpine.tar redis:7-alpine

#保存postgres镜像
docker save -o postgres-16-bookworm.tar postgres:16-bookworm

#保存retail-ai-assistant-aegra镜像
docker save -o retail-ai-assistant-aegra.tar retail-ai-assistant-aegra:latest

#保存retail-ai-assistant-entry_server镜像
docker save -o retail-ai-assistant-entry_server.tar retail-ai-assistant-entry_server:latest

