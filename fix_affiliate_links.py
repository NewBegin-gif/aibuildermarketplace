#!/usr/bin/env python3
"""
Fix alle affiliate links in bestaande artikelen:
1. Vervang kapotte CTAs (bijv /kinsta-trial-signup) met echte affiliate URLs
2. Fix footer-blokken die buiten </body> staan
3. Voeg ontbrekende nofollow sponsored toe
4. Verbeter CTA-design in alle artikelen
"""
import os, re

REPO_B2B = "/root/felix_hq/repos/aibuildermarketplace/b2b"

VAULT = {
    "Bitvavo": "https://account.bitvavo.com/create?a=68DCE39715&pid=invite&c=referral",
    "Replit": "https://replit.com/signup?referral=dglhaket",
    "InVideo": "https://invideo.sjv.io/E00nbn",
    "Invideo": "https://invideo.sjv.io/E00nbn",
    "Synthesia": "https://www.synthesia.io/?via=daniel-haket",
    "Kinsta": "https://kinsta.com/?kaid=EKSCJEFWBYJO",
    "Clay": "https://www.clay.com",
    "Murf": "https://get.murf.ai/qbhzdrcv3l7x",
}

def detect_brand(slug):
    s = slug.lower()
    for brand in ['kinsta','synthesia','invideo','replit','bitvavo','clay','murf']:
        if s.startswith(brand):
            return brand.capitalize() if brand != 'invideo' else 'InVideo'
    return None

def make_cta(brand):
    url = VAULT.get(brand, '')
    if not url:
        return ''
    return f"""<div style="margin:40px 0;padding:30px;text-align:center;background:linear-gradient(135deg,#0d1117,#1a2744);border:1px solid #30363d;border-radius:12px;">
  <h2 style="margin-top:0;color:#e6edf3;font-size:1.4em;">Ready to try {brand}?</h2>
  <p style="color:#8b949e;margin-bottom:20px;">Join thousands of founders already using {brand} to grow their business.</p>
  <a href="{url}" rel="nofollow sponsored" target="_blank" style="display:inline-block;background:#58a6ff;color:#0d1117;padding:16px 40px;text-decoration:none;font-weight:800;border-radius:8px;font-size:1.1em;transition:background .2s;">
    Get Started with {brand} →
  </a>
</div>"""

def make_footer(brand):
    links = []
    for b, url in VAULT.items():
        if b in ['Invideo']:
            continue
        style = "font-weight:800;color:#58a6ff" if b == brand else "color:#8b949e"
        links.append(f'<li style="margin:6px 0"><a href="{url}" rel="nofollow sponsored" target="_blank" style="{style};text-decoration:none">{b}</a> — {get_tagline(b)}</li>')
    return f"""<div style="margin-top:50px;padding:24px;background:#161b22;border:1px solid #30363d;border-radius:10px;">
  <h3 style="color:#e6edf3;margin-top:0">More AI Tools for Founders:</h3>
  <ul style="list-style:none;padding:0">{"".join(links)}</ul>
</div>"""

def get_tagline(brand):
    taglines = {
        'Kinsta': 'Premium managed WordPress hosting',
        'Synthesia': 'AI video with realistic avatars',
        'InVideo': 'AI-powered video creation',
        'Replit': 'AI coding platform',
        'Bitvavo': 'European crypto exchange',
        'Clay': 'B2B data enrichment',
        'Murf': 'AI voice generator',
    }
    return taglines.get(brand, 'AI tool')

fixed = 0
errors = []

for folder in sorted(os.listdir(REPO_B2B)):
    path = os.path.join(REPO_B2B, folder, "index.html")
    if not os.path.isfile(path):
        continue

    brand = detect_brand(folder)
    if not brand:
        continue

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    original = html

    # 1. Fix links die naar niet-bestaande pagina's gaan (bijv /kinsta-trial-signup)
    fake_patterns = [
        r'href="[^"]*trial-signup[^"]*"',
        r'href="[^"]*signup-now[^"]*"',
        r'href="[^"]*get-started[^"]*"',
        r'href="[^"]*try-free[^"]*"',
        r'href="[^"]*free-trial[^"]*"',
        r'href="[^"]*start-now[^"]*"',
        r'href="/[a-z]+-[a-z]+-[a-z]+"',  # relatieve paden zoals /kinsta-trial-signup
    ]
    aff_url = VAULT.get(brand, '')
    for pattern in fake_patterns:
        matches = re.findall(pattern, html)
        for m in matches:
            # Alleen vervangen als het niet al een echte affiliate link is
            if aff_url and aff_url not in m and 'b2b/' not in m and '/' in m:
                old_href = m
                new_href = f'href="{aff_url}" rel="nofollow sponsored" target="_blank"'
                html = html.replace(old_href, new_href, 1)

    # 2. Voeg nofollow sponsored toe aan affiliate links die het missen
    for b, url in VAULT.items():
        if url in html:
            # Zoek links zonder rel="nofollow sponsored"
            pattern = f'href="{re.escape(url)}"(?!.*?rel="nofollow)'
            if re.search(pattern, html):
                html = html.replace(f'href="{url}"', f'href="{url}" rel="nofollow sponsored" target="_blank"')

    # 3. Fix content buiten </body></html> — verwijder dubbele closings en footer buiten body
    # Verwijder alle content na de eerste </html>
    html_parts = html.split('</html>')
    if len(html_parts) > 2:
        html = html_parts[0] + '</html>'
    elif len(html_parts) == 2 and html_parts[1].strip():
        # Er is content na </html> — dat is de oude footer
        html = html_parts[0] + '</html>'

    # 4. Check of er een goede CTA is — zo niet, voeg toe voor </body>
    has_good_cta = aff_url in html and ('Get Started' in html or 'Claim your' in html or 'Ready to' in html)
    if not has_good_cta and '</body>' in html:
        cta = make_cta(brand)
        footer = make_footer(brand)
        html = html.replace('</body>', f'\n{cta}\n{footer}\n</body>')

    if html != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ {folder}")
        fixed += 1

print(f"\n📊 {fixed} artikelen gefixed.")
