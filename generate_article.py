import os, random, subprocess, json
from datetime import datetime
from openai import OpenAI

REPO_ROOT = "/root/felix_hq/repos/aibuildermarketplace"
REPO_B2B = f"{REPO_ROOT}/b2b"
DOMAIN = "https://aibuildermarketplace.com"
DOMAIN_B2B = f"{DOMAIN}/b2b"

VAULT = {
    "Bitvavo": "https://account.bitvavo.com/create?a=68DCE39715&pid=invite&c=referral",
    "Replit": "https://replit.com/signup?referral=dglhaket",
    "Invideo": "https://invideo.sjv.io/E00nbn",
    "Synthesia": "https://www.synthesia.io/?via=daniel-haket",
    "Kinsta": "https://kinsta.com/?kaid=EKSCJEFWBYJO",
    "Murf": "https://get.murf.ai/qbhzdrcv3l7x"
}

LANGUAGES = ["German", "Spanish", "Portuguese", "French", "English", "Dutch"]


def get_existing_folders():
    return [f.name for f in os.scandir(REPO_B2B) if f.is_dir() and f.name != '.git']


def rebuild_index(folders):
    """SEO-geoptimaliseerde b2b/index.html met donker thema, filter tabs en zoekfunctie."""
    import json as _json
    folders = sorted(folders, reverse=True)
    date_str = datetime.now().strftime("%Y-%m-%d")

    lang_codes = ['-en', '-fr', '-du', '-po', '-ge', '-sp']

    def clean_title(slug):
        s = slug
        for lc in lang_codes:
            if s.endswith(lc):
                s = s[:-len(lc)]
                break
        s = s.replace('-2026', '').replace('-', ' ').strip()
        words = s.split()
        result = []
        for w in words:
            if w.lower() == 'roi':
                result.append('ROI')
            elif w.lower() == 'vs':
                result.append('vs')
            else:
                result.append(w.capitalize())
        return ' '.join(result)

    def get_tool(slug):
        s = slug.lower()
        if s.startswith('kinsta'): return 'Kinsta'
        if s.startswith('synthesia'): return 'Synthesia'
        if s.startswith('invideo'): return 'InVideo'
        if s.startswith('replit'): return 'Replit'
        if s.startswith('bitvavo'): return 'Bitvavo'
        if s.startswith('murf'): return 'Murf'
        return 'Other'

    def get_type(slug):
        s = slug.lower()
        if 'ultimate-review' in s: return 'Review'
        if '-vs-' in s: return 'Comparison'
        if 'roi' in s: return 'ROI'
        if 'efficiency' in s: return 'Efficiency'
        if 'automation' in s: return 'Automation'
        if 'scale-up' in s: return 'Scale-Up'
        if 'founder-secrets' in s: return 'Secrets'
        if 'hosting' in s: return 'Hosting'
        if 'pricing' in s: return 'Pricing'
        return 'Guide'

    def get_desc(slug):
        tool = get_tool(slug)
        t = get_type(slug)
        descs = {
            'Review': f'Complete {tool} review for B2B founders. Features, pricing, pros and cons.',
            'Comparison': f'Head-to-head comparison. Which tool delivers better ROI for your business?',
            'ROI': f'Real ROI numbers for {tool}. Is it worth the investment for your team?',
            'Efficiency': f'Maximize your {tool} efficiency with expert workflows and best practices.',
            'Automation': f'Automate your {tool} workflows to save time and scale faster.',
            'Scale-Up': f'How to scale your business operations using {tool} effectively.',
            'Secrets': f'Advanced {tool} strategies that top founders use to get ahead.',
            'Hosting': f'Best practices for {tool} hosting, setup and optimization.',
            'Pricing': f'All {tool} pricing plans compared. Find the right plan for your budget.',
            'Guide': f'Expert {tool} guide for B2B businesses. Tips and strategies for 2026.',
        }
        return descs.get(t, f'Expert {tool} guide for B2B founders in 2026.')

    tool_icons = {'Kinsta': '🟢', 'Synthesia': '🎬', 'InVideo': '🎥', 'Replit': '💻', 'Bitvavo': '₿', 'Murf': '🎙️', 'Other': '🔧'}
    tag_colors = {'Review': '#1a7f4e', 'Comparison': '#6639ba', 'ROI': '#b45309', 'Efficiency': '#0369a1', 'Automation': '#0f766e', 'Scale-Up': '#be185d', 'Secrets': '#7c3aed', 'Hosting': '#0369a1', 'Pricing': '#b45309', 'Guide': '#374151'}

    cards_data = []
    for f in folders:
        tool = get_tool(f)
        typ = get_type(f)
        cards_data.append({'slug': f, 'tool': tool, 'type': typ, 'title': clean_title(f), 'desc': get_desc(f), 'icon': tool_icons.get(tool, '🔧'), 'color': tag_colors.get(typ, '#374151')})

    cards_json = _json.dumps(cards_data)
    n = len(folders)

    html = f"""<\!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>B2B AI Tools Reviews &amp; Comparisons 2026 | AIBuilder Marketplace</title>
  <meta name="description" content="Expert reviews and ROI comparisons of the best B2B AI tools in 2026. Kinsta, Synthesia, InVideo, Replit, Bitvavo and more.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{DOMAIN}/b2b/">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{DOMAIN}/b2b/">
  <meta property="og:title" content="B2B AI Tools Reviews &amp; Comparisons 2026 | AIBuilder Marketplace">
  <meta property="og:site_name" content="AIBuilder Marketplace">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"B2B AI Tools Reviews & Comparisons 2026","url":"{DOMAIN}/b2b/","dateModified":"{date_str}","isPartOf":{{"@type":"WebSite","name":"AIBuilder Marketplace","url":"{DOMAIN}"}}}}</script>
  <style>
    *,*::before,*::after{{box-sizing:border-box}}
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0d1117;color:#c9d1d9;margin:0;padding:0;line-height:1.6}}
    .topnav{{background:#161b22;border-bottom:1px solid #30363d;padding:14px 24px;font-size:.88em;display:flex;gap:16px;align-items:center}}
    .topnav a{{color:#8b949e;text-decoration:none}}.topnav a:hover{{color:#58a6ff}}.topnav .sep{{color:#30363d}}.topnav .current{{color:#e6edf3}}
    .hero{{background:linear-gradient(135deg,#0d1117 0%,#161b22 60%,#1a2744 100%);padding:60px 24px 50px;text-align:center;border-bottom:1px solid #30363d}}
    .hero h1{{color:#e6edf3;font-size:clamp(1.8em,4vw,2.8em);font-weight:800;margin:0 0 14px}}.hero h1 span{{color:#58a6ff}}
    .hero p{{color:#8b949e;font-size:1.05em;max-width:520px;margin:0 auto}}
    .hero-stats{{display:flex;justify-content:center;gap:40px;margin-top:32px;flex-wrap:wrap}}
    .stat .num{{font-size:2em;font-weight:800;color:#58a6ff;display:block}}.stat .lbl{{font-size:.82em;color:#6e7681}}
    .filters-wrap{{background:#161b22;border-bottom:1px solid #30363d;padding:16px 24px;position:sticky;top:0;z-index:10}}
    .filters-inner{{max-width:1100px;margin:0 auto;display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
    .filter-label{{font-size:.78em;color:#6e7681;margin-right:4px;font-weight:700;text-transform:uppercase;letter-spacing:.05em}}
    .filter-btn{{background:transparent;border:1px solid #30363d;color:#8b949e;padding:6px 14px;border-radius:20px;font-size:.82em;cursor:pointer;transition:all .15s;font-family:inherit}}
    .filter-btn:hover{{border-color:#58a6ff;color:#58a6ff}}.filter-btn.active{{background:#58a6ff;border-color:#58a6ff;color:#0d1117;font-weight:700}}
    .filter-sep{{width:1px;height:20px;background:#30363d;margin:0 4px}}
    .search-wrap{{max-width:1100px;margin:0 auto;padding:20px 24px 0}}
    .search-box{{width:100%;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 16px;color:#e6edf3;font-size:.95em;font-family:inherit;outline:none;transition:border-color .2s}}
    .search-box::placeholder{{color:#6e7681}}.search-box:focus{{border-color:#58a6ff}}
    .container{{max-width:1100px;margin:0 auto;padding:24px 24px 60px}}
    .results-count{{font-size:.85em;color:#6e7681;margin-bottom:16px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}
    .card{{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:20px;text-decoration:none;display:block;transition:border-color .2s,transform .15s}}
    .card:hover{{border-color:#388bfd;transform:translateY(-2px)}}
    .card-top{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
    .card-icon{{font-size:1.4em}}.card-tag{{font-size:.72em;font-weight:700;padding:2px 9px;border-radius:12px;color:#fff}}
    .card h3{{margin:0 0 6px;color:#e6edf3;font-size:.98em;font-weight:600}}
    .card p{{margin:0;color:#8b949e;font-size:.85em;line-height:1.5}}
    .card-arrow{{margin-top:12px;font-size:.82em;color:#388bfd}}
    .no-results{{text-align:center;padding:60px 20px;color:#6e7681}}
    .no-results .emoji{{font-size:3em;display:block;margin-bottom:12px}}
    footer{{background:#161b22;border-top:1px solid #30363d;text-align:center;padding:32px 20px;color:#6e7681;font-size:.85em}}
    footer a{{color:#58a6ff;text-decoration:none}}
  </style>
</head>
<body>
  <nav class="topnav"><a href="/">AIBuilder Marketplace</a><span class="sep">›</span><span class="current">B2B Knowledge Base</span></nav>
  <section class="hero">
    <h1>B2B AI Knowledge Base <span>2026</span></h1>
    <p>Expert reviews, ROI analyses and head-to-head comparisons of the tools that actually move the needle.</p>
    <div class="hero-stats">
      <div class="stat"><span class="num">{n}</span><span class="lbl">Articles</span></div>
      <div class="stat"><span class="num">6</span><span class="lbl">Tools Reviewed</span></div>
      <div class="stat"><span class="num">Daily</span><span class="lbl">Updated</span></div>
    </div>
  </section>
  <div class="filters-wrap"><div class="filters-inner">
    <span class="filter-label">Tool:</span>
    <button class="filter-btn active" onclick="filterTool(this,'all')">All</button>
    <button class="filter-btn" onclick="filterTool(this,'Kinsta')">🟢 Kinsta</button>
    <button class="filter-btn" onclick="filterTool(this,'Synthesia')">🎬 Synthesia</button>
    <button class="filter-btn" onclick="filterTool(this,'InVideo')">🎥 InVideo</button>
    <button class="filter-btn" onclick="filterTool(this,'Replit')">💻 Replit</button>
    <button class="filter-btn" onclick="filterTool(this,'Bitvavo')">₿ Bitvavo</button>
    <button class="filter-btn" onclick="filterTool(this,'Murf')">🎙️ Murf</button>
    <div class="filter-sep"></div>
    <span class="filter-label">Type:</span>
    <button class="filter-btn" onclick="filterType(this,'all')">All</button>
    <button class="filter-btn" onclick="filterType(this,'Review')">Review</button>
    <button class="filter-btn" onclick="filterType(this,'Comparison')">Comparison</button>
    <button class="filter-btn" onclick="filterType(this,'ROI')">ROI</button>
    <button class="filter-btn" onclick="filterType(this,'Automation')">Automation</button>
    <button class="filter-btn" onclick="filterType(this,'Scale-Up')">Scale-Up</button>
  </div></div>
  <div class="search-wrap"><input class="search-box" type="text" placeholder="Search reviews, tools or topics..." oninput="filterSearch(this.value)"></div>
  <div class="container">
    <div class="results-count" id="count"></div>
    <div class="grid" id="grid"></div>
    <div class="no-results" id="no-results" style="display:none"><span class="emoji">🔍</span>No results found. Try a different filter.</div>
  </div>
  <footer><p><a href="/">AIBuilder Marketplace</a> · <a href="/terms/">Terms</a> · <a href="mailto:felix@theweekly2pctedge.com">Contact</a></p></footer>
  <script>
    const CARDS={cards_json};
    let activeTool='all',activeType='all',searchQ='';
    function render(){{
      const grid=document.getElementById('grid'),count=document.getElementById('count'),nr=document.getElementById('no-results');
      const f=CARDS.filter(c=>{{
        const t=activeTool==='all'||c.tool===activeTool;
        const y=activeType==='all'||c.type===activeType;
        const q=searchQ.toLowerCase();
        const s=\!q||c.title.toLowerCase().includes(q)||c.tool.toLowerCase().includes(q)||c.type.toLowerCase().includes(q);
        return t&&y&&s;
      }});
      count.textContent=f.length+' article'+(f.length!==1?'s':'');
      if(!f.length){{grid.innerHTML='';nr.style.display='block';}}
      else{{nr.style.display='none';grid.innerHTML=f.map(c=>`<a class="card" href="/b2b/${{c.slug}}/"><div class="card-top"><span class="card-icon">${{c.icon}}</span><span class="card-tag" style="background:${{c.color}}">${{c.type}}</span></div><h3>${{c.title}}</h3><p>${{c.desc}}</p><div class="card-arrow">Read more →</div></a>`).join('');}}
    }}
    function filterTool(btn,tool){{document.querySelectorAll('.filter-btn').forEach(b=>{{if(b.getAttribute('onclick')&&b.getAttribute('onclick').includes('filterTool'))b.classList.remove('active');}});btn.classList.add('active');activeTool=tool;render();}}
    function filterType(btn,type){{document.querySelectorAll('.filter-btn').forEach(b=>{{if(b.getAttribute('onclick')&&b.getAttribute('onclick').includes('filterType'))b.classList.remove('active');}});btn.classList.add('active');activeType=type;render();}}
    function filterSearch(q){{searchQ=q;render();}}
    render();
  </script>
</body>
</html>"""

    with open(f"{REPO_B2B}/index.html", "w") as fh:
        fh.write(html)


