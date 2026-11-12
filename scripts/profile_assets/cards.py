"""Highlight strip, project cards and the featured thesis card."""
from datetime import date

from . import theme as t


def month_span(start, end):
    """'Dec 2026 - Jan 2027', or 'May 2027' when both dates share a month."""
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if (a.year, a.month) == (b.year, b.month):
        return f"{a:%b %Y}"
    return f"{a:%b %Y} – {b:%b %Y}"


def highlights(items):
    width, height, card = 1040, 112, 330
    parts = []
    for i, item in enumerate(items):
        x = i * 355
        color = t.NAMED[item["color"]]
        body = (
            f'<rect x="{x + 0.5}" y="0.5" width="{card - 1}" height="{height - 1}" rx="12" '
            f'fill="{t.BG}" stroke="{t.BORDER}"/>'
            f'<circle cx="{x + 46}" cy="56" r="27" fill="{color}" fill-opacity="0.1" '
            f'stroke="{color}" stroke-opacity="0.55"/>'
            f'<text x="{x + 46}" y="66" text-anchor="middle" font-size="26">{t.esc(item["icon"])}</text>'
            f'<text x="{x + 88}" y="40" font-size="10.5" font-weight="700" fill="{color}" '
            f'letter-spacing="0.5">{t.esc(item["kicker"])}</text>'
            f'<text x="{x + 88}" y="64" font-size="15" font-weight="700" fill="{t.TEXT}">'
            f'{t.esc(item["title"])}</text>'
            f'<text x="{x + 88}" y="86" font-size="12" fill="{t.MUTED}">{t.esc(item["detail"])}</text>'
        )
        parts.append(t.fade_in(body, 0.2 + i * 0.25))
    label = "Highlights: " + "; ".join(f'{i["title"]} ({i["kicker"].title()})' for i in items)
    return t.document(width, height, label, "".join(parts))


def _project_body(project, width):
    """Card content above the footer. Returns (svg, y of the lowest element)."""
    inner = width - 48
    y = 95
    lines = []
    for line in t.wrap(project["summary"], inner, 12.5):
        lines.append(f'<text x="24" y="{y}" font-size="12.5" fill="{t.MUTED}">{t.esc(line)}</text>')
        y += 18
    tags, bottom = t.chips(24, y + 16, project["stack"], width - 24)
    body = (
        f'<text x="{width - 20}" y="150" text-anchor="end" font-size="96" font-weight="700" '
        f'fill="{t.TEXT}" fill-opacity="0.04">{t.esc(project["id"])}</text>'
        f'<text x="24" y="36" font-size="11.5" font-weight="700" fill="{t.DIM}" '
        f'letter-spacing="1">PROJECT {t.esc(project["id"])}</text>'
        + t.status_pill(width - 24, 32, project["status"])
        + f'<text x="24" y="70" font-size="17" font-weight="700" fill="{t.TEXT}">'
          f'{t.esc(project["title"])}</text>'
        + "".join(lines) + tags
    )
    return body, bottom + 6


def project_cards(projects):
    """One SVG per project, all the same height so they line up in a grid."""
    width = 520
    bodies = [_project_body(p, width) for p in projects]
    height = int(max(bottom for _, bottom in bodies) + 62)
    out = {}
    for project, (body, _) in zip(projects, bodies):
        footer = (
            f'<line x1="24" y1="{height - 44}" x2="{width - 24}" y2="{height - 44}" stroke="{t.BORDER}"/>'
            f'<text x="24" y="{height - 19}" font-size="11.5" fill="{t.TEXT}">'
            f'<tspan fill="{t.DIM}">target </tspan>{month_span(project["start"], project["end"])}</text>'
            f'<text x="{width - 24}" y="{height - 19}" text-anchor="end" font-size="11" '
            f'fill="{t.DIM}">{t.esc(project["pairs_with"])}</text>'
        )
        label = (f'Project {project["id"]}: {project["title"]}. {project["summary"]} '
                 f'Stack: {", ".join(project["stack"])}. Status: {t.STATUS[project["status"]][1].lower()}.')
        out[f'project-{project["id"]}'] = t.document(
            width, height, label, t.panel(width, height) + body + footer)
    return out


def _node(x, y, label, color, width=52):
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="28" rx="6" fill="{t.TITLEBAR}" stroke="{color}"/>'
        f'<text x="{x + width / 2}" y="{y + 18}" text-anchor="middle" font-size="10.5" '
        f'font-weight="700" fill="{t.TEXT}">{label}</text>'
    )


def _packet(path, color, dur, begin=0):
    return (f'<circle r="3" fill="{color}"><animateMotion dur="{dur}s" begin="{begin}s" '
            f'repeatCount="indefinite" path="{path}"/></circle>')


