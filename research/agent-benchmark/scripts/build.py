import argparse
import json
import sys
from collections import defaultdict
from html import escape
from pathlib import Path
from statistics import mean, median

HERE = Path(__file__).resolve().parents[1]
START = "<!-- benchmark:tables -->"
END = "<!-- /benchmark:tables -->"
MIN_RUNS = 5
EFFORTS = {"low": 0, "medium": 1, "high": 2, "xhigh": 3, "max": 4, None: 5}


def load(folder, name):
    path = folder / "data" / name
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def known(rows, measure):
    return [
        r["measures"].get(measure)
        for r in rows
        if r["measures"].get(measure) is not None
    ]


def share(values):
    if not values:
        return "–"
    hits = sum(1 for v in values if v)
    return f"{hits}/{len(values)} ({round(100 * hits / len(values))}%)"


def number(value, digits=1):
    if value is None:
        return "–"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def mid(values):
    values = [v for v in values if v is not None]
    return median(values) if values else None


def label(rows):
    return f"{len(rows)}" if len(rows) >= MIN_RUNS else f"{len(rows)} †"


def group(rows, keys):
    cells = defaultdict(list)
    for row in rows:
        cells[tuple(row.get(k) for k in keys)].append(row)

    def order(item):
        key, cell = item
        return tuple(
            (EFFORTS.get(v, 9), "") if k == "effort" else (0, str(v or "~"))
            for k, v in zip(keys, key)
        ) + ((-len(cell),),)

    return sorted(cells.items(), key=order)


def table(header, lines):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in line) + " |" for line in lines]
    return "\n".join(out) + "\n"


def show(value):
    return "–" if value is None else str(value)


def per_task(cell):
    first = {}
    for row in cell:
        first.setdefault(row["task"] or ("run", row["run"]), row)
    return list(first.values())


def writer_lines(rows, keys):
    lines = []
    for key, cell in group(rows, keys):
        tasks = per_task(cell)
        rounds = known(tasks, "rounds_to_pass")
        tokens = mid([r["tokens"] for r in cell])
        lines.append(
            [show(v) for v in key]
            + [
                label(cell),
                len(tasks),
                share(known(tasks, "landed")),
                share([v == 1 for v in rounds]),
                number(float(mean(rounds)), 2) if rounds else "–",
                share(known(tasks, "landing_ci_first_pass")),
                sum(1 for v in known(tasks, "third_fail_stop") if v),
                number(mid([r["minutes"] for r in cell])),
                "–" if tokens is None else f"{tokens / 1000:.0f}k",
                sum(r["usage_limit_hits"] or 0 for r in cell),
            ]
        )
    return lines


WRITER_HEADER = [
    "runs",
    "tasks",
    "landed",
    "passed round 1",
    "mean rounds to pass",
    "landing CI first pass",
    "third-fail stops",
    "median minutes",
    "median tokens",
    "limit hits",
]


def reviewer_lines(rows, keys):
    lines = []
    for key, cell in group(rows, keys):
        verdicts = [r["outcome"] for r in cell if r["outcome"] in ("pass", "fail")]
        blockers = sum(r["measures"].get("blockers") or 0 for r in cell)
        false = sum(
            r["measures"].get("false_blockers") or 0
            for r in cell
            if r["measures"].get("blockers") is not None
        )
        lines.append(
            [show(v) for v in key]
            + [
                label(cell),
                share([v == "pass" for v in verdicts]),
                share(known(cell, "miss")),
                f"{false}/{blockers}" if blockers else "–",
                number(mid([r["minutes"] for r in cell])),
            ]
        )
    return lines


def council_lines(rows, keys):
    lines = []
    for key, cell in group(rows, keys):
        votes = [r["outcome"] for r in cell if r["outcome"] in ("SHIP", "NOT YET")]
        lines.append(
            [show(v) for v in key]
            + [
                label(cell),
                share([v == "SHIP" for v in votes]),
                share(known(cell, "matched_ruling")),
                share(known(cell, "ship_overturned")),
            ]
        )
    return lines


