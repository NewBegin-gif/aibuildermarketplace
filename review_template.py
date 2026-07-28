"""
review_template.py — V2 review-page wrapper voor aibuildermarketplace.com
─────────────────────────────────────────────────────────────────────────
Drop-in vervanging voor build_article_html() in generate_article.py.

Wat erin zit (vs. V1):
- Above-the-fold "Quick Verdict" box: rating, prijs, badge, CTA
- Sticky CTA card (desktop) en sticky bottom CTA bar (mobiel)
- Automatisch gegenereerde Table of Contents uit <h2> tags
- Affiliate disclosure (FTC compliant) prominent bovenaan
- CTA labels vertaald per taal (en/fr/nl/pt/de/es)
- Schema.org Review JSON-LD met rating
- Brand-kleur accent per tool
- Pros/Cons styling (als content ze bevat)

Signatuur identiek aan V1 — drop-in vervangbaar.
"""
import re, json
from datetime import datetime

DOMAIN = "https://aibuildermarketplace.com"

# ─────────────────────────────────────────────────────────────────────────
# BRAND LOGOS — inline SVG (geen externe requests, geen broken images)
# Elk logo gebruikt viewBox 0 0 24 24 en width="1em" height="1em" zodat
# het schaalt met de parent's font-size.
# ─────────────────────────────────────────────────────────────────────────
LOGO_HOSTINGER = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#673DE6"/><path d="M6 6h2.4v5h7.2V6H18v12h-2.4v-5H8.4v5H6V6z" fill="#fff"/></svg>'

LOGO_KINSTA = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#5333ED"/><path d="M7 6h2.6v4.7L13 6h3.1l-3.9 5.3L17 18h-3l-2.7-5.4-1.7 1.9V18H7V6z" fill="#fff"/></svg>'

LOGO_SYNTHESIA = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#1F2937"/><circle cx="12" cy="10" r="3" fill="#3B82F6"/><path d="M6 18.5c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5" stroke="#3B82F6" stroke-width="2" fill="none" stroke-linecap="round"/></svg>'

LOGO_INVIDEO = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#7C3AED"/><path d="M9 7.5v9l7-4.5-7-4.5z" fill="#fff"/></svg>'

LOGO_REPLIT = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#0E1525"/><path d="M7 6h5v5H7V6zm5 5h5v5h-5v-5zm-5 5h5v3H7v-3z" fill="#F26207"/></svg>'

LOGO_BITVAVO = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#1B49C6"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">B</text></svg>'

LOGO_MURF = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#F23E76"/><path d="M5 11h1.5v2H5v-2zm2.5-2H9v6H7.5V9zm2.5-3h1.5v12H10V6zm2.5 4h1.5v4H12.5v-4zm2.5 2h1.5v0H15v0zm2.5-1h1.5v2H17.5v-2z" fill="#fff"/><circle cx="6" cy="12" r=".7" fill="#fff"/><circle cx="9" cy="12" r="1" fill="#fff"/><circle cx="12" cy="12" r="1.2" fill="#fff"/><circle cx="15" cy="12" r="1" fill="#fff"/><circle cx="18" cy="12" r=".7" fill="#fff"/></svg>'

LOGO_WPROCKET = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#FE5C2B"/><path d="M16.5 5.5c-2 .2-4.5 1.8-6 3.3L9 10.3 6.5 11l-1 1 3 1 1 1 1 3 1-1 .7-2.5 1.5-1.5c1.5-1.5 3.1-4 3.3-6 0-.3-.2-.5-.5-.5zm-2 4a1.3 1.3 0 110-2.6 1.3 1.3 0 010 2.6z" fill="#fff"/><path d="M7 16l-1.5 2L4 18.5 4.5 17 6 15.5 7 16z" fill="#fff"/></svg>'

LOGO_RANKMATH = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#724FFF"/><path d="M5 17h2v-3H5v3zm3.5 0h2v-6h-2v6zm3.5 0h2V9h-2v8zm3.5 0h2V7h-2v10z" fill="#fff"/></svg>'

LOGO_DEFAULT = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle"><rect width="24" height="24" rx="6" fill="#3B82F6"/><path d="M12 6l-6 4v4l6 4 6-4v-4l-6-4zm0 2.4l4.2 2.8L12 14l-4.2-2.8L12 8.4z" fill="#fff"/></svg>'


# ─────────────────────────────────────────────────────────────────────────
# AFFILIATE CONFIG — per brand
# ─────────────────────────────────────────────────────────────────────────
LOGO_AIRIA = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#6D28D9"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">A</text></svg>'
LOGO_PRINTIFY = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#1FA363"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">P</text></svg>'
LOGO_FLIPPA = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#18A558"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">F</text></svg>'
LOGO_TURBOTIC = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#FF5630"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">T</text></svg>'
LOGO_LANDINGI = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#F25C26"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">L</text></svg>'
LOGO_IDRIVE = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#0072BC"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">i</text></svg>'

LOGO_EXPERTISEAI = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#4F46E5"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">E</text></svg>'
LOGO_CREDIT_REPAIR_CLOUD = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#1565C0"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">C</text></svg>'
LOGO_AISQ = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#9333EA"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">A</text></svg>'
LOGO_NGRAM = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#DB2777"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">N</text></svg>'
LOGO_MANYCHAT = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#2C6EF2"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">M</text></svg>'
LOGO_PANGRAM = '<svg viewBox="0 0 24 24" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="6" fill="#0EA5E9"/><text x="12" y="17" text-anchor="middle" fill="#fff" font-size="15" font-weight="900" font-family="Arial, sans-serif">P</text></svg>'

