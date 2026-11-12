"""GitHub stats panel: counters, language mix and weekly commit activity."""
from . import theme as t

WIDTH, HEIGHT = 1040, 330
RX0, RX1 = 400, 1010  # right-hand block


def render(stats):
    command, _ = t.prompt(66, f'gh-stats --user {stats["user"]}')
    parts = [t.window(WIDTH, HEIGHT, "bryan@archlinux: ~"), command]

    rows = [("Public repos", stats["repos"]), ("Commits", stats["commits"]),
            ("Pull requests", stats["prs"]), ("Issues", stats["issues"]),
            ("Stars earned", stats["stars"]), ("Followers", stats["followers"]),
            ("Most active", stats["most_active"]), ("Last commit", stats["last_commit"])]
    rows = [row for row in rows if row[1]]  # a counter still at zero is just noise
    rows.append(("On GitHub since", stats["since"]))
    for i, (key, value) in enumerate(rows):
        parts.append(t.fade_in(
            f'<text x="30" y="{106 + i * 25}" font-size="14" fill="{t.TEXT}">'
            f'<tspan fill="{t.BLUE}" font-weight="700">{key}</tspan>: {t.esc(value)}</text>',
            0.3 + i * 0.12))

    # Language mix: stacked bar + legend (top 6, the rest folded into "Other").
    languages = stats["languages"][:6]
    other = 100 - sum(pct for _, pct in languages)
    if other > 0.05 and stats["languages"][6:]:
        languages.append(("Other", other))
    parts.append(f'<text x="{RX0}" y="102" font-size="11" font-weight="700" fill="{t.DIM}" '
                 f'letter-spacing="1">LANGUAGES</text>')
    parts.append(f'<clipPath id="bar"><rect x="{RX0}" y="112" width="{RX1 - RX0}" height="12" rx="6"/></clipPath>')
    segments, x = [], RX0
    for i, (name, pct) in enumerate(languages):
        width = (RX1 - RX0) * pct / 100
        segments.append(f'<rect x="{x:.1f}" y="112" width="{width:.1f}" height="12" '
                        f'fill="{t.SERIES[i % len(t.SERIES)]}"/>')
        x += width
        lx, ly = RX0 + (i % 3) * 204, 148 + (i // 3) * 22
        parts.append(
            f'<circle cx="{lx + 5}" cy="{ly - 4}" r="4.5" fill="{t.SERIES[i % len(t.SERIES)]}"/>'
            f'<text x="{lx + 17}" y="{ly}" font-size="12" fill="{t.TEXT}">{t.esc(name)} '
            f'<tspan fill="{t.DIM}">{pct:.1f}%</tspan></text>')
    parts.append(f'<rect x="{RX0}" y="112" width="{RX1 - RX0}" height="12" rx="6" fill="{t.BORDER}"/>'
                 f'<g clip-path="url(#bar)">{"".join(segments)}</g>')

    # Weekly commits.
    weekly = stats["weekly"]
    top, base, peak = 222, 288, max(max(weekly), 1)
    slot = (RX1 - RX0) / len(weekly)
    parts.append(f'<text x="{RX0}" y="208" font-size="11" font-weight="700" fill="{t.DIM}" '
                 f'letter-spacing="1">COMMITS · LAST {len(weekly)} WEEKS</text>'
                 f'<text x="{RX1}" y="208" text-anchor="end" font-size="11" fill="{t.DIM}">'
                 f'{sum(weekly)} total · peak {max(weekly)}/week</text>')
    for i, count in enumerate(weekly):
        height = max((base - top) * count / peak, 2)
        color = t.CYAN if count == peak and count else (t.BLUE if count else t.BORDER)
        bx = RX0 + i * slot + (slot - 16) / 2
        parts.append(
            f'<rect x="{bx:.1f}" y="{base - height:.1f}" width="16" height="{height:.1f}" rx="2" fill="{color}">'
            f'<animate attributeName="height" values="0;{height:.1f}" dur="0.9s" fill="freeze"/>'
            f'<animate attributeName="y" values="{base};{base - height:.1f}" dur="0.9s" fill="freeze"/></rect>')
    parts.append(f'<line x1="{RX0}" y1="{base + 0.5}" x2="{RX1}" y2="{base + 0.5}" stroke="{t.BORDER}"/>'
                 f'<text x="{RX0}" y="{base + 15}" font-size="9" fill="{t.DIM}">{len(weekly)} weeks ago</text>'
                 f'<text x="{RX1}" y="{base + 15}" text-anchor="end" font-size="9" fill="{t.DIM}">this week</text>')

    closing, cx = t.prompt(HEIGHT - 22, "")
    parts.append(closing + t.cursor(cx, HEIGHT - 22))
    label = (f'GitHub stats for {stats["user"]}: {stats["repos"]} public repos, {stats["commits"]} commits, '
             f'{stats["prs"]} pull requests, {stats["stars"]} stars. Top languages: '
             + ", ".join(f"{name} {pct:.0f}%" for name, pct in languages) + ".")
    return t.document(WIDTH, HEIGHT, label, "".join(parts))