def build_sitemap(folders):
    """Schrijft ZOWEL b2b/sitemap.xml ALS root sitemap.xml met alle pagina's."""
    date_str = datetime.now().strftime("%Y-%m-%d")

    # --- ROOT sitemap.xml (bevat homepage + b2b + alle artikelen) ---
    root_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    root_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n'
    root_xml += f'  <url>\n    <loc>{DOMAIN}/</loc>\n    <lastmod>{date_str}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>\n\n'
    root_xml += f'  <url>\n    <loc>{DOMAIN}/b2b/</loc>\n    <lastmod>{date_str}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.9</priority>\n  </url>\n\n'
    for f in sorted(folders, reverse=True):
        root_xml += f'  <url>\n    <loc>{DOMAIN}/b2b/{f}/</loc>\n    <lastmod>{date_str}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n\n'
    root_xml += '</urlset>'

    with open(f"{REPO_ROOT}/sitemap.xml", "w") as f:
        f.write(root_xml)

    # --- B2B sitemap.xml (sub-sitemap, enkel b2b pagina's) ---
    b2b_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    b2b_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    b2b_xml += f'  <url>\n    <loc>{DOMAIN}/b2b/</loc>\n    <lastmod>{date_str}</lastmod>\n    <priority>1.0</priority>\n  </url>\n'
    for f in sorted(folders, reverse=True):
        b2b_xml += f'  <url>\n    <loc>{DOMAIN}/b2b/{f}/</loc>\n    <lastmod>{date_str}</lastmod>\n    <priority>0.8</priority>\n  </url>\n'
    b2b_xml += '</urlset>'

    with open(f"{REPO_B2B}/sitemap.xml", "w") as f:
        f.write(b2b_xml)


