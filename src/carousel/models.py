from dataclasses import dataclass


@dataclass(frozen=True)
class Idea:
    date: str  # "2026-11-23"
    status: str  # "ready" or "needs-check"
    quote: str  # the words on the image, without quotation marks
    author: str  # the thinker's name, shown under the quote
    source: str = ""  # work and translation, for the caption (and for checking)
    image: str = ""  # art id from assets/art/index.json; empty means pick one by date
    caption: str = ""  # a line or two of reflection
    tags: str = ""  # hashtags, shown last in the caption
    music: str = ""  # "Title — Artist" to search for in Instagram's music library; empty means no music
