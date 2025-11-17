from __future__ import annotations
from typing import List, Literal, Optional, TypedDict, Any, Dict
from pydantic import BaseModel, Field


class PastStep(BaseModel):
    action: str
    input: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    summary: Optional[str] = None


class AgentState(BaseModel):
    goal: str = Field(description="The agent's mission")
    ticker: Optional[str] = Field(default=None, description="Asset ticker, e.g., BTC or BTC-USD")
    data_points: List[Dict[str, Any]] = Field(default_factory=list, description="Raw OHLCV or computed indicator data")
    current_action: Optional[str] = Field(default=None, description="Next command, e.g., FETCH_DATA, CALCULATE_RSI, FINISH")
    past_steps: List[PastStep] = Field(default_factory=list, description="Log of actions and results")


# For LangGraph, we can define a TypedDict as the underlying state container.
class StateDict(TypedDict, total=False):
    goal: str
    ticker: str
    data_points: List[Dict[str, Any]]
    current_action: str
    past_steps: List[Dict[str, Any]]


def to_state_dict(model: AgentState) -> StateDict:
    return model.model_dump()


def from_state_dict(d: StateDict) -> AgentState:
    return AgentState.model_validate(d)