def _core_diagram():
    """Simplified 5G SA core: UE and gNB outside, network functions on the SBI inside k3s."""
    n2 = "M712 186 C 738 186 732 112 758 112"
    n3 = "M712 200 L 820 210"
    sbi = "M758 148 H996"
    links = (
        f'<line x1="682" y1="126" x2="682" y2="176" stroke="{t.DIM}" stroke-dasharray="3 4"/>'
        f'<path d="{n2}" fill="none" stroke="{t.YELLOW}" stroke-opacity="0.7"/>'
        f'<path d="{n3}" fill="none" stroke="{t.GREEN}" stroke-opacity="0.7"/>'
        f'<line x1="872" y1="210" x2="944" y2="210" stroke="{t.GREEN}" stroke-opacity="0.7"/>'
        f'<line x1="846" y1="148" x2="846" y2="196" stroke="{t.DIM}" stroke-dasharray="3 4"/>'
        f'<path d="{sbi}" stroke="{t.CYAN}" stroke-width="2"/>'
        + "".join(f'<line x1="{x}" y1="126" x2="{x}" y2="148" stroke="{t.CYAN}"/>'
                  for x in (784, 846, 908, 970))
    )
    labels = (
        f'<text x="756" y="85" font-size="10" fill="{t.DIM}">k3s · Cilium eBPF</text>'
        f'<text x="925" y="166" text-anchor="middle" font-size="10" fill="{t.CYAN}">SBI · mTLS (SPIRE)</text>'
        f'<text x="722" y="140" font-size="9" fill="{t.YELLOW}">N2</text>'
        f'<text x="756" y="198" font-size="9" fill="{t.GREEN}">N3</text>'
        f'<text x="852" y="180" font-size="9" fill="{t.DIM}">N4</text>'
        f'<text x="908" y="203" text-anchor="middle" font-size="9" fill="{t.GREEN}">N6</text>'
    )
    nodes = (
        _node(652, 98, "UE", t.MUTED, 60) + _node(652, 176, "gNB", t.MUTED, 60)
        + _node(758, 98, "AMF", t.BLUE) + _node(820, 98, "SMF", t.BLUE)
        + _node(882, 98, "NRF", t.BLUE) + _node(944, 98, "AUSF", t.BLUE)
        + _node(820, 196, "UPF", t.GREEN) + _node(944, 196, "DN", t.MUTED)
    )
    packets = (
        _packet(n2, t.YELLOW, 2.6)
        + _packet(n3 + " M872 210 L944 210", t.GREEN, 3.2, 0.6)
        + _packet(sbi, t.CYAN, 2.2) + _packet("M996 148 H758", t.CYAN, 2.2, 1.1)
    )
    cluster = (f'<rect x="744" y="66" width="266" height="178" rx="10" fill="{t.BLUE}" '
               f'fill-opacity="0.04" stroke="{t.BLUE}" stroke-opacity="0.6" stroke-dasharray="5 4"/>')
    return cluster + links + labels + packets + nodes


def featured(project):
    width, height = 1040, 296
    y = 108
    lines = []
    for line in t.wrap(project["summary"], 590, 13):
        lines.append(f'<text x="30" y="{y}" font-size="13" fill="{t.MUTED}">{t.esc(line)}</text>')
        y += 19
    tags, y = t.chips(30, y + 16, project["stack"], 630)
    facts = []
    for fact in project["facts"]:
        y += 24
        facts.append(f'<text x="30" y="{y}" font-size="12" fill="{t.TEXT}">'
                     f'<tspan fill="{t.GREEN}">✓ </tspan>{t.esc(fact)}</text>')
    repo = project["url"].split("//", 1)[1]
    body = (
        t.panel(width, height)
        + f'<text x="30" y="40" font-size="11.5" font-weight="700" fill="{t.CYAN}" '
          f'letter-spacing="1">★ {t.esc(project["kicker"])}</text>'
        + t.status_pill(width - 30, 36, project["status"])
        + f'<text x="30" y="78" font-size="22" font-weight="700" fill="{t.TEXT}">'
          f'{t.esc(project["title"])}</text>'
        + "".join(lines) + tags + "".join(facts)
        + _core_diagram()
        + f'<text x="{width - 30}" y="{height - 22}" text-anchor="end" font-size="11" '
          f'fill="{t.DIM}">{t.esc(repo)} ↗</text>'
    )
    label = (f'Featured project: {project["title"]}. {project["summary"]} '
             f'Stack: {", ".join(project["stack"])}.')
    return t.document(width, height, label, body)
