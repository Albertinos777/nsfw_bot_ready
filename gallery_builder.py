import os

def build_gallery(content_list, output_folder="output"):
    os.makedirs(output_folder, exist_ok=True)
    html_path = os.path.join(output_folder, "gallery.html")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("""
<html><head><meta charset='utf-8'>
<style>
    body { background:#111; color:#eee; font-family:sans-serif; padding:20px; }
    .item { display:inline-block; margin:10px; width:240px; vertical-align:top; }
    .item img { width:220px; height:auto; border-radius:5px; }
    .title { font-size:14px; margin:5px 0; max-width:220px; word-wrap:break-word; }
    .btn { background:#222; color:#0f0; padding:5px; display:block; text-align:center; text-decoration:none; margin-top:5px; border-radius:4px; }
    .btn:hover { background:#0f0; color:#000; }
</style></head><body>
<h1>Galleria NSFW – clicca per download diretto</h1>
""")

        for i, item in enumerate(content_list):
            f.write(f"""
<div class='item'>
    <a href='{item['link']}' download target='_blank'>
        <img src='{item['thumb']}' alt='preview'>
    </a>
    <div class='title'>{item['title']}</div>
    <a class='btn' href='{item['link']}' download target='_blank'>📥 Scarica</a>
</div>
""")

        f.write("</body></html>")
    
    print(f"[+] Galleria aggiornata in: {html_path}")
