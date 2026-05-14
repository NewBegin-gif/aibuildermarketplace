import os

# Check index.html
with open("index.html", "r") as f:
    content = f.read()

has_analytics = "gtag" in content
print(f"index.html: {len(content)} chars")
print(f"Has analytics: {has_analytics}")
print(f"Has </head>: {"</head>" in content}")
