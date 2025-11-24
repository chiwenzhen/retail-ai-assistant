# coding=utf-8
from datetime import UTC, datetime
from typing import Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime
from langchain.chat_models import init_chat_model

from prod_rec_agent.context import Context
from prod_rec_agent.state import InputState, State
from prod_rec_agent.utils import load_chat_model

def get_user_preference(state: State):
    user_id = state.user_id

    # 根据user_id获取用户信息
    user_profile="""
        客户年龄：35
        客户风险等级：中低风险
        客户日均流水：2000元
        客户AUM值：20万元
        客户最常持有周期：30天理财*3次，60天理财*1次
    """
    buy_history="""
        理财购买记录：浙银理财琮简涌金30天持有1号理财、浙银理财琮简涌金14天持有1号理财产品A、兴银理财添利天天利38号C
        基金购买记录：南方基金、华夏基金、易方达基金
        贵金属购买记录：岁岁昌龙、水月观音、招财进宝貔貅（男款）
    """

    return {
        "user_profile": user_profile,
        "buy_history": buy_history
    }

async def get_candidate_products(state: State):
    candidate_products = """
        产品代码    产品名称    风险等级    产品期限
        001 浙银理财琮简涌金30天持有1号理财     R2（中低风险）  最短持有30天
        002 浙银理财琮简涌金14天持有1号理财产品A    R2（中低风险）    最短持有14天
        003 浙银理财琮融九曜添利360天持有4号价值成长增强理财产品  R2（中低风险）  最短持有360天
        004 宁银理财宁欣固定收益类1个月定期开放式理财12号    R2（中低风险）    1个月
        005 兴银理财添利天天利19号X   R1（中低风险）    每日开放
        006 中邮理财-邮鸿宝1号G份额   R1（中低风险）    每日开放
    """
    return {
        "candidate_products": candidate_products
    }

async def call_model(
    state: State, runtime: Runtime[Context]
) -> dict[str, list[AIMessage]]:
    user_profile = state.user_profile
    buy_history = state.buy_history
    candidate_products = state.candidate_products
    model = init_chat_model(
        "qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key="sk-72fb5cc108ef4c52b08c549d25963bff"
    )
    system_message = runtime.context.system_prompt.format(
        system_time=datetime.now(tz=UTC).isoformat()
    )
    prompt = f"""
        任务描述：你是一个智能的银行财富产品推荐系统，需要根据用户画像和历史购买偏好信息，从候选产品列表中，推荐用户感兴趣的产品，并为每个产品生成推荐亮点，输出内容包括：序号、产品ID、产品名称、产品亮点。按照推荐力度从大到小，最多返回50个产品。
        用户画像和历史购买偏好：{user_profile} + {buy_history}
        候选财富产品列表：{candidate_products}
    """
    # Get the model's response
    response = cast(
        "AIMessage",
        await model.ainvoke(prompt),
    )

    return {"messages": [response]}

# Define a new graph
builder = StateGraph(State, input_schema=InputState, context_schema=Context)
builder.add_node("get_user_preference", get_user_preference)
builder.add_node("get_candidate_products", get_candidate_products)
builder.add_node("call_model", call_model)
builder.add_edge("__start__", "get_user_preference")
builder.add_edge("get_user_preference", "get_candidate_products")
builder.add_edge("get_candidate_products", "call_model")
graph = builder.compile(name="Prod Rec Agent")