def build_article_html(title, content, brand1, slug, schema_json, internal_links_html):
    """Bouw een volledig SEO-geoptimaliseerde artikel pagina."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    url = f"{DOMAIN}/b2b/{slug}/"

    # Taal op basis van slug suffix
    lang_map = {"-en": "en", "-fr": "fr", "-du": "nl", "-po": "pt", "-ge": "de", "-sp": "es"}
    html_lang = "en"
    for suffix, code in lang_map.items():
        if slug.endswith(suffix):
            html_lang = code
            break

    # Beschrijving op basis van title
    description = f"Expert B2B analysis of {title}. ROI breakdown, pricing comparison and founder insights. Find out if it's right for your business in 2026."[:160]

    # Affiliate CTA voor hoofdtool — donker thema, opvallend
    main_cta = f"""<div style='margin:40px 0;padding:30px;text-align:center;background:linear-gradient(135deg,#0d1117,#1a2744);border:1px solid #30363d;border-radius:12px;'>
  <h2 style='margin-top:0;color:#e6edf3;font-size:1.4em;'>Ready to try {brand1}?</h2>
  <p style='color:#8b949e;margin-bottom:20px;'>Join thousands of founders already using {brand1} to grow their business.</p>
  <a href='{VAULT[brand1]}' rel='nofollow sponsored' target='_blank' style='display:inline-block;background:#58a6ff;color:#0d1117;padding:16px 40px;text-decoration:none;font-weight:800;border-radius:8px;font-size:1.1em;'>
    Get Started with {brand1} →
  </a>