AFFILIATE = {
    "Hostinger": {
        "url": "https://www.hostinger.com?REFERRALCODE=UZUDGLHAKW67",
        "rating": "4.7",
        "reviews": "28,500",
        "price": "From $2.99/mo",
        "badge": "75% off + free domain",
        "tagline": "Affordable hosting with AI website builder",
        "logo": LOGO_HOSTINGER,
        "color": "#673DE6",
        "category": "Hosting",
    },
    "Kinsta": {
        "url": "https://kinsta.com/?kaid=EKSCJEFWBYJO",
        "rating": "4.8",
        "reviews": "1,247",
        "price": "From $35/mo",
        "badge": "30-day money-back",
        "tagline": "Premium managed WordPress hosting",
        "logo": LOGO_KINSTA,
        "color": "#5333ED",
        "category": "Hosting",
    },
    "Synthesia": {
        "url": "https://www.synthesia.io/?via=daniel-haket",
        "rating": "4.7",
        "reviews": "3,892",
        "price": "From $22/mo",
        "badge": "Free demo",
        "tagline": "AI video generator with avatars",
        "logo": LOGO_SYNTHESIA,
        "color": "#3B82F6",
        "category": "AI Video",
    },
    "InVideo": {
        "url": "https://invideo.sjv.io/E00nbn?u=https%3A%2F%2Finvideo.io%2Fmake%2Fai-video-generator%2F",
        "rating": "4.6",
        "reviews": "12,400",
        "price": "From $20/mo",
        "badge": "Free plan",
        "tagline": "AI video editor for creators",
        "logo": LOGO_INVIDEO,
        "color": "#7C3AED",
        "category": "AI Video",
    },
    "Invideo": {
        "url": "https://invideo.sjv.io/E00nbn?u=https%3A%2F%2Finvideo.io%2Fmake%2Fai-video-generator%2F",
        "rating": "4.6",
        "reviews": "12,400",
        "price": "From $20/mo",
        "badge": "Free plan",
        "tagline": "AI video editor for creators",
        "logo": LOGO_INVIDEO,
        "color": "#7C3AED",
        "category": "AI Video",
    },
    "Replit": {
        "url": "https://replit.com/signup?referral=dglhaket",
        "rating": "4.7",
        "reviews": "8,450",
        "price": "Free plan",
        "badge": "AI Agent included",
        "tagline": "Cloud IDE with AI coding agent",
        "logo": LOGO_REPLIT,
        "color": "#F26207",
        "category": "Developer",
    },
    "Bitvavo": {
        "url": "https://account.bitvavo.com/create?a=68DCE39715&pid=invite&c=referral",
        "rating": "4.6",
        "reviews": "21,300",
        "price": "0.25% fee",
        "badge": "€10K fee-free",
        "tagline": "EU-licensed crypto exchange",
        "logo": LOGO_BITVAVO,
        "color": "#1B49C6",
        "category": "Crypto",
    },
    "Murf": {
        "url": "https://get.murf.ai/qbhzdrcv3l7x",
        "rating": "4.6",
        "reviews": "4,820",
        "price": "From $19/mo",
        "badge": "Free trial",
        "tagline": "AI voice generator, 120+ voices",
        "logo": LOGO_MURF,
        "color": "#F23E76",
        "category": "AI Voice",
    },
    "WP Rocket": {
        "url": "https://wp-rocket.me/?ref=daniel-haket",
        "rating": "4.8",
        "reviews": "3,200",
        "price": "From $59/yr",
        "badge": "14-day refund",
        "tagline": "WordPress speed-up plugin",
        "logo": LOGO_WPROCKET,
        "color": "#FE5C2B",
        "category": "WordPress",
    },
    "Rank Math": {
        "url": "https://rankmath.com/?utm_source=daniel-haket",
        "rating": "4.9",
        "reviews": "6,100",
        "price": "Free plan",
        "badge": "Pro from $59/yr",
        "tagline": "SEO plugin for WordPress",
        "logo": LOGO_RANKMATH,
        "color": "#724FFF",
        "category": "WordPress",
    },
    "Airia": {
        "url": "https://try.airia.com/63zm3k6oocba",
        "rating": "4.6",
        "reviews": "120+",
        "price": "Custom pricing",
        "badge": "Free demo",
        "tagline": "Build and run AI agents for the enterprise",
        "logo": LOGO_AIRIA,
        "color": "#6D28D9",
        "category": "AI Agent",
    },
    "Printify": {
        "url": "https://try.printify.com/nnjq3xkyctsk",
        "rating": "4.6",
        "reviews": "9,000+",
        "price": "Free plan",
        "badge": "Free to start",
        "tagline": "Print-on-demand for your online store",
        "logo": LOGO_PRINTIFY,
        "color": "#1FA363",
        "category": "E-commerce",
    },
    "Flippa": {
        "url": "https://referral.flippa.com/423fnj9u9lh5",
        "rating": "4.3",
        "reviews": "3,500+",
        "price": "Free to browse",
        "badge": "Free signup",
        "tagline": "Buy and sell online businesses and websites",
        "logo": LOGO_FLIPPA,
        "color": "#18A558",
        "category": "Marketplace",
    },
    "Turbotic": {
        "url": "https://try.turbotic.com/9bsnqewlv0qm",
        "rating": "4.5",
        "reviews": "150+",
        "price": "Custom pricing",
        "badge": "Book a demo",
        "tagline": "Manage and scale automation with AI",
        "logo": LOGO_TURBOTIC,
        "color": "#FF5630",
        "category": "Automation",
    },
    "Landingi": {
        "url": "https://try.landingi.com/hsaaq00kz6qg",
        "rating": "4.5",
        "reviews": "1,200+",
        "price": "From $29 per mo",
        "badge": "Free trial",
        "tagline": "No-code landing page and funnel builder",
        "logo": LOGO_LANDINGI,
        "color": "#F25C26",
        "category": "Marketing",
    },
    "IDrive": {
        "url": "https://partners.idrive.com/qrvz8k6i2arr",
        "rating": "4.6",
        "reviews": "4,000+",
        "price": "From $2.95 per mo",
        "badge": "First-year deal",
        "tagline": "Cloud backup for all your devices",
        "logo": LOGO_IDRIVE,
        "color": "#0072BC",
        "category": "Backup",
    },
    "ExpertiseAI": {
        "url": "https://expertiseai.partnerlinks.io/e2k8ggh9klcg",
        "rating": "4.6",
        "reviews": "80+",
        "price": "Custom pricing",
        "badge": "Free trial",
        "tagline": "AI sales agent that turns visitors into pipeline",
        "logo": LOGO_EXPERTISEAI,
        "color": "#4F46E5",
        "category": "Sales",
    },
    "Credit Repair Cloud": {
        "url": "https://get.creditrepaircloud.com/rzjqacc3xbwo",
        "rating": "4.7",
        "reviews": "2,500+",
        "price": "From $179 per mo",
        "badge": "30-day free trial",
        "tagline": "Software to start and run a credit repair business",
        "logo": LOGO_CREDIT_REPAIR_CLOUD,
        "color": "#1565C0",
        "category": "Finance",
    },
    "AISQ": {
        "url": "https://try.aisq.com/oftwfsjuajyw",
        "rating": "4.5",
        "reviews": "25,000+",
        "price": "Free plan",
        "badge": "Free to start",
        "tagline": "End-to-end AI marketing automation",
        "logo": LOGO_AISQ,
        "color": "#9333EA",
        "category": "Marketing",
    },
    "Ngram": {
        "url": "https://partner.ngram.com/32s9nqdqy7lr",
        "rating": "4.6",
        "reviews": "200+",
        "price": "From $20 per mo",
        "badge": "Free trial",
        "tagline": "Turn your content into polished branded videos",
        "logo": LOGO_NGRAM,
        "color": "#DB2777",
        "category": "AI Video",
    },
    "ManyChat": {
        "url": "https://manychat.partnerlinks.io/fytpn81je1y4",
        "rating": "4.6",
        "reviews": "5,000+",
        "price": "Free plan",
        "badge": "Free to start",
        "tagline": "Chat marketing automation for Instagram and Messenger",
        "logo": LOGO_MANYCHAT,
        "color": "#2C6EF2",
        "category": "Marketing",
    },
    "Pangram": {
        "url": "https://affiliate.pangram.com/x1xctagyhhbz",
        "rating": "4.7",
        "reviews": "300+",
        "price": "From $8 per mo",
        "badge": "Free trial",
        "tagline": "Accurate AI content detector you can trust",
        "logo": LOGO_PANGRAM,
        "color": "#0EA5E9",
        "category": "AI Detection",
    },
}

