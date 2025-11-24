# coding=utf-8
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep


@dataclass
class InputState:
    user_id: str = field(default=None)
    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )

@dataclass
class State(InputState):
    user_profile: str = field(default="")
    buy_history: str = field(default="")
    candidate_products: str = field(default="")
    is_last_step: IsLastStep = field(default=False)