def landing_lines(rows):
    weeks = defaultdict(list)
    for row in rows:
        weeks[row["day"]].append(row)
    lines = []
    for day, cell in sorted(weeks.items()):
        lines.append(
            [
                day,
                len(cell),
                share([r["result"] == "success" for r in cell]),
                number(mid([r["minutes"] for r in cell])),
                number(mid([r["queue_minutes"] for r in cell])),
                number(mid([r["train_size"] for r in cell])),
            ]
        )
    return lines


def bar_chart(title, bars, unit):
    width, left, row = 640, 170, 26
    height = 50 + row * len(bars)
    top = max((v for _, v, _ in bars), default=1) or 1
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="sans-serif" font-size="12">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
        f'<text x="12" y="22" font-size="14" font-weight="bold">{escape(title)}</text>',
    ]
    for i, (name, value, note) in enumerate(bars):
        y = 40 + i * row
        length = (width - left - 120) * value / top
        parts += [
            f'<text x="{left - 8}" y="{y + 14}" text-anchor="end">{escape(name)}</text>',
            f'<rect x="{left}" y="{y + 2}" width="{length:.1f}" height="16" fill="#4C78A8"/>',
            f'<text x="{left + length + 6:.1f}" y="{y + 14}" fill="#3B3B3B">'
            f"{value:.0f}{unit} {escape(note)}</text>",
        ]
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def charts(runs):
    writers = [r for r in runs if r["role"] == "writer"]
    landed, minutes = [], []
    for (model,), cell in group(writers, ["model"]):
        if model is None:
            continue
        values = known(per_task(cell), "rounds_to_pass")
        if len(values) >= MIN_RUNS:
            landed.append(
                (
                    model,
                    100 * sum(v == 1 for v in values) / len(values),
                    f"(n={len(values)} tasks)",
                )
            )
        spent = mid([r["minutes"] for r in cell])
        if spent is not None and len(cell) >= MIN_RUNS:
            minutes.append((model, spent, f"(n={len(cell)})"))
    landed.sort(key=lambda b: -b[1])
    minutes.sort(key=lambda b: b[1])
    return {
        "charts/writer-first-pass.svg": bar_chart(
            "Writer tasks that passed review in round 1, by model", landed, "%"
        ),
        "charts/writer-minutes.svg": bar_chart(
            "Median writer run length, by model", minutes, " min"
        ),
    }


def summary(runs, landings):
    roles = defaultdict(int)
    for row in runs:
        roles[row["role"]] += 1
    days = sorted({r["day"] for r in runs if r["day"]})
    writers = [r for r in runs if r["role"] == "writer"]
    joined = known(writers, "rounds_to_pass")
    span = f"{days[0]} to {days[-1]}" if days else "no dated runs"
    return (
        f"{len(runs)} agent runs ({span}): "
        + ", ".join(f"{n} {role}" for role, n in sorted(roles.items()))
        + f". {len(joined)} of {len(writers)} writer runs have a known review outcome. "
        f"{len(landings)} landing CI runs.\n"
    )


