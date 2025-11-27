#保存python镜像
docker save --platform=linux/amd64 -o python-3.11-slim-bookworm.tar python:3.11-slim-bookworm

#保存redis镜像
docker save --platform=linux/amd64 -o redis-7-alpine.tar redis:7-alpine

#保存postgres镜像
docker save --platform=linux/amd64 -o postgres-16-bookworm.tar postgres:16-bookworm

#保存retail-ai-assistant-aegra镜像
docker save --platform=linux/amd64 -o retail-ai-assistant-aegra.tar retail-ai-assistant-aegra:latest

#保存retail-ai-assistant-entry_server镜像
docker save --platform=linux/amd64 -o retail-ai-assistant-entry_server.tar retail-ai-assistant-entry_server:latest

