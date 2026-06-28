"""Typed output contracts for each agent in the pipeline."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LocationContext:
    city: str
    country: Optional[str] = None
    region: Optional[str] = None
    activity: Optional[str] = None
    date_description: Optional[str] = None
    raw_input: str = ""


@dataclass
class WeatherContext:
    city_display: str
    temp_c: int = 0
    temp_f: int = 0
    condition: str = ""
    humidity: int = 0
    wind: str = ""
    error: Optional[str] = None


@dataclass
class SafetyContext:
    risk_level: str = "low"
    risk_reasons: list = field(default_factory=list)
    proceed_recommended: bool = True


@dataclass
class ActivityContext:
    recommendation: str = "go"
    best_time_window: Optional[str] = None
    gear_suggestions: list = field(default_factory=list)
    reasoning: str = ""
