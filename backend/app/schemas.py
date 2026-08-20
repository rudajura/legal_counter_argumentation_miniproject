from typing import Literal

from pydantic import BaseModel

Strength = Literal["low", "medium", "high"]


class Weakness(BaseModel):
    weakness: str
    description: str


class WeaknessesResponse(BaseModel):
    weaknesses: list[Weakness]
    full_fact_pattern: str


class CounterargumentsRequest(BaseModel):
    weaknesses: list[Weakness]
    full_fact_pattern: str
    argument: str


class CounterargumentItem(BaseModel):
    weakness: str
    counterargument: str
    strength: Strength
    reasoning: str


class AnalyzeResponse(BaseModel):
    summary: str
    items: list[CounterargumentItem]
