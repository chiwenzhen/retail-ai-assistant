import logging
from langchain.chat_models import init_chat_model
from langgraph.graph import START, END, MessagesState, StateGraph
from typing import TypedDict, Literal
from langgraph.types import interrupt, Command, RetryPolicy
from langchain.messages import AIMessage
logger = logging.getLogger(__name__)

# Define the nodes
intent_llm = init_chat_model(
    "qwen3-max",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-72fb5cc108ef4c52b08c549d25963bff",
    disable_streaming=True
)

llm = init_chat_model(
    "qwen3-max",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-72fb5cc108ef4c52b08c549d25963bff"
)

class UserProfile:
    age: int
    risk_grd: str

class UserBehavior:
    buy_lc_list: list[str]
    buy_jj_list: list[str]

class RetailAgentState(MessagesState):
    # 用户信息
    user_id: str
    user_profile: UserProfile
    query: str

    # 意图分类
    user_intent: str

    # 推荐产品
    rec_list: str

def classify_intent(state: RetailAgentState) -> Command[Literal["qa", "prod_rec", "prod_detail", "prod_diff"]]:
    print(f"running classify_intent")

    # 意图识别prompt
    last_question = state["messages"][-1].content
    classify_intent_prompt = f"""
    请分析用户输入的Query，将其意图分类到这三类：
    1.财富产品推荐：当用户让你推荐财富产品时，包括储蓄存款、理财、基金、资管、保险、贵金属、柜台债、国债等等
    2.财富产品详情：当用户让你咨询某款具体的财富产品时，包括储蓄存款、理财、基金、资管、保险、贵金属、柜台债、国债等等
    3.财富产品对比：当用户让你对比两款具体的财富产品差异时，包括储蓄存款、理财、基金、资管、保险、贵金属、柜台债、国债等等
    4.其他：其他问题时触发
    要求：只能输出[财富产品推荐, 财富产品详情, 财富产品查询, 财富产品对比, 其他]之中的一个，不得输出其他内容。
    Query: {last_question}
    """
    logger.info(f"classify_intent_prompt= {classify_intent_prompt}")
    # Get structured response directly as dict
    user_intent = intent_llm.invoke(classify_intent_prompt).content
    logger.info(f"user_intent= {user_intent}")
    if user_intent == "财富产品推荐":
        goto = "prod_rec"
    elif user_intent == "财富产品详情":
        goto = "prod_detail"
    elif user_intent == "财富产品对比":
        goto = "prod_diff"
    elif user_intent == "其他":
        goto = "qa"
    else:
        goto = "qa"
    print(f'last_question={last_question}\nuser_intent={user_intent}')
    return Command(
        update={"user_intent": user_intent},
        goto=goto
    )

# Define the chat node
def qa(state: RetailAgentState):
    print(f"running qa")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Define the chat node
def prod_rec(state: RetailAgentState):
    print(f"running prod_rec")
    rec_list = "产品推荐列表\n1.product1\n2.product2\n3.product3"
    return {"rec_list": rec_list, "messages": [AIMessage(content=rec_list)]}

def prod_detail(state: RetailAgentState):
    print(f"running prod_detail")
    rec_list = "产品详情:xxxxx"
    return {"rec_list": rec_list, "messages": [AIMessage(content=rec_list)]}

def prod_diff(state: RetailAgentState):
    print(f"running prod_diff")
    rec_list = "产品对比:产品A: bla bla bla, 产品B: bla bla bla"
    return {"rec_list": rec_list, "messages": [AIMessage(content=rec_list)]}

# Build and compile graph
builder = StateGraph(RetailAgentState)
builder.add_node("classify_intent", classify_intent)
builder.add_node("qa", qa)
builder.add_node("prod_rec", prod_rec)
builder.add_node("prod_detail", prod_detail)
builder.add_node("prod_diff", prod_diff)
builder.add_edge(START, "classify_intent")
builder.add_edge("prod_rec", END)
builder.add_edge("prod_detail", END)
builder.add_edge("prod_diff", END)
builder.add_edge("qa", END)
graph = builder.compile(name="Retail Agent")