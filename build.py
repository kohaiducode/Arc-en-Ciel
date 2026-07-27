import os
import json
import re
import shutil

# Configuration
SRC_DIR = 'src'
OUT_DIR = 'docs'
LANGUAGES = ['fr', 'en']
DEFAULT_LANG = 'fr'
BASE_PATH = '/Arc-en-Ciel'  # Change to '' if using a custom domain later

def load_json(lang, filename):
    path = os.path.join(SRC_DIR, 'translations', lang, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def render_template(template_str, data):
    """Remplace les variables {{key.subkey}} par leur valeur dans 'data'."""
    def replace(match):
        keys = match.group(1).strip().split('.')
        val = data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k, '')
            else:
                val = ''
        return str(val) if val is not None else ''
    
    return re.sub(r'\{\{\s*([\w\.]+)\s*\}\}', replace, template_str)

def generate_json_ld(global_data, reviews, lang_url):
    """Génère les données structurées SEO (Hotel)."""
    avg_rating = sum(r.get('rating', 5) for r in reviews) / len(reviews) if reviews else 5
    
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": global_data.get('hotel_name', ''),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": global_data.get('address', '')
        },
        "telephone": global_data.get('phone', ''),
        "email": global_data.get('email', ''),
        "url": lang_url,
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": round(avg_rating, 1),
            "reviewCount": len(reviews)
        }
    }
    return json.dumps(json_ld, ensure_ascii=False)

def build_site():
    print(f"-> Début de la compilation du site dans '{OUT_DIR}'...")
    
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)
    
    assets_src = os.path.join(SRC_DIR, 'assets')
    if os.path.exists(assets_src):
        shutil.copytree(assets_src, os.path.join(OUT_DIR, 'assets'))
        
    admin_src = os.path.join(SRC_DIR, 'admin')
    if os.path.exists(admin_src):
        shutil.copytree(admin_src, os.path.join(OUT_DIR, 'admin'))

    with open(os.path.join(SRC_DIR, 'templates', 'layout.html'), 'r', encoding='utf-8') as f:
        layout_html = f.read()
    with open(os.path.join(SRC_DIR, 'templates', 'header.html'), 'r', encoding='utf-8') as f:
        header_html = f.read()
    with open(os.path.join(SRC_DIR, 'templates', 'footer.html'), 'r', encoding='utf-8') as f:
        footer_html = f.read()

    pages = ['index', 'chambres', 'services', 'galerie', 'contact']
    sitemap_urls = []
    base_url = "https://arc-en-ciel.com" 
    
    for lang in LANGUAGES:
        print(f"-> Génération de la langue: {lang}")
        lang_dir = os.path.join(OUT_DIR, lang)
        os.makedirs(lang_dir, exist_ok=True)
        
        global_data = load_json(lang, 'global.json')
        pages_data = load_json(lang, 'pages.json')
        rooms_data = load_json(lang, 'rooms.json')
        reviews_data = load_json(lang, 'reviews.json')
        
        hreflang_tags = ""
        for l in LANGUAGES:
            hreflang_tags += f'<link rel="alternate" hreflang="{l}" href="{base_url}/{l}/" />\n'
        hreflang_tags += f'<link rel="alternate" hreflang="x-default" href="{base_url}/{DEFAULT_LANG}/" />'

        for page in pages:
            page_src_path = os.path.join(SRC_DIR, 'pages', f"{page}.html")
            if not os.path.exists(page_src_path):
                continue
            with open(page_src_path, 'r', encoding='utf-8') as f:
                content_html = f.read()
            
            page_context = pages_data.get(page, {})
            json_ld = generate_json_ld(global_data, reviews_data, f"{base_url}/{lang}/")
            
            # Générer le HTML dynamique (pour les listes, on pourrait utiliser un vrai moteur, mais on fait simple)
            rooms_html = ""
            if type(rooms_data) is list:
                for r in rooms_data:
                    amenities_html = "".join([f"<li>{a}</li>" for a in r.get('amenities', [])])
                    rooms_html += f"""
                    <div class="room-card">
                        <img src="{BASE_PATH}/assets/images/{r.get('image', '')}" alt="{r.get('name', '')}" loading="lazy">
                        <div class="room-card-content">
                            <h3>{r.get('name', '')}</h3>
                            <p class="room-meta"><span>{r.get('area_sqm', '')} m²</span> | <span>{r.get('capacity', '')} personnes</span></p>
                            <ul class="room-amenities">{amenities_html}</ul>
                            <a href="{global_data.get('booking_url', '#')}" class="btn-primary" target="_blank" rel="noopener">{r.get('cta_text', 'Réserver')}</a>
                        </div>
                    </div>
                    """
                    
            reviews_html = ""
            if type(reviews_data) is list:
                for r in reviews_data:
                    stars = "★" * r.get('rating', 5) + "☆" * (5 - r.get('rating', 5))
                    reviews_html += f"""
                    <div class="review-card">
                        <div class="review-stars">{stars}</div>
                        <h4>{r.get('title', '')}</h4>
                        <p>"{r.get('text', '')}"</p>
                        <p class="review-author">- {r.get('author', '')}</p>
                    </div>
                    """

            context = {
                "global": global_data,
                "page": page_context,
                "lang": lang,
                "seo_hreflang": hreflang_tags,
                "seo_json_ld": json_ld,
                "rooms_html": rooms_html,
                "reviews_html": reviews_html,
                "base_path": BASE_PATH
            }
            
            # Pre-render header and footer so their variables are evaluated
            context["header"] = render_template(header_html, context)
            context["footer"] = render_template(footer_html, context)
            
            rendered_content = render_template(content_html, context)
            context["content"] = rendered_content
            
            final_html = render_template(layout_html, context)
            
            page_out_dir = lang_dir if page == 'index' else os.path.join(lang_dir, page)
            os.makedirs(page_out_dir, exist_ok=True)
            out_file = os.path.join(page_out_dir, 'index.html')
            
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(final_html)
                
            sitemap_urls.append(f"{base_url}/{lang}/{'' if page == 'index' else page + '/'}")

    redirect_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Redirecting...</title>
    <script>
        var lang = navigator.language || navigator.userLanguage;
        lang = lang.substring(0, 2);
        var supported = {json.dumps(LANGUAGES)};
        var defaultLang = "{DEFAULT_LANG}";
        var redirectLang = supported.includes(lang) ? lang : defaultLang;
        window.location.href = "{BASE_PATH}/" + redirectLang + "/";
    </script>
</head>
<body>
    <a href="{BASE_PATH}/{DEFAULT_LANG}/">Continuer vers le site</a>
</body>
</html>'''
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(redirect_html)

    with open(os.path.join(OUT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n')
        for url in sitemap_urls:
            f.write(f'  <url>\\n    <loc>{url}</loc>\\n  </url>\\n')
        f.write('</urlset>')

    with open(os.path.join(OUT_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(f"User-agent: *\\nAllow: /\\nSitemap: {base_url}/sitemap.xml\\n")

    # Add .nojekyll for GitHub Pages
    with open(os.path.join(OUT_DIR, '.nojekyll'), 'w') as f:
        pass
    
    print("OK: Site généré avec succès !")

if __name__ == "__main__":
    build_site()