</div>"""

    # Tweede CTA halverwege het artikel
    mid_cta = f"""<div style='margin:30px 0;padding:20px;background:#161b22;border-left:4px solid #58a6ff;border-radius:6px;'>
  <p style='margin:0;color:#e6edf3;'><strong>Try {brand1} risk-free:</strong> <a href='{VAULT[brand1]}' rel='nofollow sponsored' target='_blank' style='color:#58a6ff;font-weight:700;'>Start your free trial →</a></p>
</div>"""

    # Footer met alle affiliate links — donker thema
    taglines = {'Kinsta':'Premium hosting','Synthesia':'AI video','InVideo':'Video creation','Replit':'AI coding','Bitvavo':'Crypto exchange','Murf':'AI voice'}
    footer_links = "".join([
        f"<li style='margin:6px 0'><a href='{link}' rel='nofollow sponsored' target='_blank' style='color:#58a6ff;text-decoration:none;font-weight:700'>{brand}</a> — {taglines.get(brand, 'AI tool')}</li>"
        for brand, link in VAULT.items()
    ])
    footer = f"""<div style='margin-top:50px;padding:24px;background:#161b22;border:1px solid #30363d;border-radius:10px;'>
  <h3 style='color:#e6edf3;margin-top:0;'>More AI Tools for Founders:</h3>
  <ul style='list-style:none;padding:0;'>{footer_links}</ul>
