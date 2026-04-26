#!/usr/bin/env python3
"""
Fix ALL articles: consistent dark theme + inline SVG brand logos + clean affiliate footer.
Replaces Victor's broken external image logos with working inline SVGs.
Removes Clay references. Fixes missing Murf links.
"""
import os
import re
from datetime import datetime

REPO_ROOT = os.environ.get("REPO_ROOT", "/root/felix_hq/repos/aibuildermarketplace")
# Also support running from Mac
if not os.path.exists(REPO_ROOT):
    REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aibuildermarketplace-main")

B2B_PATH = os.path.join(REPO_ROOT, "b2b")

VAULT = {
    "Kinsta": "https://kinsta.com/?kaid=EKSCJEFWBYJO",
    "Synthesia": "https://www.synthesia.io/?via=daniel-haket",
    "InVideo": "https://invideo.sjv.io/E00nbn",
    "Replit": "https://replit.com/signup?referral=dglhaket",
    "Bitvavo": "https://account.bitvavo.com/create?a=68DCE39715",
    "Murf": "https://get.murf.ai/qbhzdrcv3l7x",
}

BRAND_COLORS = {
    'kinsta': '#8b5cf6', 'synthesia': '#3b82f6', 'invideo': '#a78bfa',
    'replit': '#f59e0b', 'bitvavo': '#10b981', 'murf': '#ec4899',
}

BRAND_TAGLINES = {
    'Kinsta': 'Premium WordPress Hosting',
    'Synthesia': 'AI Video Creation',
    'InVideo': 'AI Video Editor',
    'Replit': 'AI Coding Platform',
    'Bitvavo': 'Crypto Exchange',
    'Murf': 'AI Voice Generator',
}

# Inline SVG logos (small, always work, no external dependencies)
BRAND_SVGS = {
    'kinsta': '<svg viewBox="0 0 24 24" width="20" height="20"><circle cx="12" cy="12" r="11" fill="#5333ed"/><path d="M12 6L7 9v6l5 3 5-3V9l-5-3zm0 1.2l3.9 2.3L12 11.8 8.1 9.5 12 7.2zM8 10.2l3.5 1.75v3.57L8 13.77V10.2zm5 5.32v-3.57L16.5 10.2v3.57L13 15.52z" fill="#fff"/></svg>',
    'synthesia': '<svg viewBox="0 0 24 24" width="20" height="20"><circle cx="12" cy="12" r="11" fill="#2563eb"/><path d="M9 7v10l8-5-8-5z" fill="#fff"/></svg>',
    'invideo': '<svg viewBox="0 0 24 24" width="20" height="20"><circle cx="12" cy="12" r="11" fill="#7c3aed"/><path d="M15 10.5V8c0-.55-.45-1-1-1H8c-.55 0-1 .45-1 1v8c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.5l3 3V7.5l-3 3z" fill="#fff"/></svg>',
    'replit': '<svg viewBox="0 0 24 24" width="20" height="20"><circle cx="12" cy="12" r="11" fill="#d97706"/><path d="M8 6h3.5v4.5H8V6zm4.5 0H16v4.5h-3.5V6zM8 11.5h3.5V16H8v-4.5zm4.5 0H16V16h-3.5v-4.5zM8 17h3.5v1H8v-1z" fill="#fff"/></svg>',
    'bitvavo': '<svg viewBox="0 0 24 24" width="20" height="20"><circle cx="12" cy="12" r="11" fill="#059669"/><text x="12" y="16.5" text-anchor="middle" fill="#fff" font-weight="800" font-size="13" font-family="system-ui">B</text></svg>',
    'murf': '<svg viewBox="0 0 24 24" width="20" height="20"><circle cx="12" cy="12" r="11" fill="#db2777"/><path d="M12 14c1.3 0 2.4-1.07 2.4-2.4V7.4C14.4 6.07 13.3 5 12 5s-2.4 1.07-2.4 2.4v4.2c0 1.33 1.1 2.4 2.4 2.4zm4.2-2.4c0 2.4-2 4.08-4.2 4.08S7.8 14 7.8 11.6H6.4c0 2.73 2.18 4.98 4.8 5.38V19h1.6v-2.02c2.62-.4 4.8-2.65 4.8-5.38h-1.4z" fill="#fff"/></svg>',
}

