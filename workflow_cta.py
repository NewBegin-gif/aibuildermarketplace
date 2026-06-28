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
    """Cross-brand 'Verified Workflow' box \u2014 uitgeschakeld.

    The Weekly AI Edge wordt een Nederlandstalige property; Engelse review-
    pagina's verwijzen er daarom niet meer naar. Bewust leeg gelaten i.p.v.
    de functie te verwijderen, zodat bestaande callers blijven werken.
    """
    return ""
