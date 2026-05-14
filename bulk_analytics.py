import os
import glob

analytics_code = """    <!-- Google Analytics 4 + Affiliate Tracking -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag("js", new Date());
        gtag("config", "G-XXXXXXXXXX");
    </script>"""

html_files = glob.glob("**/*.html", recursive=True)
processed = 0
skipped = 0

for file_path in html_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "gtag" not in content and "</head>" in content:
            new_content = content.replace("</head>", analytics_code + "\n</head>")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            processed += 1
        else:
            skipped += 1
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        skipped += 1

print(f"✅ Processed: {processed} files")
print(f"⚠️ Skipped: {skipped} files (already had analytics or no </head>)")
print(f"📊 Total files: {len(html_files)}")