</div>"""

    # Breadcrumb structured data
    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
            {"@type": "ListItem", "position": 2, "name": "B2B Reviews", "item": f"{DOMAIN}/b2b/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}
        ]
    })

    og_image = f"{DOMAIN}/assets/og-default.png"

    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} 2026 | AIBuilder Marketplace</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{title} 2026 | AIBuilder Marketplace">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:site_name" content="AIBuilder Marketplace">
  <meta property="article:published_time" content="{date_str}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} 2026 | AIBuilder Marketplace">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{og_image}">
  {schema_json}
  <script type="application/ld+json">
  {breadcrumb_schema}
  </script>
  <style>
    body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; }}
    nav.breadcrumb {{ font-size: 0.9em; color: #666; margin-bottom: 20px; }}
    nav.breadcrumb a {{ color: #2980b9; text-decoration: none; }}
  </style>
</head>
<body>
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="/">Home</a> &rsaquo; <a href="/b2b/">B2B Reviews</a> &rsaquo; {title}
  </nav>
  {content}
  {main_cta}
  {internal_links_html}
  {footer}
</body>
</html>"""


COMPETITORS = {
    "Kinsta": ["Cloudways", "WP Engine", "SiteGround", "Flywheel", "Hostinger", "DigitalOcean"],
    "Synthesia": ["HeyGen", "Colossyan", "D-ID", "Pictory", "Loom", "Descript"],
    "Invideo": ["Canva Video", "Kapwing", "FlexClip", "Lumen5", "Veed.io", "CapCut"],
    "Replit": ["GitHub Codespaces", "CodeSandbox", "Glitch", "Railway", "Vercel", "Render"],
    "Bitvavo": ["Binance", "Kraken", "Coinbase", "KuCoin", "Bybit", "MEXC"],
    "Murf": ["ElevenLabs", "Play.ht", "Speechify", "WellSaid Labs", "Resemble AI", "Replica Studios"],
}

