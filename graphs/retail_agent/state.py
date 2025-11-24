"""Define the state structures for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from langgraph.graph import START, END, MessagesState


class UserProfile:
    age: int
    risk_grd: str

class UserBehavior:
    buy_lc_list: list[str]
    buy_jj_list: list[str]

@dataclass
class RetailAgentState:
    # 用户信息
    user_id: str
    user_profile: UserProfile
    query: str

    # 意图分类
    user_intent: str

    # 推荐产品
    rec_list: str