# Fallback voor onbekende brands
DEFAULT_AFFILIATE = {
    "url": "/b2b/",
    "rating": "4.5",
    "reviews": "1,000",
    "price": "Varies",
    "badge": "See pricing",
    "tagline": "AI tool for founders",
    "logo": LOGO_DEFAULT,
    "color": "#3B82F6",
    "category": "AI Tool",
}


def get_affiliate(brand):
    """Case-insensitive lookup met fallback."""
    if not brand:
        return DEFAULT_AFFILIATE
    for key, val in AFFILIATE.items():
        if key.lower() == brand.lower():
            return val
    return DEFAULT_AFFILIATE


# ─────────────────────────────────────────────────────────────────────────
# MEERTALIGE LABELS
# ─────────────────────────────────────────────────────────────────────────
LANG_MAP_SUFFIX = {
    "-zh": "zh", "-ko": "ko", "-hi": "hi", "-ar": "ar", "-th": "th", "-ru": "ru", "-cs": "cs", "-fi": "fi", "-el": "el", "-hu": "hu", "-ro": "ro", "-sw": "sw", "-ha": "ha", "-yo": "yo", "-am": "am", "-af": "af", "-zu": "zu","-en": "en", "-fr": "fr", "-du": "nl", "-po": "pt", "-ge": "de", "-sp": "es"}

