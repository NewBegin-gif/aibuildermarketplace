#!/usr/bin/env python3
"""Genereert b2b/index.html met alle artikelen en dark theme."""
import os, json
from datetime import datetime

REPO_B2B = "/root/felix_hq/repos/aibuildermarketplace/b2b"
REPO_ROOT = "/root/felix_hq/repos/aibuildermarketplace"
DOMAIN = "https://aibuildermarketplace.com"

lang_codes = ['-en', '-fr', '-du', '-po', '-ge', '-sp']
lang_flags = {'-en':'🇬🇧','-fr':'🇫🇷','-du':'🇳🇱','-po':'🇵🇹','-ge':'🇩🇪','-sp':'🇪🇸'}
tool_icons = {'Kinsta':'🟢','Synthesia':'🎬','InVideo':'🎥','Replit':'💻','Bitvavo':'₿','Clay':'🎯','Murf':'🎙️','Other':'🔧'}
tag_colors = {'Review':'#1a7f4e','Comparison':'#6639ba','ROI':'#b45309','Efficiency':'#0369a1','Automation':'#0f766e','Scale-Up':'#be185d','Secrets':'#7c3aed','Hosting':'#0369a1','Pricing':'#b45309','Guide':'#374151'}

def get_lang(slug):
    for lc, flag in lang_flags.items():
        if slug.endswith(lc): return flag
    return '🇬🇧'

def clean_title(slug):
    s = slug
    for lc in lang_codes:
        if s.endswith(lc): s = s[:-len(lc)]; break
    s = s.replace('-2026','').replace('-',' ').strip()
    return ' '.join(['ROI' if w.lower()=='roi' else 'vs' if w.lower()=='vs' else w.capitalize() for w in s.split()])

def get_tool(slug):
    s = slug.lower()
    for t in ['kinsta','synthesia','invideo','replit','bitvavo','clay','murf']:
        if s.startswith(t): return {'invideo':'InVideo'}.get(t, t.capitalize())
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
    tool = get_tool(slug); t = get_type(slug)
    d = {'Review':f'Complete {tool} review for B2B founders. Features, pricing, pros and cons.','Comparison':'Head-to-head comparison. Which tool delivers better ROI?','ROI':f'Real ROI numbers for {tool}. Worth the investment?','Efficiency':f'Maximize your {tool} efficiency with expert workflows.','Automation':f'Automate your {tool} workflows to save time and scale faster.','Scale-Up':f'How to scale your business with {tool} effectively.','Secrets':f'Advanced {tool} strategies that top founders use.','Hosting':f'{tool} hosting best practices and optimization.','Pricing':f'All {tool} pricing plans compared for 2026.','Guide':f'Expert {tool} guide for B2B businesses in 2026.'}
    return d.get(t, f'Expert {tool} guide for B2B founders in 2026.')

folders = sorted([f.name for f in os.scandir(REPO_B2B) if f.is_dir() and f.name != '.git'], reverse=True)
n = len(folders)
date_str = datetime.now().strftime("%Y-%m-%d")

cards = [{'slug':f,'tool':get_tool(f),'type':get_type(f),'title':clean_title(f),'desc':get_desc(f),'icon':tool_icons.get(get_tool(f),'🔧'),'color':tag_colors.get(get_type(f),'#374151'),'lang':get_lang(f)} for f in folders]
cards_json = json.dumps(cards, ensure_ascii=False)

