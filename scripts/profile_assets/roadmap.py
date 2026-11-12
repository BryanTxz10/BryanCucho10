"""Gantt-style roadmap rendered as a terminal window."""
from datetime import date, timedelta

from . import theme as t

WIDTH, X0, X1 = 1040, 300, 1010
ROW = 24


def _bar(x, y, width, status, color, delay):
    solid = status in ("shipped", "active", "in_progress", "done")
    grow = (f'<animate attributeName="width" values="0;0;{width:.1f}" '
            f'keyTimes="0;{delay / (delay + 0.6):.3f};1" dur="{delay + 0.6:.2f}s" fill="freeze"/>')
    pulse = ('<animate attributeName="fill-opacity" values="1;0.55;1" dur="1.6s" '
             'repeatCount="indefinite"/>' if status in ("active", "in_progress") else "")
    return (
        f'<rect x="{x:.1f}" y="{y - 6}" width="{width:.1f}" height="12" rx="4" fill="{color}" '
        f'fill-opacity="{1 if solid else 0.28}" stroke="{color}">{grow}{pulse}</rect>'
    )


def render(data, today):
    start = date.fromisoformat(data["timeline"]["start"])
    end = date.fromisoformat(data["timeline"]["end"])
    span = (end - start).days

    def x_of(day):
        return X0 + (day - start).days / span * (X1 - X0)

    feat = data["featured"]
    groups = [
        ("PROJECTS", [
            (f'{p["id"]} ', p.get("short", p["title"]), p, t.STATUS[p["status"]][0])
            for p in [feat] + data["projects"] + data["extras"]
        ]),
        ("CERTIFICATIONS", [("◆ ", c["name"], c, t.PURPLE) for c in data["certifications"]]),
    ]

    command, _ = t.prompt(66, "./roadmap --gantt", "roadmap")
    parts = [t.window(WIDTH, 0, "bryan@archlinux: ~/roadmap"), command]  # height patched below

    # Axis: year labels, study-period band, month initials.
    rows_top = 150
    rows = sum(len(items) + 1 for _, items in groups)
    rows_bottom = rows_top + rows * ROW
    axis = [f'<text x="{X0}" y="92" font-size="11" fill="{t.DIM}">{start.year}</text>']
    for year in range(start.year + 1, end.year + 1):
        x = x_of(date(year, 1, 1))
        if x < X1 - 30:
            axis.append(f'<line x1="{x:.1f}" y1="84" x2="{x:.1f}" y2="{rows_bottom}" '
                        f'stroke="{t.BORDER}" stroke-dasharray="2 4"/>'
                        f'<text x="{x + 5:.1f}" y="92" font-size="11" fill="{t.DIM}">{year}</text>')
    for i, phase in enumerate(data["phases"]):
        a = x_of(date.fromisoformat(phase["start"]))
        b = x_of(date.fromisoformat(phase["end"]) + timedelta(days=1))
        axis.append(
            f'<rect x="{a:.1f}" y="100" width="{b - a:.1f}" height="22" rx="4" fill="{t.BLUE}" '
            f'fill-opacity="{0.14 if i % 2 else 0.24}" stroke="{t.BLUE}" stroke-opacity="0.5"/>'
            f'<text x="{(a + b) / 2:.1f}" y="115" text-anchor="middle" font-size="10.5" '
            f'font-weight="700" fill="{t.TEXT}">{t.esc(phase["label"])}</text>')
    month = start.replace(day=1)
    while month < end:
        nxt = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
        mid = (x_of(max(month, start)) + x_of(min(nxt, end))) / 2
        axis.append(f'<text x="{mid:.1f}" y="138" text-anchor="middle" font-size="9" '
                    f'fill="{t.DIM}">{month.strftime("%b")[0]}</text>')
        month = nxt
    parts.append("".join(axis))

    # Rows.
    y, delay = rows_top + ROW / 2, 0.4
    for title, items in groups:
        parts.append(f'<text x="30" y="{y + 4}" font-size="11" font-weight="700" fill="{t.DIM}" '
                     f'letter-spacing="1">{title}</text>')
        y += ROW
        for prefix, name, item, color in items:
            a = max(x_of(date.fromisoformat(item["start"])), X0)
            b = min(x_of(date.fromisoformat(item["end"]) + timedelta(days=1)), X1)
            due = f'{date.fromisoformat(item["end"]):%b ’%y}'
            due_w = t.text_width(due, 10)
            if b + 8 + due_w <= X1:
                due_x, anchor = b + 8, "start"
            else:
                due_x, anchor = a - 8, "end"
            parts.append(
                f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="{t.BORDER}" stroke-opacity="0.45"/>'
                f'<text x="30" y="{y + 4}" font-size="12.5" fill="{t.TEXT}" xml:space="preserve">'
                f'<tspan fill="{color}" font-weight="700">{t.esc(prefix)}</tspan>{t.esc(name)}</text>'
                + _bar(a, y, b - a, item["status"], color, delay)
                + t.fade_in(f'<text x="{due_x:.1f}" y="{y + 3.5}" text-anchor="{anchor}" font-size="10" '
                            f'fill="{t.DIM}">{due}</text>', delay + 0.5)
            )
            y += ROW
            delay += 0.12

    # Today marker (moves on every scheduled rebuild).
    now_x = x_of(min(max(today, start), end))
    parts.append(
        f'<line x1="{now_x:.1f}" y1="96" x2="{now_x:.1f}" y2="{rows_bottom + 8}" stroke="{t.ORANGE}" '
        f'stroke-width="1.5" stroke-dasharray="4 3"/>'
        f'<circle cx="{now_x:.1f}" cy="96" r="3.5" fill="{t.ORANGE}"/>'
        f'<circle cx="{now_x:.1f}" cy="96" r="3.5" fill="none" stroke="{t.ORANGE}">'
        f'<animate attributeName="r" values="3.5;11" dur="1.8s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;0" dur="1.8s" repeatCount="indefinite"/></circle>'
    )
    tag = f"TODAY · {today:%b} {today.day}"
    tag_w = t.text_width(tag, 10) + 16
    tag_x = min(max(now_x - tag_w / 2, X0), X1 - tag_w)
    parts.append(
        f'<rect x="{tag_x:.1f}" y="{rows_bottom + 8}" width="{tag_w:.1f}" height="18" rx="9" fill="{t.ORANGE}"/>'
        f'<text x="{tag_x + tag_w / 2:.1f}" y="{rows_bottom + 20.5}" text-anchor="middle" font-size="10" '
        f'font-weight="700" fill="{t.BG}">{tag}</text>'
    )

    # Legend + closing prompt.
    legend_y = rows_bottom + 52
    legend, lx = [], 30
    for color, opacity, text in ((t.GREEN, 1, "active / shipped"), (t.YELLOW, 1, "in progress"),
                                 (t.BLUE, 0.28, "planned"), (t.PURPLE, 0.28, "certification")):
        legend.append(
            f'<rect x="{lx}" y="{legend_y - 9}" width="18" height="10" rx="3" fill="{color}" '
            f'fill-opacity="{opacity}" stroke="{color}"/>'
            f'<text x="{lx + 25}" y="{legend_y}" font-size="11" fill="{t.MUTED}">{text}</text>')
        lx += 25 + t.text_width(text, 11) + 26
    parts.append("".join(legend))
    closing, cx = t.prompt(legend_y + 34, "", "roadmap")
    parts.append(closing + t.cursor(cx, legend_y + 34))

    height = legend_y + 58
    parts[0] = t.window(WIDTH, height, "bryan@archlinux: ~/roadmap")
    names = ", ".join(f'{p.get("short", p["title"])} ({t.STATUS[p["status"]][1].lower()}, '
                      f'due {date.fromisoformat(p["end"]):%b %Y})'
                      for p in [feat] + data["projects"] + data["extras"])
    certs = ", ".join(f'{c["name"]} ({date.fromisoformat(c["end"]):%b %Y})'
                      for c in data["certifications"])
    label = f"Roadmap {start.year}–{end.year}. Projects: {names}. Certifications: {certs}."
    return t.document(WIDTH, height, label, "".join(parts))
