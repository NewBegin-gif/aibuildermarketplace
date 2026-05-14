import os
import glob

old_id = "G-XXXXXXXXXX"
new_id = "G-CW1KZ258ZV"

html_files = glob.glob("**/*.html", recursive=True)
replaced = 0
not_found = 0

for file_path in html_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if old_id in content:
            new_content = content.replace(old_id, new_id)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            replaced += 1
        else:
            not_found += 1
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        not_found += 1

print(f"✅ Replaced tracking ID in: {replaced} files")
print(f"⚠️ No placeholder found in: {not_found} files")
print(f"📊 Total files scanned: {len(html_files)}")