# Bigger logos for article header
BRAND_SVGS_LG = {k: v.replace('width="20" height="20"', 'width="28" height="28"') for k, v in BRAND_SVGS.items()}


def detect_brand(folder_name):
    """Detect brand from folder name."""
    first = folder_name.split('-')[0].lower()
    if first == 'best':
        parts = folder_name.split('-')
        if len(parts) > 1:
            first = parts[1].lower()
    if first in BRAND_COLORS:
        return first
    return None


def get_title(html, folder):
    """Extract title from HTML."""
    m = re.search(r'<title>(.*?)</title>', html)
    if m:
        t = m.group(1)
        t = t.replace(' | AIBuilder Marketplace', '').replace(' 2026', '').strip()
        return t
    return folder.replace('-', ' ').title()


def get_meta_desc(html, brand_name):
    m = re.search(r'meta name="description" content="(.*?)"', html)
    return m.group(1) if m else f"Expert review of {brand_name}"


def get_lang(html):
    m = re.search(r'<html[^>]*lang="([^"]*)"', html)
    return m.group(1) if m else 'en'


def get_date(html):
    m = re.search(r'datePublished["\s:]+(\d{4}-\d{2}-\d{2})', html)
    return m.group(1) if m else datetime.now().strftime("%Y-%m-%d")


def get_schema(html):
    """Extract all structured data blocks."""
    parts = re.findall(r'<script type=["\']application/ld\+json["\']>(.*?)</script>', html, re.DOTALL)
    return "\n".join([f'<script type="application/ld+json">{s.strip()}</script>' for s in parts])


def extract_body_content(html):
    """Extract the main article content from body, removing old chrome."""
    # Try to find article body
    if '<article' in html:
        m = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
        if m:
            return clean_content(m.group(1))

    # Try body
    if '<body' in html:
        body_start = html.find('>', html.find('<body')) + 1
        body_end = html.find('</body>')
        if body_end == -1:
            body_end = len(html)
        body = html[body_start:body_end].strip()
    else:
        body = html

    return clean_content(body)


