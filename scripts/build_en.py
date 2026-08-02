#!/usr/bin/env python3
"""Genera la versión inglesa estática en /en/ a partir de las páginas españolas.

    python3 scripts/build_en.py

Por qué existe: hasta ago-2026 la web inglesa era la misma URL con `?lang=en`,
que devolvía un HTML idéntico al español y canonicalizaba hacia él. Es decir,
para Google no existía. Ahora cada página inglesa es un fichero propio con su
canonical, su hreflang recíproco y su texto ya horneado en inglés.

Qué hace con cada página española:

1. Traduce el texto horneado leyendo los `data-i18n*` y el diccionario de
   `content.json`, que es la fuente de la verdad de los textos.
2. Reescribe cabecera (title, description, canonical, hreflang, Open Graph),
   `<html lang>` y los bloques JSON-LD.
3. Apunta los enlaces internos a su equivalente inglés y los recursos a la raíz,
   porque las páginas inglesas viven un nivel más abajo.
4. Fija el idioma de la página: el selector ES/EN navega, ya no cambia un
   parámetro.

Es idempotente: se puede volver a ejecutar después de cada cambio en español.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = os.path.join(ROOT, "en")
BASE = "https://algoryme.com/"

# española -> inglesa (las rutas inglesas las fija el documento de SEO)
PAGINAS = {
    "index.html": "index.html",
    "servicio-aplicaciones-y-webs.html": "service-custom-apps-and-websites.html",
    "servicio-auditoria-adopcion-ia.html": "service-ai-adoption-audit.html",
    "servicio-automatizacion-de-procesos.html": "service-process-automation.html",
    "servicio-informes-automaticos.html": "service-automated-reports.html",
    "servicio-atencion-al-cliente.html": "service-customer-support.html",
    "servicio-chatbots-documentacion-interna.html": "service-internal-docs-chatbot.html",
    "servicio-dashboards-inteligencia-negocio.html": "service-dashboards-business-intelligence.html",
}
# legal.html y privacidad.html se quedan solo en español: su texto es jurídico y
# no está traducido. Las páginas inglesas enlazan a la versión española.

# textos sueltos que no llevan data-i18n y que en la web inglesa no pueden quedar en español
LITERALES = [
    ('aria-label="Principal"', 'aria-label="Main"'),
    ('aria-label="Principal (móvil)"', 'aria-label="Main (mobile)"'),
    ('aria-label="Mes anterior"', 'aria-label="Previous month"'),
    ('aria-label="Mes siguiente"', 'aria-label="Next month"'),
    ('content="Algoryme — consultoría de inteligencia artificial"',
     'content="Algoryme — custom software and AI automation"'),
    ('Activa JavaScript para reservar la llamada online. También puedes escribir a',
     'Turn on JavaScript to book the call online. You can also write to'),
    ('o escribirnos por <a href="https://wa.me/', 'or message us on <a href="https://wa.me/'),
]

CONTENT = json.load(open(os.path.join(ROOT, "content.json"), encoding="utf-8"))
E = lambda s: html.escape(s, quote=False)
EA = lambda s: html.escape(s, quote=True)


def url_es(f):
    return BASE if f == "index.html" else BASE + f


def url_en(f):
    destino = PAGINAS[f]
    return BASE + "en/" + ("" if destino == "index.html" else destino)


def resolve(dic, ruta):
    cur = dic
    for parte in ruta.split("."):
        if isinstance(cur, list):
            if not parte.isdigit() or int(parte) >= len(cur):
                return None
            cur = cur[int(parte)]
        elif isinstance(cur, dict) and parte in cur:
            cur = cur[parte]
        else:
            return None
    return cur if isinstance(cur, str) else None


def rich(texto):
    """Misma marca que renderRich() en el navegador: {{x}} -> <em class="mark">x</em>."""
    return re.sub(r"\{\{(.+?)\}\}", lambda m: '<em class="mark">%s</em>' % E(m.group(1)), E(texto))


def traducir_texto(src, en):
    """Sustituye el contenido de cada elemento con data-i18n por su versión inglesa.

    Los elementos con data-i18n solo llevan texto (applyI18n hace textContent),
    así que basta con reemplazar hasta su etiqueta de cierre.
    """
    def uno(m):
        apertura, tag, clave = m.group(0), m.group(1), m.group(2)
        v = resolve(en, clave)
        return apertura if v is None else apertura
    # data-i18n simple
    patron = re.compile(r'(<(\w+)[^>]*\bdata-i18n="([^"]+)"[^>]*>)(.*?)(</\2>)', re.S)

    def rep(m):
        v = resolve(en, m.group(3))
        return m.group(1) + (E(v) if v is not None else m.group(4)) + m.group(5)
    src = patron.sub(rep, src)

    # data-i18n-rich
    patron_r = re.compile(r'(<(\w+)[^>]*\bdata-i18n-rich="([^"]+)"[^>]*>)(.*?)(</\2>)', re.S)

    def rep_r(m):
        v = resolve(en, m.group(3))
        return m.group(1) + (rich(v) if v is not None else m.group(4)) + m.group(5)
    src = patron_r.sub(rep_r, src)

    # atributos: placeholder, aria-label y alt
    for attr_i18n, attr in (("data-i18n-placeholder", "placeholder"),
                            ("data-i18n-aria", "aria-label"),
                            ("data-i18n-alt", "alt")):
        patron_a = re.compile(r'(<\w+[^>]*\b%s="([^"]+)"[^>]*>)' % attr_i18n)

        def rep_a(m, attr=attr):
            v = resolve(en, m.group(2))
            if v is None:
                return m.group(1)
            return re.sub(r'(?<![-\w])%s="[^"]*"' % attr, '%s="%s"' % (attr, EA(v)), m.group(1), count=1)
        src = patron_a.sub(rep_a, src)
    return src


def traducir_jsonld(src, en, es, f):
    """Los bloques de datos estructurados también van en inglés y apuntan a URLs inglesas."""
    nombres = {}
    for i, item in enumerate(es["svc"]["items"]):
        nombres[item["name"]] = en["svc"]["items"][i]["name"]
    nombres.update({"Inicio": "Home", "Servicios": "Services",
                    es["nav"]["projects"]: en["nav"]["projects"]})
    faq_es = {q["q"]: (en["faq"]["items"][i]["q"], en["faq"]["items"][i]["a"])
              for i, q in enumerate(es["faq"]["items"])}

    def anda(v):
        if isinstance(v, dict):
            return {k: anda(x) for k, x in v.items()}
        if isinstance(v, list):
            return [anda(x) for x in v]
        if isinstance(v, str):
            if v in nombres:
                return nombres[v]
            if v in faq_es:
                return faq_es[v][0]
            for esp, ing in PAGINAS.items():
                if v.endswith("/" + esp):
                    return BASE + "en/" + ("" if ing == "index.html" else ing)
            return v
        return v

    def rep(m):
        try:
            d = json.loads(m.group(1))
        except Exception:
            return m.group(0)
        d = anda(d)
        # las respuestas del FAQ van dentro de acceptedAnswer.text
        if d.get("@type") == "FAQPage":
            for pregunta, orig in zip(d.get("mainEntity", []), es["faq"]["items"]):
                pregunta["acceptedAnswer"]["text"] = en["faq"]["items"][
                    [x["q"] for x in es["faq"]["items"]].index(orig["q"])]["a"]
        return '<script type="application/ld+json">%s</script>' % json.dumps(d, ensure_ascii=False)

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', rep, src, flags=re.S)


def construir(f):
    src = open(os.path.join(ROOT, f), encoding="utf-8").read()
    es, en = CONTENT["es"], CONTENT["en"]
    meta_key = re.search(r'var PAGE_META = "([^"]+)"', src).group(1)
    meta = CONTENT["meta"]["en"].get(meta_key) or CONTENT["meta"]["en"]["home"]

    for a, b in LITERALES:
        src = src.replace(a, b)
    src = traducir_texto(src, en)
    src = traducir_jsonld(src, en, es, f)

    # --- cabecera ---
    src = src.replace('<html lang="es">', '<html lang="en">', 1)
    src = re.sub(r"<title>.*?</title>", "<title>%s</title>" % EA(meta["title"]), src, count=1, flags=re.S)
    for attr, campo in (('name="description"', "description"),
                        ('property="og:title"', "title"),
                        ('property="og:description"', "description"),
                        ('name="twitter:title"', "title"),
                        ('name="twitter:description"', "description")):
        src = re.sub(r'<meta %s content="[^"]*">' % re.escape(attr),
                     '<meta %s content="%s">' % (attr, EA(meta[campo])), src, count=1)
    src = re.sub(r'<link rel="canonical" href="[^"]*">',
                 '<link rel="canonical" href="%s">' % url_en(f), src, count=1)
    src = re.sub(r'<link rel="alternate" hreflang="es" href="[^"]*">',
                 '<link rel="alternate" hreflang="es" href="%s">' % url_es(f), src, count=1)
    src = re.sub(r'<link rel="alternate" hreflang="en" href="[^"]*">',
                 '<link rel="alternate" hreflang="en" href="%s">' % url_en(f), src, count=1)
    src = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*">',
                 '<link rel="alternate" hreflang="x-default" href="%s">' % url_es(f), src, count=1)
    src = re.sub(r'<meta property="og:url" content="[^"]*">',
                 '<meta property="og:url" content="%s">' % url_en(f), src, count=1)
    src = src.replace('<meta property="og:locale" content="es_ES">',
                      '<meta property="og:locale" content="en_US">')
    src = src.replace('<meta property="og:locale:alternate" content="en_US">',
                      '<meta property="og:locale:alternate" content="es_ES">')

    # --- enlaces y recursos: las páginas inglesas cuelgan de /en/ ---
    for esp, ing in PAGINAS.items():
        if esp != "index.html":
            src = src.replace('href="%s"' % esp, 'href="%s"' % ing)
    src = src.replace('href="/"', 'href="/en/"').replace('href="/#', 'href="/en/#')
    src = src.replace('href="legal.html"', 'href="/legal.html"')
    src = src.replace('href="privacidad.html"', 'href="/privacidad.html"')
    for carpeta in ("casos/", "equipo/", "marca/"):
        src = src.replace('src="%s' % carpeta, 'src="/%s' % carpeta)
        src = src.replace('srcset="%s' % carpeta, 'srcset="/%s' % carpeta)

    # --- idioma fijado por la URL ---
    src = src.replace("var lang = 'es';", "var lang = 'en';", 1)
    ini = src.index("(function initLang(){")
    fin = src.index("})();", ini) + len("})();")
    src = src[:ini] + ("""(function initLang(){
  /* esta página es la inglesa: el idioma lo manda la URL, no el navegador */
  var qp = null;
  try { qp = new URLSearchParams(location.search).get('lang'); } catch(e){}
  if (qp === 'es' && typeof ALT_URL !== 'undefined' && ALT_URL.es){ location.replace(ALT_URL.es); return; }
  lang = 'en';
})();""") + src[fin:]
    src = re.sub(r'var ALT_URL = \{[^;]+\};',
                 'var ALT_URL = {"es":"%s","en":"%s"};' % (url_es(f), url_en(f)), src, count=1)

    os.makedirs(EN, exist_ok=True)
    destino = os.path.join(EN, PAGINAS[f])
    open(destino, "w", encoding="utf-8").write(src)
    return destino


def main():
    hechas = [construir(f) for f in PAGINAS]
    print("páginas inglesas generadas:", len(hechas))
    for h in hechas:
        print("  en/" + os.path.basename(h))


if __name__ == "__main__":
    main()