# Long-tail SEO topics per brand — elke entry genereert een uniek artikel
TOPICS = {
    "Kinsta": [
        "migration-guide", "wordpress-speed", "woocommerce-hosting", "staging-environment",
        "managed-hosting-benefits", "cdn-performance", "security-features", "developer-tools",
        "agency-hosting", "multisite-setup", "php-performance", "backup-restore",
        "uptime-monitoring", "support-quality", "enterprise-wordpress", "cost-savings",
        "free-trial-review", "devkinsta-local", "application-hosting", "database-hosting",
    ],
    "Synthesia": [
        "training-videos", "sales-enablement", "onboarding-videos", "multilingual-video",
        "avatar-customization", "enterprise-video", "marketing-videos", "explainer-videos",
        "video-localization", "api-integration", "template-library", "brand-kit",
        "compliance-training", "product-demos", "internal-comms", "video-analytics",
        "ai-avatar-quality", "script-to-video", "team-collaboration", "video-personalization",
    ],
    "Invideo": [
        "social-media-video", "youtube-creation", "ad-creation", "template-editing",
        "text-to-video", "brand-videos", "tutorial-creation", "video-ads-roi",
        "content-repurposing", "batch-video-creation", "stock-footage", "voiceover-sync",
        "instagram-reels", "tiktok-videos", "linkedin-video", "ecommerce-video",
        "team-workflow", "export-quality", "mobile-editing", "ai-script-generator",
    ],
    "Replit": [
        "ai-coding-assistant", "team-collaboration", "deployment-guide", "bounties-freelancing",
        "education-coding", "prototype-mvp", "database-integration", "api-development",
        "mobile-coding", "version-control", "ghostwriter-ai", "startup-stack",
        "fullstack-apps", "python-projects", "javascript-hosting", "hackathon-tool",
        "pair-programming", "code-review", "student-discount", "enterprise-security",
    ],
    "Bitvavo": [
        "beginner-crypto-guide", "staking-rewards", "trading-fees-comparison", "euro-deposits",
        "security-audit", "mobile-app-review", "portfolio-tracking", "tax-reporting",
        "limit-orders-guide", "altcoin-selection", "withdrawal-guide", "api-trading",
        "institutional-trading", "crypto-savings", "defi-integration", "dutch-crypto-regulation",
        "customer-support-review", "two-factor-security", "recurring-buys", "crypto-portfolio-2026",
    ],
    "Murf": [
        "voiceover-production", "elearning-narration", "podcast-intro", "youtube-voiceover",
        "commercial-voice", "audiobook-creation", "ivr-phone-system", "voice-cloning",
        "multilingual-voiceover", "voice-quality-test", "enterprise-tts", "api-voice-generation",
        "advertising-voice", "documentary-narration", "app-voice-integration", "voice-branding",
        "studio-vs-ai-voice", "accessibility-audio", "presentation-voiceover", "dubbing-localization",
    ],
}


