"""Gera o kit diário para redes sociais: Reel (MP4), stories, carrossel e legendas.
Uso: python3 tools/social.py [pasta_saida]   (padrão: /mnt/project-files/dose-do-bem-social/AAAA-MM-DD)
"""
import json, os, sys, shutil, subprocess, datetime
sys.path.insert(0, os.path.dirname(__file__))
from build import pick_dose
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
MESES = ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
SITE = "dosedobem.com.br"

def main():
    data = json.load(open(os.path.join(ROOT, "noticias.json")))
    day = datetime.date.fromisoformat(data["atualizado"])
    out = sys.argv[1] if len(sys.argv) > 1 else f"/mnt/project-files/dose-do-bem-social/{day}"
    dose = pick_dose(data["noticias"])
    wd = day.weekday()
    dia = ("o " if wd >= 5 else "a ") + DIAS[wd] + ("" if wd >= 5 else "-feira")
    D = {"dose": [{k: n.get(k, "") for k in ("titulo", "resumo", "categoria", "regiao", "pais", "fonte")} for n in dose],
         "saud": "Bom dia", "dia": dia,
         "dataTxt": f"{DIAS[wd].capitalize()}{'' if wd >= 5 else '-feira'}, {day.day} de {MESES[day.month-1]}"}
    os.makedirs(out, exist_ok=True)
    dj = os.path.join(out, ".data.json"); json.dump(D, open(dj, "w"), ensure_ascii=False)
    here = os.path.join(ROOT, "tools", "social")
    subprocess.run(["node", os.path.join(here, "render.js"), dj, out, "--video"], check=True)
    fr = os.path.join(out, ".frames")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", "30", "-i", f"{fr}/%04d.png",
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "20", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", os.path.join(out, "reel.mp4")], check=True)
    shutil.rmtree(fr); os.remove(dj)
    # versão leve do Reel para o botão "Baixar o Reel do dia" do site
    os.makedirs(os.path.join(ROOT, "social"), exist_ok=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(out, "reel.mp4"), "-c:v", "libx264",
                    "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "27", "-c:a", "copy", "-movflags", "+faststart",
                    os.path.join(ROOT, "social", "reel.mp4")], check=True)
    lines = "\n".join(f"{i+1}. {n['titulo']}" for i, n in enumerate(dose))
    tags = "#notíciasboas #boasnotícias #bomdia #dosedobem #otimismo"
    ig = f"☀️ Bom dia! {len(dose)} notícias boas para começar {dia}:\n\n{lines}\n\nLeia todas, com a fonte original, no link da bio: {SITE}\nSalve e mande para alguém que precisa de uma notícia boa hoje 💛\n\n{tags}"
    fb = f"☀️ Bom dia! {len(dose)} notícias boas para começar {dia}:\n\n{lines}\n\nLeia todas no site, sempre com o link da fonte: https://{SITE}"
    top = dose[0]["titulo"]
    x = f"☀️ Bom dia! {len(dose)} notícias boas para começar {dia}. Hoje tem: {top}\n\nLeia a dose completa 👉 https://{SITE}"
    if len(x) > 280: x = f"☀️ Bom dia! {len(dose)} notícias boas para começar {dia}.\n\nLeia a dose completa 👉 https://{SITE}"
    wa = f"☀️ *Bom dia! Sua Dose do Bem de hoje:*\n\n{lines}\n\nLeia todas 👉 https://{SITE}"
    with open(os.path.join(out, "legendas.md"), "w") as f:
        f.write(f"# Legendas · {D['dataTxt']}\n\n## Instagram (Reel e carrossel)\n\n{ig}\n\n## Facebook\n\n{fb}\n\n## X ({len(x)} caracteres)\n\n{x}\n\n## WhatsApp (canal ou grupos)\n\n{wa}\n")
    print("ok:", out)

if __name__ == "__main__":
    main()
