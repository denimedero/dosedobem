#!/usr/bin/env python3
"""Monta o site a partir de src/page.html e gera os feeds da Alexa a partir de noticias.json.

Uso: python3 tools/build.py   (rodar na raiz do repositório)
"""
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dosedobem.com.br/"

HEAD = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Dose do Bem: notícias boas do dia, checadas e com fonte. Uma dose por dia, em português, español e English.">
<meta property="og:title" content="Dose do Bem">
<meta property="og:description" content="Notícias boas, checadas e com fonte. Uma dose por dia.">
<meta property="og:image" content="{site}icons/icon-512.png">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Dose do Bem">
<link rel="alternate" hreflang="pt-BR" href="{site}">
<link rel="alternate" hreflang="es" href="{site}?lang=es">
<link rel="alternate" hreflang="en" href="{site}?lang=en">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
""".format(site=SITE)

LANGS = {
    "pt": dict(brand="Dose do Bem", loc="pt-BR",
               intro="Esta é a Dose do Bem de {d}. São {n} notícias boas.",
               ords="Primeira|Segunda|Terceira|Quarta|Quinta".split("|"),
               outro="Essa foi a sua dose de hoje. Até amanhã!",
               months="janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split(),
               days="segunda-feira terça-feira quarta-feira quinta-feira sexta-feira sábado domingo".split(),
               date="{wd}, {d} de {m}"),
    "es": dict(brand="Dosis de Bien", loc="es",
               intro="Esta es la Dosis de Bien del {d}. Son {n} noticias buenas.",
               ords="Primera|Segunda|Tercera|Cuarta|Quinta".split("|"),
               outro="Esa fue tu dosis de hoy. ¡Hasta mañana!",
               months="enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(),
               days="lunes martes miércoles jueves viernes sábado domingo".split(),
               date="{wd} {d} de {m}"),
    "en": dict(brand="Dose of Good", loc="en-US",
               intro="This is Dose of Good for {d}. Here are {n} good news stories.",
               ords="First|Second|Third|Fourth|Fifth".split("|"),
               outro="That was your dose for today. See you tomorrow!",
               months="January February March April May June July August September October November December".split(),
               days="Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split(),
               date="{wd}, {m} {d}"),
}


def pick_dose(items):
    """Mesma lógica do site: destaques primeiro, um por tema, até 5."""
    srt = sorted(items, key=lambda n: (0 if n.get("destaque") else 1, [-ord(c) for c in n["data"]]))
    out, seen = [], set()
    for n in srt:
        if n["categoria"] not in seen:
            out.append(n); seen.add(n["categoria"])
        if len(out) == 5:
            break
    for n in srt:
        if len(out) >= 5:
            break
        if n not in out:
            out.append(n)
    return out


def field(n, lang, k):
    if lang != "pt":
        v = (n.get("i18n") or {}).get(lang, {}).get(k)
        if v:
            return v
    return n[k]


def build_alexa(data):
    os.makedirs(os.path.join(ROOT, "alexa"), exist_ok=True)
    day = datetime.date.fromisoformat(data["atualizado"])
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.0Z")
    dose = pick_dose(data["noticias"])
    for lang, L in LANGS.items():
        d = L["date"].format(wd=L["days"][day.weekday()], d=day.day, m=L["months"][day.month - 1])
        parts = [L["intro"].format(d=d, n=len(dose))]
        for i, n in enumerate(dose):
            parts.append(f'{L["ords"][i]}: {field(n, lang, "titulo").rstrip(".")}. {field(n, lang, "resumo")}')
        parts.append(L["outro"])
        text = " ".join(parts)
        if len(text) > 4400:
            text = text[:4400].rsplit(". ", 1)[0] + "."
        feed = [{
            "uid": f"dosedobem-{lang}-{data['atualizado']}",
            "updateDate": now,
            "titleText": f'{L["brand"]}: {d}',
            "mainText": text,
            "redirectionUrl": SITE + ("" if lang == "pt" else f"?lang={lang}"),
        }]
        with open(os.path.join(ROOT, "alexa", f"{lang}.json"), "w", encoding="utf-8") as f:
            json.dump(feed, f, ensure_ascii=False, indent=1)


def build_page():
    page = open(os.path.join(ROOT, "src", "page.html"), encoding="utf-8").read()
    # src/page.html começa com <title>, metas e <style> (cabeçalho) e depois o conteúdo.
    cut = page.index("</style>") + len("</style>")
    head_part = page[:cut].replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    head_part = head_part.replace('<meta name="theme-color" content="#FFFFFF">', '<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">\n<meta name="theme-color" content="#0B0B0A" media="(prefers-color-scheme: dark)">')
    html = HEAD + head_part + "\n</head>\n<body>\n" + page[cut:] + "\n</body>\n</html>\n"
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)


SHARE_TPL = """<!doctype html>
<html lang="{hl}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | Dose do Bem</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Dose do Bem">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{img}">
<meta property="og:url" content="{self}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">
<link rel="canonical" href="{dest}">
<meta http-equiv="refresh" content="0;url={dest}">
<script>location.replace({dest_js});</script>
<style>body{{font:16px system-ui,sans-serif;margin:40px 20px;color:#0B0B0A}}a{{color:#B45F06}}</style>
</head>
<body><p><a href="{dest}">{title}</a></p></body>
</html>
"""


def build_share_pages(data):
    """Uma página leve por notícia (n/<id>/), com prévia (título, resumo, foto) para WhatsApp, X e Facebook.
    Ela redireciona na hora para o site com a notícia aberta. Páginas antigas ficam (links já compartilhados continuam funcionando)."""
    from html import escape
    for n in data["noticias"]:
        nid = n["id"]
        if not re.fullmatch(r"[a-z0-9-]+", nid):
            continue
        d = os.path.join(ROOT, "n", nid)
        os.makedirs(d, exist_ok=True)
        for lang, fname, hl in (("pt", "index.html", "pt-BR"), ("es", "es.html", "es"), ("en", "en.html", "en")):
            dest = f"{SITE}?n={nid}" + ("" if lang == "pt" else f"&lang={lang}")
            selfu = f"{SITE}n/{nid}/" + ("" if lang == "pt" else fname)
            html = SHARE_TPL.format(
                hl=hl, title=escape(field(n, lang, "titulo")), desc=escape(field(n, lang, "resumo")),
                img=escape(n.get("img") or SITE + "icons/icon-512.png"), self=escape(selfu),
                dest=escape(dest), dest_js=json.dumps(dest))
            open(os.path.join(d, fname), "w", encoding="utf-8").write(html)


if __name__ == "__main__":
    data = json.load(open(os.path.join(ROOT, "noticias.json"), encoding="utf-8"))
    build_page()
    build_alexa(data)
    build_share_pages(data)
    print("ok:", data["atualizado"], len(data["noticias"]), "notícias")