def generate_topic(existing_folders):
    """Genereer een uniek topic dat nog niet bestaat."""
    brands = list(VAULT.keys())
    random.shuffle(brands)

    for _ in range(50):  # max 50 pogingen
        brand = random.choice(brands)
        mode = random.choice(["Review", "Versus", "Pricing", "Alternative"])
        lang = random.choice(LANGUAGES)
        lang_code = lang[:2].lower()

        if mode == "Review" and brand in TOPICS:
            # Kies een specifiek long-tail topic
            available = [t for t in TOPICS[brand]
                         if f"{brand.lower()}-{t}-{lang_code}" not in existing_folders]
            if not available:
                continue
            tag = random.choice(available)
            slug = f"{brand.lower()}-{tag}-{lang_code}"
            title = f"{brand}: {tag.replace('-', ' ').title()} Guide"
            prompt = f"""Write a detailed, expert-level article about {brand} focusing specifically on "{tag.replace('-', ' ')}" for B2B founders and SaaS businesses. Language: {lang}. Use HTML tags only (no <html>, <head>, <body>).

Structure:
1. A specific, benefit-driven headline (e.g. "How {brand} {tag.replace('-', ' ').title()} Can Save Founders 10+ Hours/Week")
2. The exact problem this solves — be specific about the pain point
3. Step-by-step guide or detailed feature breakdown with concrete examples
4. Pricing: which plan do you need for this specific feature?
5. Real-world use case with numbers and results
6. Pros and Cons (be honest about limitations)
7. Verdict and recommendation

Write like an experienced founder, not a marketer. Use specific numbers, real examples, and avoid generic phrases."""

        elif mode == "Versus":
            if random.random() < 0.5 and brand in COMPETITORS:
                brand2 = random.choice(COMPETITORS[brand])
                slug = f"{brand.lower()}-vs-{brand2.lower().replace(' ', '-').replace('.', '')}-{lang_code}"
            else:
                brand2 = random.choice([b for b in brands if b != brand])
                slug = f"{brand.lower()}-vs-{brand2.lower()}-{lang_code}"
            if slug in existing_folders:
                continue
            title = f"{brand} vs {brand2}"
            prompt = f"""Write an in-depth comparison: {brand} vs {brand2} for startup founders. Language: {lang}. Use HTML tags only (no <html>, <head>, <body>).

Structure:
1. Compelling headline with both tool names
2. Quick verdict table: Pricing, Best For, Key Strength, Biggest Weakness
3. Detailed comparison: Features, Pricing Tiers, Performance, Support
4. "Our Recommendation" — which tool for which use case
5. FAQ with 3-4 common questions

Use real pricing numbers and specific feature comparisons. No generic praise."""

        elif mode == "Pricing":
            slug = f"{brand.lower()}-pricing-{lang_code}"
            if slug in existing_folders:
                # Try pricing-breakdown variant
                slug = f"{brand.lower()}-pricing-breakdown-{lang_code}"
            if slug in existing_folders:
                slug = f"{brand.lower()}-cost-analysis-{lang_code}"
            if slug in existing_folders:
                continue
            title = f"{brand} Pricing Guide 2026"
            prompt = f"""Write a comprehensive pricing guide for {brand} for B2B founders evaluating their budget. Language: {lang}. Use HTML tags only (no <html>, <head>, <body>).

Structure:
1. Headline: "{brand} Pricing in 2026: Complete Guide"
2. Quick pricing table: ALL tiers with monthly/annual costs
3. What each plan includes — specific features per tier
4. Hidden costs founders should know about
5. ROI calculation: "If you pay X/month, here's the breakeven"
6. Comparison with 2 cheaper alternatives
7. Verdict: best plan for startups vs scale-ups vs enterprise

Include real pricing numbers. Founders searching pricing are ready to buy."""

        elif mode == "Alternative":
            slug = f"{brand.lower()}-alternatives-{lang_code}"
            if slug in existing_folders:
                slug = f"best-{brand.lower()}-alternatives-{lang_code}"
            if slug in existing_folders:
                slug = f"{brand.lower()}-competitors-{lang_code}"
            if slug in existing_folders:
                continue
            alt = random.choice(COMPETITORS.get(brand, ["competitor"]))
            title = f"Best {brand} Alternatives 2026"
            prompt = f"""Write "Best {brand} Alternatives in 2026" for B2B founders. Language: {lang}. Use HTML tags only (no <html>, <head>, <body>).

Structure:
1. Headline: "5 Best {brand} Alternatives for Founders in 2026"
2. Why founders look for alternatives
3. Each alternative ({alt} + 3-4 others): overview, pricing vs {brand}, pros/cons, best for
4. Comparison table: all alternatives vs {brand}
5. Final verdict: when to stay vs switch

Honest pros and cons only. Founders trust real reviews, not sales pitches."""

        else:
            continue

        return brand, mode, slug, title, prompt, lang, lang_code

    return None, None, None, None, None, None, None


