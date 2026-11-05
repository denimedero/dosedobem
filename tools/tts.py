#!/usr/bin/env python3
"""Gera a "dose" em áudio (voz neural do Google Cloud Text-to-Speech) nos 3 idiomas.

Precisa da variável de ambiente GOOGLE_TTS_KEY. Sem ela, não faz nada.
Saída: audio/pt.mp3, audio/es.mp3, audio/en.mp3 e o campo "audio" em noticias.json
com o arquivo e o segundo em que começa cada notícia (para o player saber onde está).

Uso: python3 tools/tts.py   (depois rode tools/build.py)
"""
import base64, json, os, sys, urllib.request, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, LANGS, pick_dose, field
import datetime

KEY = os.environ.get("GOOGLE_TTS_KEY")
API = "https://texttospeech.googleapis.com/v1beta1/"
GREET = {"pt": "Bom dia!", "es": "¡Buenos días!", "en": "Good morning!"}
CODES = {"pt": "pt-BR", "es": "es-US", "en": "en-US"}
# preferência: vozes mais naturais que aceitam SSML com marcações
PREF = ["Neural2", "Wavenet", "Studio", "News", "Standard"]


def call(path, body=None):
    req = urllib.request.Request(API + path + ("&" if "?" in path else "?") + "key=" + KEY,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def best_voice(code, voices):
    cands = [v for v in voices if code in v["languageCodes"]]
    def rank(v):
        n = v["name"]
        for i, p in enumerate(PREF):
            if p in n:
                return (i, 0 if v.get("ssmlGender") == "FEMALE" else 1, n)
        return (99, 1, n)
    cands.sort(key=rank)
    return cands[0]["name"] if cands else None


def ssml_for(lang, data, dose):
    L = LANGS[lang]
    day = datetime.date.fromisoformat(data["atualizado"])
    d = L["date"].format(wd=L["days"][day.weekday()], d=day.day, m=L["months"][day.month - 1])
    e = html.escape
    parts = ['<speak>', e(GREET[lang]), '<break time="250ms"/>', e(L["intro"].format(d=d, n=len(dose))), '<break time="600ms"/>']
    for i, n in enumerate(dose):
        parts += [f'<mark name="n{i}"/>', e(L["ords"][i]) + ':', '<break time="200ms"/>',
                  e(field(n, lang, "titulo").rstrip(".")) + '.', '<break time="350ms"/>',
                  e(field(n, lang, "resumo")), '<break time="800ms"/>']
    parts += ['<mark name="end"/>', e(L["outro"]), '</speak>']
    return "".join(parts)


def main():
    if not KEY:
        print("GOOGLE_TTS_KEY não definida; áudios não gerados.")
        return
    path = os.path.join(ROOT, "noticias.json")
    data = json.load(open(path, encoding="utf-8"))
    dose = pick_dose(data["noticias"])
    voices = call("voices")["voices"]
    os.makedirs(os.path.join(ROOT, "audio"), exist_ok=True)
    out = {}
    for lang, code in CODES.items():
        name = best_voice(code, voices)
        res = call("text:synthesize", {
            "input": {"ssml": ssml_for(lang, data, dose)},
            "voice": {"languageCode": code, "name": name},
            "audioConfig": {"audioEncoding": "MP3", "speakingRate": 1.0, "effectsProfileId": ["handset-class-device"]},
            "enableTimePointing": ["SSML_MARK"],
        })
        open(os.path.join(ROOT, "audio", f"{lang}.mp3"), "wb").write(base64.b64decode(res["audioContent"]))
        marks = {tp["markName"]: round(tp["timeSeconds"], 2) for tp in res.get("timepoints", [])}
        out[lang] = {"src": f"audio/{lang}.mp3?v={data['atualizado']}", "voz": name,
                     "marcas": [marks.get(f"n{i}") for i in range(len(dose))], "fim": marks.get("end"),
                     "ids": [n["id"] for n in dose]}
        print(lang, name, out[lang]["marcas"])
    data["audio"] = out
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
