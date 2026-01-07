# chat_parser.py
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List

TIME_RE = re.compile(
    r'^(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s*[AP]M) - (.*?): (.*)$'
)


@dataclass
class Message:
    ts: datetime
    author: str
    text: str


def parse_chat(path: str) -> List[Message]:
    msgs: List[Message] = []

    with open(path, encoding="utf8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            m = TIME_RE.match(line)
            if not m:
                # continuation of previous message
                if msgs:
                    msgs[-1].text += "\n" + line
                continue

            d, t, author, txt = m.groups()

            # skip system / media / deleted
            if author.startswith("Messages and calls are"):
                continue
            if txt.startswith("<") and txt.endswith(">"):
                continue
            if "message was deleted" in txt:
                continue

            # handle narrow no‑break spaces in exported times
            t_norm = t.replace("\u202f", " ").strip()
            ts = datetime.strptime(f"{d} {t_norm}", "%m/%d/%y %I:%M %p")

            msgs.append(Message(ts=ts, author=author, text=txt))

    return msgs