LABELS = {
    "zh": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}。{tagline}。诚实的创始人评测，含优点、缺点和投资回报率。",
    },
    "ko": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. 장단점과 ROI를 담은 솔직한 창업자 리뷰.",
    },
    "hi": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. फायदे, नुकसान और ROI के साथ ईमानदार संस्थापक समीक्षा।",
    },
    "ar": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. مراجعة صادقة من المؤسس مع الإيجابيات والسلبيات والعائد على الاستثمار.",
    },
    "th": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. รีวิวจากผู้ก่อตั้งอย่างตรงไปตรงมา พร้อมข้อดี ข้อเสีย และ ROI",
    },
    "ru": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Честный обзор от основателя с плюсами, минусами и ROI.",
    },
    "cs": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Upřímná recenze zakladatele s klady, zápory a ROI.",
    },
    "fi": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Rehellinen perustajan arvostelu: hyödyt, haitat ja ROI.",
    },
    "el": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Ειλικρινής κριτική ιδρυτή με πλεονεκτήματα, μειονεκτήματα και ROI.",
    },
    "hu": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Őszinte alapítói értékelés előnyökkel, hátrányokkal és ROI-val.",
    },
    "ro": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Recenzie sinceră a fondatorului cu avantaje, dezavantaje și ROI.",
    },
    "sw": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Mapitio ya kweli ya mwanzilishi yenye faida, hasara na ROI.",
    },
    "ha": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Sahihin bita daga wanda ya kafa: fa'idodi, illa da ROI.",
    },
    "yo": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Àtúnyẹ̀wò olódodo láti ọ̀dọ̀ olùdásílẹ̀: àǹfààní, àìní àti ROI.",
    },
    "am": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. ከመስራቹ ሐቀኛ ግምገማ ከጥቅሞች፣ ጉዳቶች እና ROI ጋር።",
    },
    "af": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Eerlike stigter-resensie met voordele, nadele en ROI.",
    },
    "zu": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
        "meta_description": "{title} —{price}. {tagline}. Ukubuyekezwa okuqotho komsunguli: izinzuzo, ububi ne-ROI.",
    },

    "en": {
        "cta_main": "Try {brand} →",
        "cta_free": "Start free trial →",
        "cta_get": "Get started with {brand}",
        "quick_verdict": "Quick Verdict",
        "rating": "Rating",
        "price": "Pricing",
        "best_for": "Best for",
        "toc": "Contents",
        "in_this_review": "In this review",
        "read_more": "Read more",
        "more_tools": "More tools for founders",
        "faq": "Frequently asked questions",
        "back_to_top": "Back to top ↑",
        "all_reviews": "All Reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Based on {reviews} reviews",
        "founders_choice": "Founder's choice",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "We may earn a commission when you sign up via the links on this page — at no extra cost to you. Our reviews remain independent and based on hands-on testing.",
        "last_updated": "Last updated",
        "reading_time": "min read",
    },
    "fr": {
        "cta_main": "Essayer {brand} →",
        "cta_free": "Essai gratuit →",
        "cta_get": "Démarrer avec {brand}",
        "quick_verdict": "Verdict rapide",
        "rating": "Note",
        "price": "Prix",
        "best_for": "Idéal pour",
        "toc": "Sommaire",
        "in_this_review": "Dans ce test",
        "read_more": "Lire plus",
        "more_tools": "Plus d'outils pour fondateurs",
        "faq": "Questions fréquentes",
        "back_to_top": "Retour en haut ↑",
        "all_reviews": "Tous les tests",
        "home": "Accueil",
        "breadcrumb_reviews": "Tests B2B",
        "based_on": "Sur la base de {reviews} avis",
        "founders_choice": "Choix des fondateurs",
        "disclosure_title": "Divulgation d'affiliation",
        "disclosure": "Nous pouvons recevoir une commission si vous vous inscrivez via les liens de cette page — sans frais supplémentaires pour vous. Nos tests restent indépendants et basés sur une utilisation réelle.",
        "last_updated": "Mis à jour",
        "reading_time": "min de lecture",
    },
    "nl": {
        "cta_main": "Probeer {brand} →",
        "cta_free": "Gratis proberen →",
        "cta_get": "Begin met {brand}",
        "quick_verdict": "Snel oordeel",
        "rating": "Score",
        "price": "Prijs",
        "best_for": "Ideaal voor",
        "toc": "Inhoud",
        "in_this_review": "In deze review",
        "read_more": "Lees meer",
        "more_tools": "Meer tools voor founders",
        "faq": "Veelgestelde vragen",
        "back_to_top": "Naar boven ↑",
        "all_reviews": "Alle reviews",
        "home": "Home",
        "breadcrumb_reviews": "B2B Reviews",
        "based_on": "Op basis van {reviews} reviews",
        "founders_choice": "Aanrader voor founders",
        "disclosure_title": "Affiliate disclosure",
        "disclosure": "Wij ontvangen mogelijk een commissie als je je aanmeldt via de links op deze pagina — zonder extra kosten voor jou. Onze reviews blijven onafhankelijk en gebaseerd op eigen ervaring.",
        "last_updated": "Laatst bijgewerkt",
        "reading_time": "min leestijd",
    },
    "pt": {
        "cta_main": "Experimentar {brand} →",
        "cta_free": "Teste grátis →",
        "cta_get": "Começar com {brand}",
        "quick_verdict": "Veredito rápido",
        "rating": "Avaliação",
        "price": "Preço",
        "best_for": "Ideal para",
        "toc": "Índice",
        "in_this_review": "Nesta análise",
        "read_more": "Ler mais",
        "more_tools": "Mais ferramentas para fundadores",
        "faq": "Perguntas frequentes",
        "back_to_top": "Voltar ao topo ↑",
        "all_reviews": "Todas as análises",
        "home": "Início",
        "breadcrumb_reviews": "Análises B2B",
        "based_on": "Com base em {reviews} avaliações",
        "founders_choice": "Escolha dos fundadores",
        "disclosure_title": "Divulgação de afiliação",
        "disclosure": "Podemos receber uma comissão se você se inscrever pelos links desta página — sem custo adicional para você. Nossas análises permanecem independentes e baseadas em testes reais.",
        "last_updated": "Última atualização",
        "reading_time": "min de leitura",
    },
    "de": {
        "cta_main": "{brand} testen →",
        "cta_free": "Kostenlos starten →",
        "cta_get": "Mit {brand} loslegen",
        "quick_verdict": "Schnelles Fazit",
        "rating": "Bewertung",
        "price": "Preis",
        "best_for": "Ideal für",
        "toc": "Inhalt",
        "in_this_review": "In diesem Test",
        "read_more": "Weiterlesen",
        "more_tools": "Mehr Tools für Gründer",
        "faq": "Häufige Fragen",
        "back_to_top": "Nach oben ↑",
        "all_reviews": "Alle Tests",
        "home": "Startseite",
        "breadcrumb_reviews": "B2B-Tests",
        "based_on": "Basierend auf {reviews} Bewertungen",
        "founders_choice": "Empfehlung für Gründer",
        "disclosure_title": "Affiliate-Hinweis",
        "disclosure": "Wir erhalten möglicherweise eine Provision, wenn Sie sich über die Links auf dieser Seite anmelden — ohne Mehrkosten für Sie. Unsere Tests bleiben unabhängig und basieren auf eigener Erfahrung.",
        "last_updated": "Zuletzt aktualisiert",
        "reading_time": "Min Lesezeit",
    },
    "es": {
        "cta_main": "Probar {brand} →",
        "cta_free": "Prueba gratis →",
        "cta_get": "Empezar con {brand}",
        "quick_verdict": "Veredicto rápido",
        "rating": "Valoración",
        "price": "Precio",
        "best_for": "Ideal para",
        "toc": "Contenidos",
        "in_this_review": "En esta reseña",
        "read_more": "Leer más",
        "more_tools": "Más herramientas para fundadores",
        "faq": "Preguntas frecuentes",
        "back_to_top": "Volver arriba ↑",
        "all_reviews": "Todas las reseñas",
        "home": "Inicio",
        "breadcrumb_reviews": "Reseñas B2B",
        "based_on": "Basado en {reviews} reseñas",
        "founders_choice": "Recomendado para fundadores",
        "disclosure_title": "Divulgación de afiliación",
        "disclosure": "Podemos recibir una comisión si te registras a través de los enlaces de esta página — sin coste adicional para ti. Nuestras reseñas se mantienen independientes y se basan en pruebas reales.",
        "last_updated": "Última actualización",
        "reading_time": "min de lectura",
    },
}


