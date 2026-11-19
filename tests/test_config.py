import json
import re
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "config.json"


def test_config_has_the_values_the_daily_routine_reads():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert config["brand_id"] == 8209012
    assert config["timezone"] == "Asia/Calcutta"
    assert re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", config["post_time"])
    assert config["publish_mode"] in ("draft", "auto")
    assert isinstance(config["is_ai_generated"], bool)
    assert isinstance(config["reel_seconds"], int) and 5 <= config["reel_seconds"] <= 30
