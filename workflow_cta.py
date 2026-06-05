"""Single source of truth for the cross-brand 'Verified Workflow' box.

Used by review_template.py (new articles) and retrofit_workflow_cta.py
(existing articles) so the box is identical everywhere.

The box is fully inline-styled and references the CSS custom properties that
already exist in every /b2b/ article's :root (--card, --border, --accent,
--text, --text2), so it inherits each article's brand accent automatically and
needs no separate <style> changes.
"""
import re


def wf_campaign(brand1):
    """Slugify a brand/tool name for the utm_campaign value."""
    return re.sub(r"[^a-z0-9]+", "-", (brand1 or "").lower()).strip("-") or "general"


def workflow_cta_html(brand1):
    """Return the inline-styled 'Verified Workflow' editor's-note box."""
    name = (brand1 or "this tool").strip()
    camp = wf_campaign(brand1)
    href = (
        "https://theweeklyaiedge.com/?utm_source=aibuildermarketplace"
        "&utm_medium=review_box&utm_campaign=" + camp
    )
    return (
        '<aside class="workflow-cta" style="margin:44px 0 8px;padding:24px 26px;'
        'background:var(--card);border:1px solid var(--border);'
        'border-left:4px solid var(--accent);border-radius:12px">'
        '<div style="display:flex;align-items:center;gap:8px;font-size:.72rem;'
        'font-weight:700;letter-spacing:.09em;text-transform:uppercase;'
        'color:var(--accent);margin-bottom:10px">'
        '<span aria-hidden="true">\u2726</span> Verified Workflow</div>'
        '<p style="margin:0 0 16px;color:var(--text2);font-size:1rem;line-height:1.6">'
        'I don\u2019t just review <strong style="color:var(--text)">' + name + '</strong>, '
        'I use it to automate my business so I can step away from the screen. '
        'See my exact live setup over at The Weekly AI Edge.</p>'
        '<a href="' + href + '" target="_blank" rel="noopener" '
        'style="display:inline-flex;align-items:center;gap:8px;background:var(--accent);'
        'color:#fff;padding:11px 22px;border-radius:8px;font-weight:600;font-size:.92rem;'
        'text-decoration:none">See my live setup at The Weekly AI Edge '
        '<span aria-hidden="true">\u2192</span></a></aside>'
    )