def clean_content(content):
    """Clean up old nav, breadcrumbs, footers from content."""
    # Remove old topnav
    content = re.sub(r'<nav class="topnav">.*?</nav>', '', content, flags=re.DOTALL)
    # Remove old breadcrumbs
    content = re.sub(r'<nav class="breadcrumb"[^>]*>.*?</nav>', '', content, flags=re.DOTALL)
    # Remove old article headers we added
    content = re.sub(r'<header class="article-header">.*?</header>', '', content, flags=re.DOTALL)
    # Remove old footer with affiliate links (Victor's broken one)
    content = re.sub(r'<div class="article-footer">.*?</div>', '', content, flags=re.DOTALL)
    # Remove broken img tags with external logos
    content = re.sub(r'<img src="https://[^"]*(?:logo|icon|simple-icons)[^"]*"[^>]*>', '', content, flags=re.IGNORECASE)
    # Remove Clay references
    content = re.sub(r'<li[^>]*>.*?[Cc]lay.*?</li>', '', content, flags=re.DOTALL)
    # Remove old "Complete Tech Stack" / "More AI Tools" / "Official Site" footer blocks
    content = re.sub(r"<div style=['\"][^'\"]*margin-top:\s*50px[^'\"]*>.*?</div>", '', content, flags=re.DOTALL)
    content = re.sub(r"<div style=['\"][^'\"]*margin-top:\s*30px[^'\"]*>.*?</div>", '', content, flags=re.DOTALL)
    content = re.sub(r"<div[^>]*>\s*<h3>.*?(?:Tech Stack|More AI|Founders).*?</div>", '', content, flags=re.DOTALL)
    # Remove old "Official Site" link lists
    content = re.sub(r"<ul[^>]*>(?:<li[^>]*>.*?Official Site.*?</li>\s*)+</ul>", '', content, flags=re.DOTALL)
    # Remove old emoji-only affiliate lists (Victor's broken footer with emoji + no href)
    content = re.sub(r"<ul[^>]*style=['\"]list-style:none[^'\"]*['\"]>(?:<li[^>]*>.*?</li>\s*)+</ul>", '', content, flags=re.DOTALL)
    # Remove empty ul/li from footer cleanup
    content = re.sub(r'<ul[^>]*>\s*</ul>', '', content)
    # Remove old footer divs
    content = re.sub(r"<footer>.*?</footer>", '', content, flags=re.DOTALL)
    # Remove old inline CTA blocks
    content = re.sub(r"<div style=['\"][^'\"]*text-align:center[^'\"]*background[^'\"]*gradient[^'\"]*>.*?</div>", '', content, flags=re.DOTALL)
    # Remove old mid-article CTA blocks
    content = re.sub(r"<div style=['\"][^'\"]*background:#161b22[^'\"]*border-left[^'\"]*>.*?</div>", '', content, flags=re.DOTALL)
    # Clean up multiple blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def build_affiliate_footer(brand_key):
    """Build clean affiliate footer with inline SVG logos."""
    items = []
    for name, url in VAULT.items():
        key = name.lower()
        if key == 'invideo':
            key = 'invideo'
        svg = BRAND_SVGS.get(key, '')
        tagline = BRAND_TAGLINES.get(name, 'AI Tool')
        items.append(
            f'<li style="margin:8px 0;display:flex;align-items:center;gap:10px">'
            f'{svg}'
            f'<a href="{url}" rel="nofollow sponsored" target="_blank" '
            f'style="color:#58a6ff;text-decoration:none;font-weight:600">{name}</a>'
            f'<span style="color:#64748b">— {tagline}</span></li>'
        )
    links_html = "\n".join(items)
    return f'''<div style="margin-top:50px;padding:28px;background:#111827;border:1px solid #1e293b;border-radius:12px;">
  <h3 style="color:#f1f5f9;margin-top:0;font-size:1.1rem;">More AI Tools for Founders</h3>
  <ul style="list-style:none;padding:0;margin:0">{links_html}</ul>
</div>'''


def build_main_cta(brand_key, brand_name):
    """Build the main CTA block for a brand."""
    url = VAULT.get(brand_name, '')
    if not url:
        # Try capitalized
        for k, v in VAULT.items():
            if k.lower() == brand_key:
                url = v
                brand_name = k
                break
    if not url:
        return ''
    accent = BRAND_COLORS.get(brand_key, '#3b82f6')
    return f'''<div style="margin:40px 0;padding:32px;text-align:center;background:linear-gradient(135deg,#0a0e17,#1a2744);border:1px solid #1e293b;border-radius:12px;">
  <h2 style="margin-top:0;color:#f1f5f9;font-size:1.3em;">Ready to try {brand_name}?</h2>
  <p style="color:#94a3b8;margin-bottom:20px;">Join thousands of founders already using {brand_name} to grow their business.</p>
  <a href="{url}" rel="nofollow sponsored" target="_blank" style="display:inline-block;background:{accent};color:#fff;padding:14px 36px;text-decoration:none;font-weight:700;border-radius:8px;font-size:1.05em;">
    Get Started with {brand_name} &rarr;
  </a>
</div>'''