def get_lang(slug):
    """Detecteert taalcode uit slug suffix."""
    for suffix, code in LANG_MAP_SUFFIX.items():
        if slug.endswith(suffix):
            return code
    return "en"


def get_labels(lang):
    return LABELS.get(lang, LABELS["en"])


# ─────────────────────────────────────────────────────────────────────────
# TOC EXTRACTIE
# ─────────────────────────────────────────────────────────────────────────
def slugify(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60] or "section"


def build_toc(content):
    """Vindt alle <h2> tags, voegt id-attributen toe en bouwt een TOC.
    Returns (content_with_ids, toc_items_list)."""
    headings = []
    used_ids = set()

    def repl(m):
        attrs = m.group(1) or ""
        inner = m.group(2)
        existing_id = re.search(r'id\s*=\s*["\']([^"\']+)["\']', attrs)
        if existing_id:
            sid = existing_id.group(1)
        else:
            base = slugify(inner)
            sid = base
            i = 2
            while sid in used_ids:
                sid = f"{base}-{i}"
                i += 1
            attrs = (attrs + f' id="{sid}"').strip()
        used_ids.add(sid)
        text = re.sub(r"<[^>]+>", "", inner).strip()
        headings.append({"id": sid, "text": text})
        return f"<h2 {attrs}>{inner}</h2>"

    new_content = re.sub(
        r"<h2([^>]*)>(.*?)</h2>",
        repl,
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return new_content, headings


def render_toc(headings, labels):
    if len(headings) < 2:
        return ""
    items = "".join(
        f'<li><a href="#{h["id"]}">{h["text"]}</a></li>' for h in headings
    )
    return (
        f'<aside class="toc" aria-label="{labels["toc"]}">'
        f'<div class="toc-title">{labels["in_this_review"]}</div>'
        f'<ol>{items}</ol>'
        f'</aside>'
    )


# ─────────────────────────────────────────────────────────────────────────
# READING TIME
# ─────────────────────────────────────────────────────────────────────────
def reading_time(content):
    text = re.sub(r"<[^>]+>", " ", content)
    words = len(text.split())
    return max(2, round(words / 220))


# ─────────────────────────────────────────────────────────────────────────
# BUILD ARTICLE HTML V2
# ─────────────────────────────────────────────────────────────────────────
# cross-brand Verified Workflow box (single source of truth: workflow_cta.py)
try:
    from workflow_cta import workflow_cta_html as _wf_box
except Exception:
    def _wf_box(_b):
        return ""


def build_article_html_v2(title, content, brand1, slug, schema_json, internal_links_html):
    """V2 wrapper — drop-in vervanging voor build_article_html()."""
    aff = get_affiliate(brand1)
    lang = get_lang(slug)
    L = get_labels(lang)
    date_str = datetime.now().strftime("%Y-%m-%d")
    url = f"{DOMAIN}/b2b/{slug}/"
    accent = aff["color"]
    aff_url = aff["url"]

    # TOC + headings met id
    content_with_ids, headings = build_toc(content)
    toc_html = render_toc(headings, L)
    rt = reading_time(content)

    # Meta description
    description = (
        f"{title} — {aff['price']}. "
        f"{aff['tagline']}. Honest founder review with pros, cons and ROI."
    )[:160]

    # CTA labels
    cta_main = L["cta_main"].format(brand=brand1)
    cta_free = L["cta_free"]
    cta_get = L["cta_get"].format(brand=brand1)

    # Star rating display
    rating_val = float(aff["rating"])
    full_stars = int(rating_val)
    half = 1 if (rating_val - full_stars) >= 0.5 else 0
    empty = 5 - full_stars - half
    stars_html = "★" * full_stars + ("⯨" if half else "") + "☆" * empty

    # ─── Quick Verdict card (above the fold) ───
    quick_verdict = f"""
<aside class="verdict-card" aria-labelledby="verdict-title">
  <div class="verdict-top">
    <span class="verdict-icon" aria-hidden="true">{aff['logo']}</span>
    <div class="verdict-meta">
      <div class="verdict-brand">{brand1}</div>
      <div class="verdict-tagline">{aff['tagline']}</div>
    </div>
    <span class="verdict-badge">{aff['badge']}</span>
  </div>
  <div class="verdict-stats">
    <div class="vstat"><div class="vstat-lbl">{L['rating']}</div><div class="vstat-val"><span class="stars" aria-label="{aff['rating']} out of 5">{stars_html}</span> <strong>{aff['rating']}</strong></div><div class="vstat-sub">{L['based_on'].format(reviews=aff['reviews'])}</div></div>
    <div class="vstat"><div class="vstat-lbl">{L['price']}</div><div class="vstat-val"><strong>{aff['price']}</strong></div><div class="vstat-sub">{aff['category']}</div></div>
    <div class="vstat"><div class="vstat-lbl">{L['best_for']}</div><div class="vstat-val"><strong>{L['founders_choice']}</strong></div><div class="vstat-sub">B2B / SaaS</div></div>
  </div>
  <a class="verdict-cta" href="{aff_url}" rel="sponsored noopener" target="_blank">
    {cta_get} →
  </a>
  <div class="verdict-tiny">{L['disclosure_title']} · {L['last_updated']} {date_str}</div>
</aside>
"""

    # ─── Sticky sidebar CTA (desktop) ───
    sticky_card = f"""
<aside class="sticky-card" aria-label="{cta_get}">
  <div class="sc-icon">{aff['logo']}</div>
  <div class="sc-brand">{brand1}</div>
  <div class="sc-rating"><span class="stars">{stars_html}</span> {aff['rating']}/5</div>
  <div class="sc-price">{aff['price']}</div>
  <div class="sc-badge">{aff['badge']}</div>
  <a class="sc-cta" href="{aff_url}" rel="sponsored noopener" target="_blank">{cta_main}</a>
  <a class="sc-cta-secondary" href="{aff_url}" rel="sponsored noopener" target="_blank">{cta_free}</a>
  <div class="sc-tiny">{L['disclosure_title']}</div>
</aside>
"""

    # ─── Mobile bottom sticky CTA ───
    mobile_cta = f"""
<div class="mobile-cta" role="region" aria-label="{cta_main}">
  <div class="mc-info">
    <div class="mc-brand"><span class="mc-logo">{aff['logo']}</span>{brand1}</div>
    <div class="mc-rating">{stars_html} {aff['rating']} · {aff['price']}</div>
  </div>
  <a class="mc-btn" href="{aff_url}" rel="sponsored noopener" target="_blank">{cta_main}</a>
</div>
"""

    # ─── Disclosure block ───
    disclosure_block = f"""
<div class="disclosure" role="note">
  <strong>{L['disclosure_title']}.</strong> {L['disclosure']}
</div>
"""

    # ─── Mid-article CTA ───
    mid_cta = f"""
<div class="mid-cta">
  <div class="mc2-text"><strong>{cta_get}</strong> — {aff['badge']}. {aff['tagline']}.</div>
  <a class="mc2-btn" href="{aff_url}" rel="sponsored noopener" target="_blank">{cta_free}</a>
</div>
"""

    # ─── Footer affiliate links (all tools) ───
    footer_items = ""
    for brand, data in AFFILIATE.items():
        if brand.lower() == "invideo":  # skip duplicate
            continue
        footer_items += (
            f'<li><a href="{data["url"]}" rel="sponsored noopener" target="_blank">'
            f'<span class="fi-icon">{data["logo"]}</span>'
            f'<span class="fi-text"><strong>{brand}</strong><span class="fi-tag">{data["tagline"]}</span></span>'
            f'<span class="fi-arrow">→</span></a></li>'
        )

    footer_tools = f"""
<section class="more-tools">
  <h3>{L['more_tools']}</h3>
  <ul class="ft-list">{footer_items}</ul>
</section>
"""

    # ─── Review schema ───
    review_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Review",
        "itemReviewed": {
            "@type": "SoftwareApplication",
            "name": brand1,
            "applicationCategory": aff["category"],
            "offers": {"@type": "Offer", "price": aff["price"], "priceCurrency": "USD"},
        },
        "reviewRating": {
            "@type": "Rating",
            "ratingValue": aff["rating"],
            "bestRating": "5",
        },
        "author": {"@type": "Organization", "name": "AIBuilder Marketplace"},
        "datePublished": date_str,
        "dateModified": date_str,
        "name": title,
        "url": url,
    })

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": L["home"], "item": DOMAIN},
            {"@type": "ListItem", "position": 2, "name": L["breadcrumb_reviews"], "item": f"{DOMAIN}/b2b/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url},
        ],
    })

    og_image = f"{DOMAIN}/assets/og-default.png"

    # Volledige HTML
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-CW1KZ258ZV"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-CW1KZ258ZV');
  </script>
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
  <script type="application/ld+json">{breadcrumb_schema}</script>
  <script type="application/ld+json">{review_schema}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *,*::before,*::after{{box-sizing:border-box}}
    :root{{--bg:#0a0e17;--bg2:#0f172a;--card:#111827;--card2:#1a2238;--border:#1e293b;--text:#f1f5f9;--text2:#cbd5e1;--muted:#94a3b8;--accent:{accent};--accent-soft:{accent}22}}
    html{{scroll-behavior:smooth}}
    body{{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);margin:0;padding:0;line-height:1.75;-webkit-font-smoothing:antialiased}}
    a{{color:var(--accent);text-decoration:none;transition:opacity .15s}}
    a:hover{{opacity:.85}}

    .topnav{{background:rgba(10,14,23,.92);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:0 24px;position:sticky;top:0;z-index:100}}
    .topnav-inner{{max-width:1180px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:56px}}
    .topnav-logo{{font-weight:800;font-size:.95rem;color:var(--text)}}
    .topnav-logo span{{background:linear-gradient(135deg,#3b82f6,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
    .topnav-links a{{color:var(--text2);font-size:.85rem;font-weight:500;margin-left:20px}}
    .topnav-links a:hover{{color:var(--text)}}

    .layout{{max-width:1180px;margin:0 auto;padding:0 24px;display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:40px}}
    @media(max-width:980px){{.layout{{grid-template-columns:1fr;gap:0}}}}
    .main{{min-width:0}}

    .breadcrumb{{margin:24px 0 0;font-size:.82rem;color:var(--muted)}}
    .breadcrumb a{{color:var(--text2)}}

    .article-header{{padding:24px 0 0}}
    .article-header h1{{font-size:clamp(1.6rem,4vw,2.4rem);font-weight:800;line-height:1.2;margin:0 0 16px;letter-spacing:-.02em;color:var(--text)}}
    .article-meta{{display:flex;gap:16px;align-items:center;color:var(--muted);font-size:.82rem;margin-bottom:24px;flex-wrap:wrap}}
    .article-meta .tag{{background:var(--accent-soft);color:var(--accent);padding:4px 12px;border-radius:20px;font-weight:600;font-size:.75rem;border:1px solid var(--accent-soft)}}

    .disclosure{{background:#0c1426;border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:8px;padding:12px 16px;margin:0 0 24px;font-size:.82rem;color:var(--text2);line-height:1.6}}
    .disclosure strong{{color:var(--text)}}

    .verdict-card{{background:linear-gradient(180deg,var(--card),var(--card2));border:1px solid var(--border);border-radius:16px;padding:24px;margin:0 0 32px;box-shadow:0 4px 24px rgba(0,0,0,.2)}}
    .verdict-top{{display:flex;align-items:center;gap:14px;margin-bottom:18px;flex-wrap:wrap}}
    .verdict-icon{{font-size:2.4rem;line-height:0;display:inline-flex;align-items:center}}
    .verdict-meta{{flex:1;min-width:0}}
    .verdict-brand{{font-size:1.2rem;font-weight:800;color:var(--text)}}
    .verdict-tagline{{font-size:.85rem;color:var(--muted);margin-top:2px}}
    .verdict-badge{{background:var(--accent-soft);color:var(--accent);border:1px solid var(--accent);font-size:.72rem;font-weight:700;padding:5px 11px;border-radius:99px;text-transform:uppercase;letter-spacing:.04em;white-space:nowrap}}
    .verdict-stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px;padding:14px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}}
    .vstat-lbl{{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;font-weight:600}}
    .vstat-val{{font-size:.95rem;color:var(--text);margin-top:4px;line-height:1.3}}
    .vstat-val strong{{color:var(--text);font-weight:700}}
    .vstat-sub{{font-size:.72rem;color:var(--muted);margin-top:2px}}
    .stars{{color:#fbbf24;letter-spacing:1px;font-size:.95rem}}
    .verdict-cta{{display:block;text-align:center;background:var(--accent);color:#0a0e17;font-weight:800;font-size:1rem;padding:14px 24px;border-radius:10px;text-decoration:none;transition:transform .15s,box-shadow .15s}}
    .verdict-cta:hover{{transform:translateY(-1px);box-shadow:0 6px 20px var(--accent-soft);opacity:1}}
    .verdict-tiny{{margin-top:10px;font-size:.7rem;color:var(--muted);text-align:center}}

    .toc{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 22px;margin:0 0 32px}}
    .toc-title{{font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:10px}}
    .toc ol{{margin:0;padding-left:20px;color:var(--text2)}}
    .toc li{{margin:6px 0;font-size:.9rem}}
    .toc a{{color:var(--text2);transition:color .15s}}
    .toc a:hover{{color:var(--accent);opacity:1}}

    .article-body{{padding:0 0 40px}}
    .article-body h2{{color:var(--text);font-size:1.45rem;font-weight:700;margin:44px 0 18px;padding-bottom:10px;border-bottom:1px solid var(--border);scroll-margin-top:80px}}
    .article-body h3{{color:var(--text);font-size:1.12rem;font-weight:600;margin:32px 0 14px;scroll-margin-top:80px}}
    .article-body p{{color:var(--text2);margin:0 0 16px;font-size:1rem}}
    .article-body ul,.article-body ol{{color:var(--text2);padding-left:24px;margin:0 0 16px}}
    .article-body li{{margin:8px 0;font-size:.98rem}}
    .article-body strong{{color:var(--text)}}
    .article-body blockquote{{border-left:3px solid var(--accent);margin:24px 0;padding:14px 20px;background:var(--card);border-radius:0 8px 8px 0;color:var(--text2);font-style:italic}}
    .article-body table{{width:100%;border-collapse:collapse;margin:24px 0;font-size:.92rem;border:1px solid var(--border);border-radius:8px;overflow:hidden}}
    .article-body th{{background:var(--card);color:var(--text);padding:12px 16px;text-align:left;font-weight:600;border-bottom:1px solid var(--border)}}
    .article-body td{{padding:12px 16px;border-top:1px solid var(--border);color:var(--text2)}}
    .article-body tr:hover td{{background:var(--card)}}
    .article-body code{{background:var(--card);color:var(--accent);padding:2px 8px;border-radius:4px;font-size:.88em}}
    .article-body pre{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px;overflow-x:auto;margin:16px 0}}
    .article-body img{{max-width:100%;border-radius:8px;margin:16px 0}}

    .mid-cta{{background:linear-gradient(135deg,var(--card),var(--card2));border:1px solid var(--accent);border-radius:12px;padding:20px 24px;margin:32px 0;display:flex;align-items:center;gap:20px;flex-wrap:wrap}}
    .mc2-text{{flex:1;min-width:0;color:var(--text2);font-size:.95rem}}
    .mc2-text strong{{color:var(--text)}}
    .mc2-btn{{background:var(--accent);color:#0a0e17;font-weight:700;padding:11px 22px;border-radius:8px;white-space:nowrap;font-size:.92rem}}
    .mc2-btn:hover{{opacity:1;transform:translateY(-1px)}}

    .more-tools{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px;margin:40px 0}}
    .more-tools h3{{margin:0 0 16px;color:var(--text);font-size:1.05rem;font-weight:700}}
    .ft-list{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}}
    .ft-list a{{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid var(--border);border-radius:8px;background:var(--bg2);transition:all .15s}}
    .ft-list a:hover{{border-color:var(--accent);transform:translateY(-1px);opacity:1}}
    .fi-icon{{font-size:1.5rem;line-height:0;display:inline-flex;align-items:center;flex-shrink:0}}
    .fi-text{{display:flex;flex-direction:column;flex:1;min-width:0}}
    .fi-text strong{{color:var(--text);font-size:.88rem;font-weight:700}}
    .fi-tag{{color:var(--muted);font-size:.74rem;margin-top:2px}}
    .fi-arrow{{color:var(--accent);font-weight:700}}

    .sticky-card{{position:sticky;top:80px;align-self:start;background:linear-gradient(180deg,var(--card),var(--card2));border:1px solid var(--border);border-radius:14px;padding:22px 20px;text-align:center;margin-top:24px;box-shadow:0 4px 24px rgba(0,0,0,.18)}}
    @media(max-width:980px){{.sticky-card{{display:none}}}}
    .sc-icon{{font-size:2.2rem;margin-bottom:10px;line-height:0;display:flex;justify-content:center}}
    .sc-brand{{font-size:1.05rem;font-weight:800;color:var(--text);margin-bottom:6px}}
    .sc-rating{{color:var(--muted);font-size:.82rem;margin-bottom:6px}}
    .sc-rating .stars{{font-size:.92rem}}
    .sc-price{{color:var(--text);font-weight:700;font-size:.92rem;margin-bottom:6px}}
    .sc-badge{{display:inline-block;background:var(--accent-soft);color:var(--accent);border:1px solid var(--accent);font-size:.7rem;font-weight:700;padding:3px 10px;border-radius:99px;margin-bottom:16px;text-transform:uppercase;letter-spacing:.04em}}
    .sc-cta{{display:block;background:var(--accent);color:#0a0e17;font-weight:800;padding:12px 16px;border-radius:8px;font-size:.92rem;margin-bottom:8px;text-decoration:none}}
    .sc-cta:hover{{opacity:1;transform:translateY(-1px)}}
    .sc-cta-secondary{{display:block;color:var(--accent);font-weight:600;padding:8px;font-size:.84rem;text-decoration:none}}
    .sc-tiny{{margin-top:8px;font-size:.7rem;color:var(--muted)}}

    .mobile-cta{{display:none;position:fixed;left:0;right:0;bottom:0;background:rgba(10,14,23,.96);backdrop-filter:blur(20px);border-top:1px solid var(--border);padding:10px 14px;z-index:90;align-items:center;gap:12px;box-shadow:0 -4px 24px rgba(0,0,0,.4)}}
    @media(max-width:980px){{.mobile-cta{{display:flex}}body{{padding-bottom:72px}}}}
    .mc-info{{flex:1;min-width:0}}
    .mc-brand{{color:var(--text);font-weight:700;font-size:.88rem;display:flex;align-items:center;gap:6px}}
    .mc-logo{{font-size:1.1rem;line-height:0}}
    .mc-rating{{color:var(--muted);font-size:.72rem}}
    .mc-rating .stars{{font-size:.78rem}}
    .mc-btn{{background:var(--accent);color:#0a0e17;font-weight:800;padding:10px 16px;border-radius:8px;white-space:nowrap;font-size:.88rem;text-decoration:none}}

    .article-footer{{padding:0 0 40px}}
    footer.site{{background:var(--bg2);border-top:1px solid var(--border);padding:32px 24px;text-align:center;color:var(--muted);font-size:.82rem;margin-top:40px}}
    footer.site a{{color:var(--text2)}}

    @media(max-width:640px){{
      .topnav-links{{display:none}}
      .article-header h1{{font-size:1.55rem}}
      .verdict-stats{{grid-template-columns:1fr;gap:10px}}
      .verdict-card{{padding:18px}}
    }}
  </style>
</head>
<body>
  <nav class="topnav"><div class="topnav-inner">
    <a href="/" class="topnav-logo"><span>AIBuilder</span> Marketplace</a>
    <div class="topnav-links"><a href="/b2b/">{L['all_reviews']}</a><a href="/">{L['home']}</a></div>
  </div></nav>

  <div class="layout">
    <main class="main">
      <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="/">{L['home']}</a> &rsaquo; <a href="/b2b/">{L['breadcrumb_reviews']}</a> &rsaquo; {title}
      </nav>
      <header class="article-header">
        <h1>{title}</h1>
        <div class="article-meta">
          <span class="tag">{brand1}</span>
          <span>{date_str}</span>
          <span>{rt} {L['reading_time']}</span>
        </div>
      </header>

      {disclosure_block}
      {quick_verdict}
      {toc_html}

      <article class="article-body">
        {content_with_ids}
        {mid_cta}
        {internal_links_html}
        {_wf_box(brand1)}
      </article>

      <div class="article-footer">{footer_tools}</div>
    </main>

    {sticky_card}
  </div>

  {mobile_cta}

  <footer class="site">
    <p>&copy; 2025-2026 <a href="/">AIBuilder Marketplace</a> · <a href="/terms/">Terms</a> · <a href="mailto:felix@theweekly2pctedge.com">Contact</a></p>
    <p style="margin-top:8px;font-size:.74rem">{L['disclosure']}</p>
  </footer>
</body>
</html>"""


# Aliassen voor backwards compat
build_article_html = build_article_html_v2