def build(folder):
    runs = load(folder, "runs.jsonl")
    landings = load(folder, "landings.jsonl")
    writers = [r for r in runs if r["role"] == "writer"]
    reviewers = [r for r in runs if r["role"] == "reviewer"]
    council = [r for r in runs if r["role"] == "council seat"]
    others = [r for r in runs if r["role"] in ("researcher", "planner", "fixer")]
    note = (
        f"† fewer than {MIN_RUNS} runs: read as an anecdote, not a rate. "
        "– means no observation.\n\n"
    )
    files = {
        "tables/writers.md": "# Writers by model and effort\n\n"
        + note
        + table(
            ["model", "effort", *WRITER_HEADER],
            writer_lines(writers, ["model", "effort"]),
        ),
        "tables/writers-by-task.md": "# Writers by model, effort and task type\n\n"
        + note
        + table(
            ["task type", "model", "effort", *WRITER_HEADER],
            writer_lines(writers, ["task_type", "model", "effort"]),
        ),
        "tables/reviewers.md": "# Reviewers by model, effort and tier\n\n"
        + note
        + table(
            [
                "model",
                "effort",
                "tier",
                "runs",
                "verdict pass",
                "missed a defect",
                "false blockers",
                "median minutes",
            ],
            reviewer_lines(reviewers, ["model", "effort", "tier"]),
        ),
        "tables/council.md": "# Council seats by model and effort\n\n"
        + note
        + table(
            [
                "model",
                "effort",
                "votes",
                "voted SHIP",
                "matched final ruling",
                "SHIP later overturned",
            ],
            council_lines(council, ["model", "effort"]),
        ),
        "tables/harness.md": "# Runs by harness and model\n\n"
        + note
        + table(
            [
                "harness",
                "model",
                "runs",
                "median minutes",
                "limit hits",
                "failed or interrupted",
            ],
            [
                [
                    show(h),
                    show(m),
                    label(cell),
                    number(mid([r["minutes"] for r in cell])),
                    sum(r["usage_limit_hits"] or 0 for r in cell),
                    sum(
                        1
                        for r in cell
                        if r["outcome"] in ("failed", "interrupted", "cancelled")
                    ),
                ]
                for (h, m), cell in group(runs, ["harness", "model"])
            ],
        ),
        "tables/other-roles.md": "# Researchers, planners and fixers\n\n"
        + note
        + table(
            [
                "role",
                "model",
                "effort",
                "runs",
                "claims failed / checked",
                "stops caused",
            ],
            [
                [
                    show(role),
                    show(m),
                    show(e),
                    label(cell),
                    f"{sum(r['measures'].get('claims_failed') or 0 for r in cell)}/"
                    f"{sum(r['measures'].get('claims_checked') or 0 for r in cell)}",
                    sum(r["measures"].get("stops_caused") or 0 for r in cell),
                ]
                for (role, m, e), cell in group(others, ["role", "model", "effort"])
            ],
        ),
        "tables/landings.md": "# Landing CI by day\n\n"
        + table(
            [
                "day",
                "runs",
                "first pass",
                "median minutes",
                "median queue minutes",
                "median train size",
            ],
            landing_lines(landings),
        ),
    }
    files.update(charts(runs))
    block = (
        summary(runs, landings)
        + "\n"
        + note
        + "### Writers\n\n"
        + table(
            ["model", "effort", *WRITER_HEADER],
            writer_lines(writers, ["model", "effort"]),
        )
        + "\n### Reviewers\n\n"
        + table(
            [
                "model",
                "effort",
                "runs",
                "verdict pass",
                "missed a defect",
                "false blockers",
                "median minutes",
            ],
            reviewer_lines(reviewers, ["model", "effort"]),
        )
        + "\n![Writer tasks that passed review in round 1](charts/writer-first-pass.svg)\n\n"
        + "![Median writer run length](charts/writer-minutes.svg)\n\n"
        + "More tables: [writers by task type](tables/writers-by-task.md), "
        "[reviewers by tier](tables/reviewers.md), [council](tables/council.md), "
        "[harness](tables/harness.md), [other roles](tables/other-roles.md), "
        "[landing CI](tables/landings.md).\n"
    )
    readme = folder / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        if START in text and END in text:
            head, rest = text.split(START, 1)
            files["README.md"] = (
                head + START + "\n" + block + END + rest.split(END, 1)[1]
            )
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild the agent benchmark tables and charts from data/ alone."
    )
    parser.add_argument(
        "--check", action="store_true", help="fail if any output is stale"
    )
    parser.add_argument("--folder", type=Path, default=HERE, help=argparse.SUPPRESS)
    args = parser.parse_args()
    stale = []
    for name, text in build(args.folder).items():
        path = args.folder / name
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == text:
            continue
        stale.append(name)
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    if args.check and stale:
        sys.exit("stale: " + ", ".join(stale) + " (run: python scripts/build.py)")


if __name__ == "__main__":
    main()