def restyle_article(folder, html):
    """Completely restyle an article to the new dark theme with logos."""
    brand_key = detect_brand(folder)
    if not brand_key:
        return None

    brand_name = brand_key.capitalize()
    if brand_name == 'Invideo':
        brand_name = 'InVideo'

    accent = BRAND_COLORS[brand_key]
    title = get_title(html, folder)
    desc = get_meta_desc(html, brand_name)
    lang = get_lang(html)
    date_str = get_date(html)
    schema = get_schema(html)
    body = extract_body_content(html)
    logo_svg = BRAND_SVGS_LG[brand_key]

    # Extra cleanup: remove ANY remaining affiliate footer blocks (catches all formats)
    # Remove blocks containing "More AI Tools" or "Tech Stack" or "Official Site"
    body = re.sub(r'<div[^>]*>\s*<h3[^>]*>.*?(?:More AI Tools|Tech Stack|Complete.*Stack).*?</h3>.*?</ul>\s*</div>', '', body, flags=re.DOTALL)
    # Remove any remaining "margin-top:50px" footer divs
    body = re.sub(r'<div\s+style="margin-top:50px[^"]*">.*?</div>', '', body, flags=re.DOTALL)
    body = re.sub(r"<div\s+style='margin-top:50px[^']*'>.*?</div>", '', body, flags=re.DOTALL)
    # Remove any remaining CTA gradient blocks
    body = re.sub(r'<div\s+style="[^"]*text-align:center[^"]*background[^"]*gradient[^"]*">.*?</div>', '', body, flags=re.DOTALL)
    body = re.sub(r"<div\s+style='[^']*text-align:center[^']*background[^']*gradient[^']*'>.*?</div>", '', body, flags=re.DOTALL)
    # Remove mid-article CTA blocks
    body = re.sub(r'<div\s+style="[^"]*background:#161b22[^"]*border-left[^"]*">.*?</div>', '', body, flags=re.DOTALL)
    body = re.sub(r"<div\s+style='[^']*background:#161b22[^']*border-left[^']*'>.*?</div>", '', body, flags=re.DOTALL)
    # Clean multiple blank lines
    body = re.sub(r'\n{3,}', '\n\n', body).strip()

    main_cta = build_main_cta(brand_key, brand_name)
    footer_block = build_affiliate_footer(brand_key)

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} 2026 | AIBuilder Marketplace</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://aibuildermarketplace.com/b2b/{folder}/">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title} 2026 | AIBuilder Marketplace">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="https://aibuildermarketplace.com/assets/og-default.png">
  <meta property="og:site_name" content="AIBuilder Marketplace">
  <meta name="twitter:card" content="summary_large_image">
  {schema}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *,*::before,*::after{{box-sizing:border-box}}
    :root{{--bg:#0a0e17;--bg2:#111827;--card:#1a1f2e;--border:#1e293b;--text:#f1f5f9;--text2:#94a3b8;--muted:#64748b;--accent:{accent}}}
    body{{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);margin:0;padding:0;line-height:1.8}}
    a{{color:var(--accent);text-decoration:none}}a:hover{{opacity:.85}}
    .topnav{{background:rgba(10,14,23,.92);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:0 24px;position:sticky;top:0;z-index:100}}
    .topnav-inner{{max-width:800px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:56px}}
    .topnav-logo{{font-weight:800;font-size:.95rem;color:var(--text)}}
    .topnav-logo em{{background:linear-gradient(135deg,#3b82f6,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-style:normal}}
    .topnav-links a{{color:var(--text2);font-size:.85rem;font-weight:500;margin-left:20px}}
    .topnav-links a:hover{{color:var(--text)}}
    .breadcrumb{{max-width:800px;margin:20px auto 0;padding:0 24px;font-size:.82rem;color:var(--muted)}}
    .breadcrumb a{{color:var(--text2)}}
    .article-header{{max-width:800px;margin:0 auto;padding:32px 24px 0}}
    .article-header h1{{font-size:clamp(1.5rem,4vw,2.2rem);font-weight:800;line-height:1.2;margin:0 0 16px;letter-spacing:-.02em}}
    .brand-badge{{display:inline-flex;align-items:center;gap:10px;margin-bottom:20px}}
    .brand-badge .tag{{background:rgba(59,130,246,.1);color:var(--accent);padding:4px 12px;border-radius:20px;font-weight:600;font-size:.75rem;border:1px solid rgba(59,130,246,.15)}}
    .brand-badge .date{{color:var(--muted);font-size:.82rem}}
    .article-body{{max-width:800px;margin:0 auto;padding:0 24px}}
    .article-body h1{{font-size:1.6rem;font-weight:800;margin:24px 0 16px}}
    .article-body h2{{color:var(--text);font-size:1.35rem;font-weight:700;margin:36px 0 16px;padding-bottom:8px;border-bottom:1px solid var(--border)}}
    .article-body h3{{color:var(--text);font-size:1.05rem;font-weight:600;margin:24px 0 10px}}
    .article-body p{{color:var(--text2);margin:0 0 16px;font-size:.95rem}}
    .article-body ul,.article-body ol{{color:var(--text2);padding-left:24px;margin:0 0 16px}}
    .article-body li{{margin:6px 0;font-size:.95rem}}
    .article-body strong{{color:var(--text)}}
    .article-body blockquote{{border-left:3px solid var(--accent);margin:20px 0;padding:14px 20px;background:var(--card);border-radius:0 8px 8px 0;color:var(--text2);font-style:italic}}
    .article-body table{{width:100%;border-collapse:collapse;margin:20px 0;font-size:.88rem}}
    .article-body th{{background:var(--card);color:var(--text);padding:10px 14px;text-align:left;font-weight:600;border:1px solid var(--border)}}
    .article-body td{{padding:8px 14px;border:1px solid var(--border);color:var(--text2)}}
    .article-body tr:hover td{{background:var(--card)}}
    .article-body code{{background:var(--card);color:var(--accent);padding:2px 6px;border-radius:4px;font-size:.88em}}
    .article-body img{{max-width:100%;border-radius:8px}}
    footer{{background:var(--bg2);border-top:1px solid var(--border);padding:28px 24px;text-align:center;color:var(--muted);font-size:.82rem;margin-top:40px}}
    footer a{{color:var(--text2)}}
    @media(max-width:640px){{.topnav-links{{display:none}}.article-header h1{{font-size:1.4rem}}}}
  </style>
</head>
<body>
  <nav class="topnav"><div class="topnav-inner">
    <a href="/" class="topnav-logo"><em>AIBuilder</em> Marketplace</a>
    <div class="topnav-links"><a href="/b2b/">All Reviews</a><a href="/">Home</a></div>
  </div></nav>
  <nav class="breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/b2b/">B2B Reviews</a> &rsaquo; {title}</nav>
  <header class="article-header">
    <div class="brand-badge">
      {logo_svg}
      <span class="tag">{brand_name}</span>
      <span class="date">{date_str}</span>
    </div>
    <h1>{title}</h1>
  </header>
  <article class="article-body">
    {body}
    {main_cta}
    {footer_block}
  </article>
  <footer>
    <p>&copy; 2025-2026 <a href="/">AIBuilder Marketplace</a>. Some links are affiliate links. <a href="/terms/">Terms</a></p>
  </footer>
</body>
</html>'''


def main():
    fixed = 0
    skipped = 0
    errors = []

    for folder in sorted(os.listdir(B2B_PATH)):
        article_path = os.path.join(B2B_PATH, folder, "index.html")
        if not os.path.isfile(article_path):
            continue

        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                html = f.read()
        except:
            errors.append(f"Cannot read: {folder}")
            continue

        brand_key = detect_brand(folder)
        if not brand_key:
            skipped += 1
            continue

        new_html = restyle_article(folder, html)
        if new_html:
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            fixed += 1
        else:
            skipped += 1

    print(f"\n{'='*50}")
    print(f"Fixed: {fixed} articles")
    print(f"Skipped: {skipped}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  - {e}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
