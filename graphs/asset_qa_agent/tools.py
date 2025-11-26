"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from collections.abc import Callable
from typing import Any
import math
import re

from langchain_chroma import Chroma
from langchain_core.tools import BaseTool, tool
from langchain_community.embeddings import DashScopeEmbeddings

from langgraph.runtime import get_runtime

from asset_qa_agent.context import Context

@tool
def financial_knowledge_search(query: str) -> str:
    """检索`query`相关的金融咨询

    Args:
        query: 用户提问的关于金融的问题
    """
    try:
        embeddings = DashScopeEmbeddings(
            model="text-embedding-v2",  # or other Qwen embedding models
            dashscope_api_key="sk-72fb5cc108ef4c52b08c549d25963bff"
        )
    except Exception as e:
        raise RuntimeError(
            "Failed to initialize OpenAIEmbeddings. Ensure the OpenAI API key is set."
        ) from e

    # Load the stored vector database
    chroma_db = Chroma(persist_directory="./vector_db/chroma_db", embedding_function=embeddings)
    retriever = chroma_db.as_retriever(search_kwargs={"k": 5})

    # Search the database for relevant documents
    documents = retriever.invoke(query)

    # Format the documents into a string
    context_str = "\n\n".join(doc.page_content for doc in documents)

    return context_str


# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b
