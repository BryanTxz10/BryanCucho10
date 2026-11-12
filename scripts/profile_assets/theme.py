"""Shared look for every generated SVG.

Same Tokyo Night palette and monospace stack as assets/terminal.svg, so the
generated cards read as part of the same terminal.
"""
import textwrap
from xml.sax.saxutils import escape

BG = "#1a1b26"
TITLEBAR = "#16161e"
BORDER = "#2f334d"
TEXT = "#c0caf5"
MUTED = "#a9b1d6"
DIM = "#565f89"
BLUE = "#1793D1"
CYAN = "#7dcfff"
GREEN = "#9ece6a"
YELLOW = "#e0af68"
RED = "#f7768e"
PURPLE = "#bb9af7"
ORANGE = "#ff9e64"

NAMED = {"blue": BLUE, "cyan": CYAN, "green": GREEN, "yellow": YELLOW,
         "red": RED, "purple": PURPLE, "orange": ORANGE}
SERIES = [BLUE, GREEN, YELLOW, PURPLE, RED, CYAN, ORANGE, MUTED]

# status -> (colour, label). "active" = published and still being worked on.
STATUS = {
    "shipped": (GREEN, "SHIPPED"),
    "active": (GREEN, "ACTIVE"),
    "in_progress": (YELLOW, "IN PROGRESS"),
    "planned": (BLUE, "PLANNED"),
}

FONT = ("'Fira Code','JetBrains Mono','Cascadia Code',Consolas,"
        "'DejaVu Sans Mono',monospace")
CHAR = 0.61  # advance width of one monospace glyph, as a fraction of font-size


def esc(value):
    return escape(str(value), {'"': "&quot;"})


def text_width(value, size):
    return len(str(value)) * size * CHAR


def wrap(value, width_px, size):
    return textwrap.wrap(value, max(8, int(width_px / (size * CHAR))))


def document(width, height, label, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">\n'
        f'<title>{esc(label)}</title>\n'
        f'<style>text{{font-family:{FONT};}}</style>\n'
        f'{body}\n</svg>\n'
    )


def panel(width, height):
    """Plain rounded card background."""
    return (f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" '
            f'fill="{BG}" stroke="{BORDER}"/>')


def window(width, height, title):
    """Terminal window chrome, identical to assets/terminal.svg."""
    return (
        panel(width, height)
        + f'<path d="M0.5 12.5 a12 12 0 0 1 12 -12 h{width - 25} a12 12 0 0 1 12 12 '
          f'v23.5 h-{width - 1} z" fill="{TITLEBAR}"/>'
        + f'<circle cx="22" cy="18" r="6" fill="{RED}"/>'
        + f'<circle cx="42" cy="18" r="6" fill="{YELLOW}"/>'
        + f'<circle cx="62" cy="18" r="6" fill="{GREEN}"/>'
        + f'<text x="{width / 2}" y="23" text-anchor="middle" font-size="13" '
          f'fill="{DIM}">{esc(title)}</text>'
    )


def prompt(y, command, cwd="~"):
    """`[bryan@archlinux ~]$ command` line; returns (svg, x after the prompt)."""
    head = f"[bryan@archlinux {cwd}]$ "
    return (
        f'<text x="30" y="{y}" font-size="14" fill="{TEXT}" xml:space="preserve">'
        f'<tspan fill="{GREEN}">[</tspan><tspan fill="{BLUE}" font-weight="700">bryan</tspan>@'
        f'<tspan fill="{BLUE}" font-weight="700">archlinux</tspan> {esc(cwd)}'
        f'<tspan fill="{GREEN}">]$</tspan> {esc(command)}</text>'
    ), 30 + text_width(head, 14)


def cursor(x, y):
    return (f'<rect x="{x:.1f}" y="{y - 13}" width="9" height="17" fill="{TEXT}">'
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
            f'dur="1s" repeatCount="indefinite"/></rect>')


def fade_in(body, begin):
    return (f'<g opacity="0"><animate attributeName="opacity" to="1" begin="{begin:.2f}s" '
            f'dur="0.4s" fill="freeze"/>{body}</g>')


def status_pill(right, y, status):
    """Status badge whose right edge sits at `right`; `y` is its vertical centre."""
    color, label = STATUS[status]
    width = text_width(label, 11) + 34
    x = right - width
    dot = f'<circle cx="{x + 13}" cy="{y}" r="3.5" fill="{color}">'
    if status in ("active", "in_progress"):
        dot += ('<animate attributeName="opacity" values="1;0.25;1" dur="1.4s" '
                'repeatCount="indefinite"/>')
    dot += "</circle>"
    return (
        f'<rect x="{x:.1f}" y="{y - 11}" width="{width:.1f}" height="22" rx="11" '
        f'fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.6"/>'
        f'{dot}<text x="{x + 23:.1f}" y="{y + 4}" font-size="11" font-weight="700" '
        f'fill="{color}">{label}</text>'
    )


def chips(x, y, labels, max_x, size=11):
    """Row(s) of stack tags. Returns (svg, y of the last row)."""
    out, cx = [], x
    for label in labels:
        width = text_width(label, size) + 16
        if cx + width > max_x and cx > x:
            cx, y = x, y + 28
        out.append(
            f'<rect x="{cx:.1f}" y="{y - 15}" width="{width:.1f}" height="21" rx="5" '
            f'fill="{TITLEBAR}" stroke="{BORDER}"/>'
            f'<text x="{cx + 8:.1f}" y="{y}" font-size="{size}" fill="{CYAN}">{esc(label)}</text>'
        )
        cx += width + 7
    return "".join(out), y