# Bouw HTML — let op: geen bash heredoc, dus gewone ! werkt hier prima
excl = '!'  # voorkom mogelijke editor-problemen

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>B2B AI Tools Reviews &amp; Comparisons 2026 | AIBuilder Marketplace</title>
  <meta name="description" content="Expert reviews and ROI comparisons of the best B2B AI tools in 2026. Kinsta, Synthesia, InVideo, Replit, Bitvavo, Murf and more.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href=\"""" + DOMAIN + """/b2b/">
  <meta property="og:type" content="website">
  <meta property="og:url" content=\"""" + DOMAIN + """/b2b/">
  <meta property="og:title" content="B2B AI Tools Reviews &amp; Comparisons 2026 | AIBuilder Marketplace">
  <meta property="og:image" content=\"""" + DOMAIN + """/assets/og-default.png">
  <meta property="og:site_name" content="AIBuilder Marketplace">
  <style>
    *,*::before,*::after{box-sizing:border-box}
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0d1117;color:#c9d1d9;margin:0;padding:0;line-height:1.6}
    .topnav{background:#161b22;border-bottom:1px solid #30363d;padding:14px 24px;font-size:.88em;display:flex;gap:16px;align-items:center}
    .topnav a{color:#8b949e;text-decoration:none}.topnav a:hover{color:#58a6ff}.topnav .current{color:#e6edf3}
    .hero{background:linear-gradient(135deg,#0d1117 0%,#161b22 60%,#1a2744 100%);padding:60px 24px 50px;text-align:center;border-bottom:1px solid #30363d}
    .hero h1{color:#e6edf3;font-size:clamp(1.8em,4vw,2.8em);font-weight:800;margin:0 0 14px}.hero h1 span{color:#58a6ff}
    .hero p{color:#8b949e;font-size:1.05em;max-width:520px;margin:0 auto}
    .hero-stats{display:flex;justify-content:center;gap:40px;margin-top:32px;flex-wrap:wrap}
    .stat .num{font-size:2em;font-weight:800;color:#58a6ff;display:block}.stat .lbl{font-size:.82em;color:#6e7681}
    .filters-wrap{background:#161b22;border-bottom:1px solid #30363d;padding:16px 24px;position:sticky;top:0;z-index:10}
    .filters-inner{max-width:1100px;margin:0 auto;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
    .filter-label{font-size:.78em;color:#6e7681;margin-right:4px;font-weight:700;text-transform:uppercase;letter-spacing:.05em}
    .filter-btn{background:transparent;border:1px solid #30363d;color:#8b949e;padding:6px 14px;border-radius:20px;font-size:.82em;cursor:pointer;transition:all .15s;font-family:inherit}
    .filter-btn:hover{border-color:#58a6ff;color:#58a6ff}.filter-btn.active{background:#58a6ff;border-color:#58a6ff;color:#0d1117;font-weight:700}
    .filter-sep{width:1px;height:20px;background:#30363d;margin:0 4px}
    .search-wrap{max-width:1100px;margin:0 auto;padding:20px 24px 0}
    .search-box{width:100%;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 16px;color:#e6edf3;font-size:.95em;font-family:inherit;outline:none;transition:border-color .2s}
    .search-box::placeholder{color:#6e7681}.search-box:focus{border-color:#58a6ff}
    .container{max-width:1100px;margin:0 auto;padding:24px 24px 60px}
    .results-count{font-size:.85em;color:#6e7681;margin-bottom:16px}
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
    .card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:20px;text-decoration:none;display:block;transition:border-color .2s,transform .15s}
    .card:hover{border-color:#388bfd;transform:translateY(-2px)}
    .card-top{display:flex;align-items:center;gap:10px;margin-bottom:10px}
    .card-icon{font-size:1.4em}.card-tag{font-size:.72em;font-weight:700;padding:2px 9px;border-radius:12px;color:#fff}
    .card h3{margin:0 0 6px;color:#e6edf3;font-size:.98em;font-weight:600}
    .card p{margin:0;color:#8b949e;font-size:.85em;line-height:1.5}
    .card-lang{margin-left:auto;font-size:1.1em}
    .card-arrow{margin-top:12px;font-size:.82em;color:#388bfd}
    .no-results{text-align:center;padding:60px 20px;color:#6e7681}
    footer{background:#161b22;border-top:1px solid #30363d;text-align:center;padding:32px 20px;color:#6e7681;font-size:.85em}
    footer a{color:#58a6ff;text-decoration:none}
  </style>
</head>
<body>
  <nav class="topnav"><a href="/">AIBuilder Marketplace</a><span style="color:#30363d">›</span><span class="current">B2B Knowledge Base</span></nav>
  <section class="hero">
    <h1>B2B AI Knowledge Base <span>2026</span></h1>
    <p>Expert reviews, ROI analyses and head-to-head comparisons of the tools that actually move the needle.</p>
    <div class="hero-stats">
      <div class="stat"><span class="num">""" + str(n) + """</span><span class="lbl">Articles</span></div>
      <div class="stat"><span class="num">7</span><span class="lbl">Tools Reviewed</span></div>
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
    <button class="filter-btn" onclick="filterTool(this,'Clay')">🎯 Clay</button>
    <button class="filter-btn" onclick="filterTool(this,'Murf')">🎙️ Murf</button>
    <div class="filter-sep"></div>
    <span class="filter-label">Type:</span>
    <button class="filter-btn active" onclick="filterType(this,'all')">All</button>
    <button class="filter-btn" onclick="filterType(this,'Review')">Review</button>
    <button class="filter-btn" onclick="filterType(this,'Comparison')">Comparison</button>
    <button class="filter-btn" onclick="filterType(this,'ROI')">ROI</button>
    <button class="filter-btn" onclick="filterType(this,'Automation')">Automation</button>
    <button class="filter-btn" onclick="filterType(this,'Scale-Up')">Scale-Up</button>
  </div></div>
  <div class="search-wrap"><input class="search-box" type="text" placeholder="Search articles, tools or topics..." oninput="filterSearch(this.value)"></div>
  <div class="container">
    <div class="results-count" id="count"></div>
    <div class="grid" id="grid"></div>
    <div class="no-results" id="no-results" style="display:none"><span style="font-size:3em;display:block;margin-bottom:12px">🔍</span>No results found.</div>
  </div>
  <footer><p><a href="/">AIBuilder Marketplace</a> · <a href="/b2b/">B2B Reviews</a> · <a href="mailto:felix@theweekly2pctedge.com">Contact</a></p></footer>
  <script>
    const CARDS = """ + cards_json + """;
    let activeTool='all', activeType='all', searchQ='';
    function render() {
      const grid=document.getElementById('grid'), count=document.getElementById('count'), nr=document.getElementById('no-results');
      const f=CARDS.filter(c => {
        const t = activeTool==='all' || c.tool===activeTool;
        const y = activeType==='all' || c.type===activeType;
        const q = searchQ.toLowerCase();
        const s = !q || c.title.toLowerCase().includes(q) || c.tool.toLowerCase().includes(q) || c.type.toLowerCase().includes(q);
        return t && y && s;
      });
      count.textContent = f.length + ' article' + (f.length !== 1 ? 's' : '');
      if (!f.length) { grid.innerHTML=''; nr.style.display='block'; }
      else { nr.style.display='none'; grid.innerHTML=f.map(c=>`<a class="card" href="/b2b/${c.slug}/"><div class="card-top"><span class="card-icon">${c.icon}</span><span class="card-tag" style="background:${c.color}">${c.type}</span><span class="card-lang">${c.lang}</span></div><h3>${c.title}</h3><p>${c.desc}</p><div class="card-arrow">Read more →</div></a>`).join(''); }
    }
    function filterTool(btn,tool) { document.querySelectorAll('.filter-btn').forEach(b=>{ if(b.getAttribute('onclick')&&b.getAttribute('onclick').includes('filterTool')) b.classList.remove('active'); }); btn.classList.add('active'); activeTool=tool; render(); }
    function filterType(btn,type) { document.querySelectorAll('.filter-btn').forEach(b=>{ if(b.getAttribute('onclick')&&b.getAttribute('onclick').includes('filterType')) b.classList.remove('active'); }); btn.classList.add('active'); activeType=type; render(); }
    function filterSearch(q) { searchQ=q; render(); }
    render();
  </script>
</body>
</html>"""

with open(f"{REPO_B2B}/index.html", "w") as fh:
    fh.write(html)

print(f"Done! {n} artikelen geschreven naar b2b/index.html")
