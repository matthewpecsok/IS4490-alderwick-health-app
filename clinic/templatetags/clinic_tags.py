from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

BADGE_CLASSES = {
    # appointment status
    "scheduled": "badge-info",
    "checked_in": "badge-warning",
    "completed": "badge-success",
    "cancelled": "badge-muted",
    "no_show": "badge-danger",
    # request status
    "submitted": "badge-info",
    "under_review": "badge-warning",
    "declined": "badge-muted",
    # visit / thread status
    "draft": "badge-warning",
    "signed": "badge-success",
    "open": "badge-info",
    "closed": "badge-muted",
    # labs / problems / allergies
    "normal": "badge-success",
    "high": "badge-danger",
    "low": "badge-danger",
    "abnormal": "badge-danger",
    "active": "badge-info",
    "resolved": "badge-muted",
    "mild": "badge-muted",
    "moderate": "badge-warning",
    "severe": "badge-danger",
}


@register.filter
def badge_class(value):
    return BADGE_CLASSES.get(str(value), "badge-muted")


@register.simple_tag
def status_badge(value, label=None):
    css = BADGE_CLASSES.get(str(value), "badge-muted")
    text = label or str(value).replace("_", " ").capitalize()
    return mark_safe(f'<span class="badge {css}">{escape(text)}</span>')


@register.filter
def simple_markdown(text):
    """Render the small markup subset used in policy documents.

    '## ' lines become headings, '- ' lines become bullet lists, blank lines
    separate paragraphs. Everything is HTML-escaped first.
    """
    html = []
    paragraph = []
    in_list = False

    def flush_paragraph():
        if paragraph:
            html.append(f"<p>{' '.join(paragraph)}</p>")
            paragraph.clear()

    for raw in (text or "").splitlines():
        line = escape(raw.strip())
        if not line:
            flush_paragraph()
            if in_list:
                html.append("</ul>")
                in_list = False
            continue
        if line.startswith("## "):
            flush_paragraph()
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append(f"<h3>{line[3:]}</h3>")
        elif line.startswith("- "):
            flush_paragraph()
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append(f"<li>{line[2:]}</li>")
        else:
            if in_list:
                html.append("</ul>")
                in_list = False
            paragraph.append(line)
    flush_paragraph()
    if in_list:
        html.append("</ul>")
    return mark_safe("\n".join(html))


@register.filter
def split_lines(text):
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


@register.filter
def avatar_variant(value):
    """Pick one of five avatar colors from a primary key."""
    try:
        return f"alt-{int(value) % 5}"
    except (TypeError, ValueError):
        return ""