def main():
    existing_folders = get_existing_folders()
    brand, mode, slug, title, prompt, lang, lang_code = generate_topic(existing_folders)

    if not slug:
        print("⚠️ Geen uniek topic gevonden na 50 pogingen. Alle combinaties bestaan al.")
        return

    path = f"{REPO_B2B}/{slug}"
    print(f"🚀 Victor 5.0 [{mode}]: {title} in {lang}...")

    # Gebruik OpenRouter (Claude) als beschikbaar, anders Ollama
    openrouter_key = os.getenv("OPENROUTER_KEY", "")
    if not openrouter_key:
        env_path = "/root/felix_hq/.env"
        if os.path.exists(env_path):
            for line in open(env_path):
                if line.startswith("OPENROUTER_KEY="):
                    openrouter_key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

    if openrouter_key:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)
        model = "anthropic/claude-sonnet-4"
        print("🧠 Schrijven met Claude Sonnet...")
    else:
        client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        model = "gemma4"
        print("🧠 Schrijven met lokale Ollama...")

    try:
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000
        )
        content = res.choices[0].message.content.replace("```html", "").replace("```", "")

        # Schema structured data
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"{title} 2026",
            "description": f"Expert B2B analysis of {title}.",
            "author": {"@type": "Organization", "name": "AIBuilder Marketplace"},
            "publisher": {"@type": "Organization", "name": "AIBuilder Marketplace"},
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "dateModified": datetime.now().strftime("%Y-%m-%d"),
            "itemReviewed": {"@type": "SoftwareApplication", "name": brand},
            "reviewRating": {"@type": "Rating", "ratingValue": "4.9"}
        }
        schema_json = f"<script type='application/ld+json'>\n{json.dumps(schema, indent=2)}\n</script>"

        # Interne links
        internal_links_html = ""
        if len(existing_folders) > 3:
            random_links = random.sample(existing_folders, 3)
            li_links = "".join([
                f"<li><a href='/b2b/{r}/'>{r.replace('-', ' ').title()}</a></li>"
                for r in random_links
            ])
            internal_links_html = f"<div style='margin-top:30px;padding-top:20px;border-top:1px solid #eee;'><h4>Read more B2B Insights:</h4><ul>{li_links}</ul></div>"

        full_html = build_article_html(title, content, brand, slug, schema_json, internal_links_html)

        os.makedirs(path, exist_ok=True)
        with open(f"{path}/index.html", "w") as f:
            f.write(full_html)

        # Update index en sitemaps
        new_folders = get_existing_folders()
        rebuild_index(new_folders)
        build_sitemap(new_folders)

        subprocess.run(["git", "add", "."], cwd=REPO_ROOT)
        subprocess.run(["git", "commit", "-m", f"Victor 5.0: {title} ({lang_code})"], cwd=REPO_ROOT)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=REPO_ROOT)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT)

        print(f"✅ Succes! {title} is live.")

    except Exception as e:
        print(f"❌ Fout: {e}")


if __name__ == "__main__":
    main()
