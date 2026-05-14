with open("index.html", "r") as f:
    content = f.read()

analytics_code = """    <!-- Google Analytics 4 + Affiliate Tracking -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag("js", new Date());
        gtag("config", "G-XXXXXXXXXX");
    </script>"""

new_content = content.replace("</head>", analytics_code + "\n</head>")

with open("index.html", "w") as f:
    f.write(new_content)

print("✅ Added GA4 to index.html")
print(f"New size: {len(new_content)} chars")
