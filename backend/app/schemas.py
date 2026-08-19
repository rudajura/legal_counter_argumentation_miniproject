from typing import Literal

from pydantic import BaseModel

Strength = Literal["low", "medium", "high"]


class CounterargumentItem(BaseModel):
    weakness: str
    counterargument: str
    strength: Strength
    reasoning: str


class AnalyzeResponse(BaseModel):
    summary: str
    items: list[CounterargumentItem]
