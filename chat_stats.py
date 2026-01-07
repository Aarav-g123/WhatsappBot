# chat_stats.py
from collections import defaultdict, Counter
from typing import Dict, List

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
    by: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for m in msgs:
        day = m.ts.date().isoformat()
        by[m.author][day] += 1
    return by


COMMON_STOP = {
    "the","and","a","an","to","of","in","on","for","with","at","by","from",
    "is","am","are","was","were","be","been","being","do","does","did",
    "have","has","had","will","would","can","could","should","shall","may",
    "you","u","i","im","i'm","me","my","mine","we","our","ours",
    "he","she","it","they","them","their","theirs","his","her","hers",
    "this","that","these","those","here","there","then","than",
    "so","but","or","if","as","because","when","while","what","which","who",
    "how","why",
    "like","really","just","literally","kinda","sorta","maybe","probably",
    "thing","things","stuff","okay","ok","yeah","yep","nope",
}


def word_frequencies(msgs: List[Message]) -> Dict[str, Counter]:
    import re

    by: Dict[str, Counter] = defaultdict(Counter)

    for m in msgs:
        words = re.findall(r"[A-Za-z']+", m.text.lower())
        words = [w for w in words if w not in COMMON_STOP]
        by[m.author].update(words)

    return by


def sentiment_scores(msgs: List[Message]) -> Dict[str, Dict[str, float]]:
    from nltk.sentiment import SentimentIntensityAnalyzer

    sia = SentimentIntensityAnalyzer()
    sums = defaultdict(lambda: defaultdict(float))
    counts = defaultdict(int)

    for m in msgs:
        txt = m.text.strip()
        if not txt:
            continue
        vs = sia.polarity_scores(txt)
        sums[m.author]["Happiness"] += vs["pos"]
        sums[m.author]["Sadness"] += vs["neg"]
        sums[m.author]["Overall"] += vs["compound"]
        counts[m.author] += 1

    out = {}
    for author, comp in sums.items():
        n = counts[author] or 1
        avg = {k: v / n for k, v in comp.items()}
        max_val = max(abs(v) for v in avg.values()) or 1.0
        norm = {k: round(v / max_val, 3) for k, v in avg.items()}
        out[author] = norm
    return out


def confrontational_index(msgs: List[Message]) -> Dict[str, float]:
    from nltk.sentiment import SentimentIntensityAnalyzer

    sia = SentimentIntensityAnalyzer()
    sums = defaultdict(float)
    counts = defaultdict(int)

    for m in msgs:
        txt = m.text.strip()
        if not txt:
            continue
        vs = sia.polarity_scores(txt)
        negative_intensity = max(vs["neg"], -vs["compound"])
        sums[m.author] += negative_intensity
        counts[m.author] += 1

    out = {}
    for author, total in sums.items():
        n = counts[author] or 1
        out[author] = round(total / n, 3)
    return out


def pos_stats(
    msgs: List[Message], top_k: int = 10
) -> Dict[str, Dict[str, List[str]]]:
    import re
    import nltk

    by_author_tokens = defaultdict(list)

    for m in msgs:
        txt = m.text.strip()
        if not txt:
            continue
        tokens = nltk.word_tokenize(txt)
        tokens = [t.lower() for t in tokens if t.isalpha()]
        tokens = [t for t in tokens if t not in COMMON_STOP]
        by_author_tokens[m.author].extend(tokens)

    out: Dict[str, Dict[str, List[str]]] = {}

    for author, tokens in by_author_tokens.items():
        tagged = nltk.pos_tag(tokens)
        nouns = Counter()
        verbs = Counter()
        adjs = Counter()

        for word, tag in tagged:
            if tag.startswith("NN"):
                nouns[word] += 1
            elif tag.startswith("VB"):
                verbs[word] += 1
            elif tag.startswith("JJ"):
                adjs[word] += 1

        out[author] = {
            "nouns": [w for w, _ in nouns.most_common(top_k)],
            "verbs": [w for w, _ in verbs.most_common(top_k)],
            "adjectives": [w for w, _ in adjs.most_common(top_k)],
        }

    return out


def words_not_to_say(
    msgs: List[Message], min_total: float = 0.5
) -> Dict[str, List[str]]:
    import re
    from nltk.sentiment import SentimentIntensityAnalyzer

    sia = SentimentIntensityAnalyzer()
    word_scores = defaultdict(lambda: defaultdict(float))

    for m in msgs:
        txt = m.text.lower().strip()
        if not txt:
            continue
        vs = sia.polarity_scores(txt)
        neg_score = max(vs["neg"], -vs["compound"])
        if neg_score <= 0:
            continue
        words = re.findall(r"[A-Za-z']+", txt)
        words = [w for w in words if w not in COMMON_STOP]
        if not words:
            continue
        per_word = neg_score / len(words)
        for w in words:
            word_scores[m.author][w] += per_word

    out: Dict[str, List[str]] = {}
    for author, scores in word_scores.items():
        filtered = {w: s for w, s in scores.items() if s >= min_total}
        sorted_words = sorted(filtered.items(), key=lambda x: -x[1])
        out[author] = [w for w, _ in sorted_words]
    return out
