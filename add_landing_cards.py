#!/usr/bin/env python3
"""
add_landing_cards.py
Voegt 9 nieuwe tool-cards toe aan de landing/homepage (index.html),
gemodelleerd op de bestaande Iconosquare-card.
Ankert op de Iconosquare-card en voegt de nieuwe <article>-cards in NA de
afsluitende </article> van die card. Idempotent (merk dat er al staat wordt
overgeslagen). Default = dry-run; gebruik --apply om echt te schrijven.

Run vanuit /root/felix_hq/repos/aibuildermarketplace
"""
import re, sys, time, shutil, os

HTML = "index.html"

# ---- merk-data -------------------------------------------------------------
# filter = bestaande data-category bucket op de homepage
BRANDS = [
 {"name":"QuillBot","url":"https://try.quillbot.com/1kodsf2wz3o2",
  "domain":"quillbot.com","badge":"Free trial","filter":"productivity",
  "color":"#00A67E","rating":"4.6","reviews":1800,
  "tagline":"AI paraphrasing, grammar & citation tool for better writing",
  "tags":["Writing","Grammar","Paraphrasing"]},

 {"name":"RunPod","url":"https://get.runpod.io/dai55gii8gxb",
  "domain":"runpod.io","badge":"Pay as you go","filter":"hosting",
  "color":"#6C2BD9","rating":"4.6","reviews":900,
  "tagline":"Affordable cloud GPUs for AI training & inference",
  "tags":["Cloud GPU","AI Training","Infrastructure"]},

 {"name":"Lindy","url":"https://try.lindy.ai/04841byjd5bi",
  "domain":"lindy.ai","badge":"Free trial","filter":"productivity",
  "color":"#4F46E5","rating":"4.5","reviews":700,
  "tagline":"Build AI agents & automations without code",
  "tags":["AI Agents","Automation","No-Code"]},

 {"name":"Typewise","url":"https://partner.typewise.app/gi20pkpo8bcd",
  "domain":"typewise.app","badge":"Custom pricing","filter":"sales",
  "color":"#0EA5E9","rating":"4.5","reviews":300,
  "tagline":"AI text prediction & autocomplete for customer service teams",
  "tags":["Customer Service","AI Writing","Productivity"]},

 {"name":"Adwisely","url":"https://get.adwisely.com/lahunz19q93e",
  "domain":"adwisely.com","badge":"Free trial","filter":"marketing",
  "color":"#F97316","rating":"4.4","reviews":600,
  "tagline":"Automated retargeting ads for Shopify & e-commerce",
  "tags":["Advertising","Retargeting","E-commerce"]},

 {"name":"AdCreative.ai","url":"https://free-trial.adcreative.ai/9rbtqowzgwy2",
  "domain":"adcreative.ai","badge":"Free trial","filter":"marketing",
  "color":"#EC4899","rating":"4.5","reviews":1200,
  "tagline":"AI-generated ad creatives & banners that convert",
  "tags":["Advertising","AI Design","Creatives"]},

 {"name":"Tax1099","url":"https://get.tax1099.com/0ivysaedzf4n",
  "domain":"tax1099.com","badge":"Pay per form","filter":"finance",
  "color":"#16A34A","rating":"4.5","reviews":500,
  "tagline":"E-file 1099, W-2 & IRS forms for businesses",
  "tags":["Finance","Tax Filing","Compliance"]},

 {"name":"Bitdefender","url":"https://get.bitdefender.com/s1cknsqsf3d1",
  "domain":"bitdefender.com","badge":"Free trial","filter":"productivity",
  "color":"#ED1C24","rating":"4.7","reviews":5200,
  "tagline":"Award-winning antivirus & cybersecurity protection",
  "tags":["Security","Antivirus","Privacy"]},

 {"name":"ClickUp","url":"https://try.web.clickup.com/1fuixmntw4bz",
  "domain":"clickup.com","badge":"Free plan","filter":"productivity",
  "color":"#7B68EE","rating":"4.6","reviews":8000,
  "tagline":"All-in-one project management & productivity platform",
  "tags":["Project Management","Productivity","Collaboration"]},
]

def esc(s):
    return s.replace("&", "&amp;")

def reviews_fmt(n):
    return "{:,}+".format(n)

