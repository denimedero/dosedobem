# Dose do Bem

Notícias boas, checadas e com fonte. Uma dose por dia, em português, español e English.

Site: https://dosedobem.com.br/ (`?lang=es`, `?lang=en`)

## Arquivos
- `src/page.html`: o código do site (é daqui que se edita).
- `tools/build.py`: monta o `index.html` e gera os feeds da Alexa. Rode `python3 tools/build.py` depois de mudar o `src/page.html` ou o `noticias.json`.
- `noticias.json`: a edição do dia (com traduções em `i18n.es` e `i18n.en`), atualizada toda manhã.
- `alexa/pt.json`, `alexa/es.json`, `alexa/en.json`: feeds do Resumo de Notícias (Flash Briefing) da Alexa.
- `manifest.webmanifest`, `sw.js`, `icons/`: o site pode ser instalado como app e funciona offline.
