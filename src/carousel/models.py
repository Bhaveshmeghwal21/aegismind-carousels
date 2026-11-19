from dataclasses import dataclass, field


@dataclass(frozen=True)
class Slide:
    title: str
    body: str


@dataclass(frozen=True)
class Idea:
    date: str  # "2026-11-23"
    status: str  # "ready" or "needs-check"
    topic: str  # small label above the line on the image
    hook: str  # the line on the image
    caption: str
    slides: list[Slide] = field(default_factory=list)  # kept for a possible return to carousels; unused for now