def card_html(b):
    name = b["name"]; dom = b["domain"]; letter = name[0]
    tags = "".join('<span class="tool-tag">%s</span>' % esc(t) for t in b["tags"])
    logo = (
      '<div class="tool-logo" style="background:#fff;box-sizing:border-box;'
      'padding:5px" data-bg="%s" data-fg="#fff" data-letter="%s">'
      '<img src="https://logo.clearbit.com/%s" alt="%s" '
      'style="max-width:100%%;max-height:100%%;object-fit:contain" '
      'onerror="if(!this.dataset.t){this.dataset.t=1;this.src=&quot;'
      'https://www.google.com/s2/favicons?domain=%s&sz=128&quot;}else{'
      'var p=this.parentNode;p.style.background=p.dataset.bg;'
      'p.style.color=p.dataset.fg;p.textContent=p.dataset.letter}"></div>'
    ) % (b["color"], letter, dom, esc(name), dom)
    return "\n".join([
      '  <article class="tool-card fade-in" data-category="%s">' % b["filter"],
      '   <div class="tool-card-top">',
      '    <div class="tool-card-header">%s<h3>%s</h3></div>' % (logo, esc(name)),
      '    <span class="tool-badge deal">%s</span>' % esc(b["badge"]),
      '   </div>',
      '   <div class="tool-rating"><span class="stars">\u2605\u2605\u2605\u2605\u2605</span> %s \u00b7 %s reviews</div>' % (b["rating"], reviews_fmt(b["reviews"])),
      '   <p class="tool-desc">%s</p>' % esc(b["tagline"]),
      '   <div class="tool-tags">%s</div>' % tags,
      '   <div class="tool-cta-row">',
      '    <a href="%s" target="_blank" rel="sponsored noopener" class="tool-cta-primary">Try %s <span aria-hidden="true">\u2192</span></a>' % (b["url"], esc(name)),
      '    <a href="/b2b/?tool=%s" class="tool-cta-secondary">Reviews <span aria-hidden="true">\u2192</span></a>' % name,
      '   </div>',
      '  </article>',
    ])

def main():
    apply = "--apply" in sys.argv
    print("=== add_landing_cards  (%s) ===" % ("APPLY" if apply else "DRY-RUN"))
    if not os.path.exists(HTML):
        print("  FOUT: %s niet gevonden (run vanuit repos/aibuildermarketplace)" % HTML)
        return
    with open(HTML, encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")

    # idempotent: merken die al een eigen landing-card hebben overslaan
    todo = [b for b in BRANDS if ('/b2b/?tool=%s"' % b["name"]) not in content]
    skipped = [b["name"] for b in BRANDS if b not in todo]
    if skipped:
        print("  al aanwezig, overslaan: %s" % ", ".join(skipped))
    if not todo:
        print("  niets te doen.")
        return

    # anker: Iconosquare secondary CTA -> daarna eerste </article>
    sec = next((i for i, ln in enumerate(lines)
                if 'b2b/?tool=Iconosquare' in ln and 'tool-cta-secondary' in ln), None)
    if sec is None:
        print("  ANKER NIET GEVONDEN (Iconosquare secondary CTA)")
        return
    close = next((i for i in range(sec, len(lines)) if lines[i].strip() == "</article>"), None)
    if close is None:
        print("  </article> na anker niet gevonden")
        return

    new = []
    for b in todo:
        new.extend(card_html(b).split("\n"))
    print("  anker: Iconosquare-card sluit op regel %d -> %d cards na regel %d"
          % (close + 1, len(todo), close + 1))
    for b in todo:
        print("        + %-16s filter=%-12s -> /b2b/?tool=%s"
              % (b["name"], b["filter"], b["name"]))

    lines[close + 1:close + 1] = new
    new_content = "\n".join(lines)

    if apply:
        ts = time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(HTML, "%s.bak_%s" % (HTML, ts))
        with open(HTML, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("  -> geschreven (backup: %s.bak_%s)" % (HTML, ts))
        print("  -> +%d regels, %d nieuwe cards" % (len(new), len(todo)))
    else:
        print("  Dry-run. %d cards (%d regels) zouden worden ingevoegd."
              % (len(todo), len(new)))
        print("Draai opnieuw met --apply om te schrijven.")

if __name__ == "__main__":
    main()
