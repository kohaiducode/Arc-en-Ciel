import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader
from csscompressor import compress

def load_data(locale, base_dir):
    data_dir = os.path.join(base_dir, "data")
    with open(os.path.join(data_dir, f"{locale}.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def build_site():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(base_dir, "src")
    docs_dir = os.path.join(base_dir, "docs")
    data_dir = os.path.join(base_dir, "data")
    
    # Load Jinja2 environment
    env = Environment(loader=FileSystemLoader(os.path.join(src_dir, "templates")))
    
    # Define locales based on available json files
    locales = [f.split('.')[0] for f in os.listdir(data_dir) if f.endswith('.json')]
    
    # Pages to generate
    pages = ["index", "rooms", "location", "contact"]
    site_url = ""
    sitemap_urls = []

    for locale in locales:
        data = load_data(locale, base_dir)
        site_url = data.get("site_url", "https://votresite.github.io/arc-en-ciel")
        
        locale_dir = os.path.join(docs_dir, locale)
        os.makedirs(locale_dir, exist_ok=True)
        
        for page in pages:
            template = env.get_template(f"{page}.html")
            html_content = template.render(
                locale=locale,
                locales=locales,
                data=data,
                page_name=page
            )
            
            output_file = os.path.join(locale_dir, f"{page}.html")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"Generated {output_file}")
            
            # Add to sitemap
            sitemap_urls.append({
                "loc": f"{site_url}/{locale}/{page}.html",
                "hreflang": locale
            })

    # Generate sitemap.xml
    sitemap_template = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
{% for url in urls %}
  <url>
    <loc>{{ url.loc }}</loc>
    {% for l in locales %}
    <xhtml:link rel="alternate" hreflang="{{ l }}" href="{{ site_url }}/{{ l }}/{{ url.loc.split('/')[-1] }}" />
    {% endfor %}
    <xhtml:link rel="alternate" hreflang="x-default" href="{{ site_url }}/fr/{{ url.loc.split('/')[-1] }}" />
  </url>
{% endfor %}
</urlset>"""
    sitemap_env = Environment()
    sitemap_rendered = sitemap_env.from_string(sitemap_template).render(urls=sitemap_urls, locales=locales, site_url=site_url)
    with open(os.path.join(docs_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_rendered)
    
    # Generate robots.txt
    robots_content = f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n"
    with open(os.path.join(docs_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_content)
        
    # Generate root index.html (redirect)
    redirect_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Hôtel Arc en Ciel</title>
    <script>
        var lang = navigator.language || navigator.userLanguage;
        if (lang.startsWith('fr')) {
            window.location.href = './fr/index.html';
        } else {
            window.location.href = './en/index.html';
        }
    </script>
</head>
<body>
    <p>Redirection en cours... <a href="./fr/index.html">Français</a> | <a href="./en/index.html">English</a></p>
</body>
</html>"""
    with open(os.path.join(docs_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(redirect_html)

    # Copy and minify CSS
    css_src = os.path.join(src_dir, "css")
    css_dest = os.path.join(docs_dir, "assets", "css")
    os.makedirs(css_dest, exist_ok=True)
    
    for file in os.listdir(css_src):
        if file.endswith(".css"):
            with open(os.path.join(css_src, file), "r", encoding="utf-8") as f:
                css_content = f.read()
            minified_css = compress(css_content)
            with open(os.path.join(css_dest, file), "w", encoding="utf-8") as f:
                f.write(minified_css)
            print(f"Minified and copied {file}")
            
    print("Build complete!")

if __name__ == "__main__":
    build_site()
