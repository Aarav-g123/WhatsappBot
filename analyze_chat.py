# analyze_chat.py
from pathlib import Path

from chat_parser import parse_chat
from chat_stats import (
    basic_stats,
    daily_activity,
    word_frequencies,
    sentiment_scores,
    confrontational_index,
    pos_stats,
    words_not_to_say,
)
from chat_report import author_html, write_html


def main():
    msgs = parse_chat("chat.txt")
    if not msgs:
        print("No messages parsed.")
        return

    stats_by_author = basic_stats(msgs)
    daily_by_author = daily_activity(msgs)
    words_by_author = word_frequencies(msgs)
    sentiment_by_author = sentiment_scores(msgs)
    confront_by_author = confrontational_index(msgs)
    pos_by_author = pos_stats(msgs)
    bad_words_by_author = words_not_to_say(msgs)

    out_dir = Path("chat_reports")
    out_dir.mkdir(exist_ok=True)

    for author, stats in stats_by_author.items():
        daily_counts = daily_by_author.get(author, {})
        top_words = dict(words_by_author.get(author, {}))
        sent = sentiment_by_author.get(author, {})
        confront_score = confront_by_author.get(author, 0.0)
        pos_info = pos_by_author.get(author, {"nouns": [], "verbs": [], "adjectives": []})
        bad_words = bad_words_by_author.get(author, [])

        html = author_html(
            author,
            stats,
            daily_counts,
            top_words,
            sent,
            confront_score,
            pos_info,
            bad_words,
        )

        safe_name = "".join(
            c if c.isalnum() or c in ("-", "_") else "_" for c in author
        )
        file_path = out_dir / f"{safe_name}.html"
        write_html(file_path, html)
        print(f"Wrote {file_path}")


if __name__ == "__main__":
    main()
