from dataclasses import dataclass


@dataclass(frozen=True)
class Slide:
    title: str
    body: str


@dataclass(frozen=True)
class Idea:
    date: str  # "2026-11-23"
    status: str  # "ready" or "needs-check"
    topic: str
    hook: str
    slides: list[Slide]
    caption: str
