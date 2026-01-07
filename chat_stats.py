# chat_stats.py
from collections import defaultdict, Counter
from typing import Dict, List, Iterable

from chat_parser import Message


def basic_stats(msgs: List[Message]) -> Dict[str, Dict[str, float]]:
    by_author: Dict[str, List[Message]] = defaultdict(list)
    for m in msgs:
        by_author[m.author].append(m)

    msgs_sorted = sorted(msgs, key=lambda m: m.ts)

    gaps = [
        (msgs_sorted[i + 1].ts - msgs_sorted[i].ts).total_seconds()
        for i in range(len(msgs_sorted) - 1)
    ]
    median_gap = sorted(gaps)[len(gaps) // 2] if gaps else 0

    out: Dict[str, Dict[str, float]] = {}

    for author, lst in by_author.items():
        lst_sorted = sorted(lst, key=lambda m: m.ts)
        times = [m.ts for m in lst_sorted]

        silences = [
            (times[i + 1] - times[i]).total_seconds()
            for i in range(len(times) - 1)
        ]

        word_counts = [len(m.text.split()) for m in lst_sorted]

        # longest streak for this author in global order
        streak = 1
        max_streak = 1
        for i in range(1, len(msgs_sorted)):
            if (
                msgs_sorted[i].author == author
                and msgs_sorted[i - 1].author == author
            ):
                streak += 1
            else:
                max_streak = max(max_streak, streak)
                streak = 1
        max_streak = max(max_streak, streak)

        longest_silence_days = (
            max(silences, default=0) / 86400.0
        ) if silences else 0.0
        active_span_days = (
            (max(times) - min(times)).total_seconds() / 86400.0
            if times
            else 0.0
        )

        out[author] = {
            "Total messages": float(len(lst_sorted)),
            "Average words per message": round(
                sum(word_counts) / len(word_counts), 2
            )
            if word_counts
            else 0.0,
            "Longest silence (days)": round(longest_silence_days, 2),
            "Longest streak (messages)": float(max_streak),
            "Mid-conversation exits": float(
                sum(1 for g in silences if g > median_gap * 3)
            ),
            "Active span (days)": round(active_span_days, 2),
        }

    return out


def daily_activity(msgs: List[Message]) -> Dict[str, Dict[str, int]]:
    """Messages per day (YYYY-MM-DD) for each author."""
    by: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for m in msgs:
        day = m.ts.date().isoformat()
        by[m.author][day] += 1
    return by


def word_frequencies(
    msgs: List[Message],
    stopwords: Iterable[str] = (),
) -> Dict[str, Counter]:
    import re

    stops = set(w.lower() for w in stopwords)
    by: Dict[str, Counter] = defaultdict(Counter)

    for m in msgs:
        words = re.findall(r"[A-Za-z']+", m.text.lower())
        words = [w for w in words if w not in stops]
        by[m.author].update(words)

    return by
