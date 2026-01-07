# chat_report.py
from typing import Dict


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def author_html(
    author: str,
    stats: Dict[str, float],
    daily_counts: Dict[str, int],
    top_words: Dict[str, int],
    sentiment: Dict[str, float],
    confront_score: float,
    pos_info: Dict[str, list],
    bad_words: list,
) -> str:
    days_sorted = sorted(daily_counts.items())
    labels = [d for d, _ in days_sorted]
    values = [c for _, c in days_sorted]

    labels_js = ",".join(f"'{d}'" for d in labels)
    values_js = ",".join(str(v) for v in values)

    words_sorted = sorted(top_words.items(), key=lambda x: -x[1])[:10]

    stats_rows = "".join(
        f"<tr><th>{_escape(k)}</th><td>{v}</td></tr>" for k, v in stats.items()
    )

    words_rows = "".join(
        f"<tr><td>{_escape(w)}</td><td>{c}</td></tr>" for w, c in words_sorted
    )

    emo_labels = ["Happiness", "Sadness", "Confrontational"]
    emo_values = [
        sentiment.get("Happiness", 0.0),
        sentiment.get("Sadness", 0.0),
        confront_score,
    ]
    emo_labels_js = ",".join(f"'{k}'" for k in emo_labels)
    emo_values_js = ",".join(str(v) for v in emo_values)

    nouns_list = ", ".join(_escape(w) for w in pos_info.get("nouns", []))
    verbs_list = ", ".join(_escape(w) for w in pos_info.get("verbs", []))
    adjs_list = ", ".join(_escape(w) for w in pos_info.get("adjectives", []))
    bad_list = ", ".join(_escape(w) for w in bad_words[:15])

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Chat analytics - {_escape(author)}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      margin: 0;
      background: #f5f5f7;
      color: #111827;
    }}
    header {{
      background: linear-gradient(135deg, #4f46e5, #6366f1);
      color: white;
      padding: 24px 32px;
      box-shadow: 0 2px 8px rgba(15,23,42,0.25);
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    h1 {{ margin: 0 0 4px 0; font-size: 28px; }}
    main {{
      max-width: 960px;
      margin: 24px auto 40px;
      padding: 0 16px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }}
    .card {{
      background: white;
      border-radius: 12px;
      padding: 16px 18px;
      box-shadow: 0 1px 3px rgba(15,23,42,0.12);
      border: 1px solid #e5e7eb;
    }}
    .card h2 {{
      margin: 0 0 12px 0;
      font-size: 18px;
      color: #111827;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      padding: 6px 8px;
      text-align: left;
      border-bottom: 1px solid #e5e7eb;
    }}
    th {{
      width: 55%;
      color: #4b5563;
      font-weight: 500;
    }}
    td {{
      color: #111827;
    }}
    .tag {{
      display: inline-flex;
      align-items: center;
      background: rgba(255,255,255,0.15);
      border-radius: 999px;
      padding: 2px 10px;
      font-size: 12px;
    }}
    canvas {{
      max-height: 260px;
    }}
    .note {{
      font-size: 12px;
      color: #6b7280;
      margin-bottom: 8px;
    }}
    .small-list {{
      font-size: 13px;
      color: #374151;
    }}
    .small-list span.label {{
      font-weight: 600;
      color: #111827;
    }}
  </style>
</head>
<body>
  <header>
    <div class="tag">Chat analytics</div>
    <h1>{_escape(author)}</h1>
    <div>Confrontational index: {confront_score}</div>
  </header>
  <main>
    <p class="note">
      Word stats exclude a curated list of common function and filler words.
    </p>
    <div class="grid">
      <section class="card">
        <h2>Overview</h2>
        <table>{stats_rows}</table>
        <p class="small-list">
          <span class="label">Common nouns:</span> {nouns_list}<br/>
          <span class="label">Common verbs:</span> {verbs_list}<br/>
          <span class="label">Common adjectives:</span> {adjs_list}
        </p>
      </section>
      <section class="card">
        <h2>Top words</h2>
        <table>
          <tr><th>Word</th><th>Count</th></tr>
          {words_rows}
        </table>
        <p class="small-list">
          <span class="label">Words not to say:</span> {bad_list}
        </p>
      </section>
    </div>

    <div class="grid">
      <section class="card">
        <h2>Messages over time</h2>
        <canvas id="dailyChart" height="80"></canvas>
      </section>
      <section class="card">
        <h2>Emotion profile</h2>
        <canvas id="sentChart" height="80"></canvas>
      </section>
    </div>
  </main>

  <script>
    const labels = [{labels_js}];
    const data = [{values_js}];

    const ctx = document.getElementById('dailyChart').getContext('2d');
    new Chart(ctx, {{
      type: 'line',
      data: {{
        labels: labels,
        datasets: [{{
          label: 'Messages per day',
          data: data,
          borderColor: '#4f46e5',
          backgroundColor: 'rgba(79,70,229,0.12)',
          borderWidth: 2,
          tension: 0.25,
          pointRadius: 2,
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          x: {{
            ticks: {{
              maxRotation: 45,
              minRotation: 45,
              autoSkip: true,
              maxTicksLimit: 12,
            }}
          }},
          y: {{
            beginAtZero: true,
            precision: 0,
          }}
        }},
        plugins: {{
          legend: {{ display: false }},
        }},
      }}
    }});

    const sentLabels = [{emo_labels_js}];
    const sentValues = [{emo_values_js}];
    const ctx2 = document.getElementById('sentChart').getContext('2d');
    new Chart(ctx2, {{
      type: 'radar',
      data: {{
        labels: sentLabels,
        datasets: [{{
          label: 'Normalised emotion + confrontation',
          data: sentValues,
          backgroundColor: 'rgba(239,68,68,0.12)',
          borderColor: '#ef4444',
          borderWidth: 2,
          pointBackgroundColor: '#ef4444',
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          r: {{
            beginAtZero: true,
            suggestedMax: 1,
          }}
        }},
        plugins: {{
          legend: {{ display: false }},
        }},
      }}
    }});
  </script>
</body>
</html>
"""
    return html


def write_html(path: str, html: str) -> None:
    with open(path, "w", encoding="utf8") as f:
        f.write(html)
