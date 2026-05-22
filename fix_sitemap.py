#!/usr/bin/env python3
import os
import datetime

print("Starting sitemap generation...")

base_url = "https://aibuildermarketplace.com"
today = datetime.date.today().strftime("%Y-%m-%d")

html_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".html") and "backup" not in file:
            path = os.path.join(root, file)[2:]
            html_files.append(path)

html_files.sort()
print(f"Found {len(html_files)} HTML files")

sitemap = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>"]
sitemap.append("<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">")

for html_file in html_files:
    if html_file == "index.html":
        url = f"{base_url}/"
        priority = "1.0"
    elif html_file.endswith("/index.html"):
        url_path = html_file[:-11]
        url = f"{base_url}/{url_path}/"
        priority = "0.8"
    else:
        url = f"{base_url}/{html_file}"
        priority = "0.7"
    
    if "/b2b/" in html_file:
        priority = "0.9"
    
    sitemap.append("  <url>")
    sitemap.append(f"    <loc>{url}</loc>")
    sitemap.append(f"    <lastmod>{today}</lastmod>")
    sitemap.append(f"    <priority>{priority}</priority>")
    sitemap.append("  </url>")

sitemap.append("</urlset>")

with open("sitemap_new.xml", "w") as f:
    f.write("\n".join(sitemap))

print(f"Generated sitemap_new.xml with {len(html_files)} URLs")
