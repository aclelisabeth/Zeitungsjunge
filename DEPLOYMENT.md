# Zeitungsjunge - Deployment Guide

## GitHub Pages Setup (Manuell)

### 1. Repository Settings aktivieren

1. Gehe zu https://github.com/aclelisabeth/Zeitungsjunge
2. Settings → Pages
3. Wähle unter "Source":
   - **Branch:** master
   - **Folder:** /docs
4. Speichern!

→ Deine Seite wird dann verfügbar unter:
**https://aclelisabeth.github.io/Zeitungsjunge/**

### 2. Projektstruktur

```
Zeitungsjunge/
├── src/                    # Node.js Source Code
│   ├── config.js          # Konfiguration
│   ├── fetcher.js         # RSS + Web Scraping
│   ├── ranker.js          # Ranking Engine
│   ├── filter.js          # Zeitrahmen Filter
│   ├── output.js          # HTML/MD Generator
│   └── cli.js             # CLI Tool
├── docs/                  # 📍 GitHub Pages (deployed)
│   ├── index.html         # Dashboard
│   ├── today.html
│   ├── week.html
│   ├── month.html
│   └── quarter.html
├── output/                # Local generated files
│   ├── *.md
│   └── *.html
├── .github/workflows/
│   └── generate-headlines.yml  # GitHub Actions
├── package.json
└── README.md
```

## Verwendung

### CLI Commands

```bash
# Installieren
npm install

# Heute generieren
npm run scrape:today

# Letzte Woche
npm run scrape:week

# Letzte 30 Tage
npm run scrape:month

# Letzte 90 Tage  
npm run scrape -- --range quarter

# Alle verfügbaren Artikel
npm run scrape -- --range all

# Nur Markdown
npm run scrape -- --output md

# Nur HTML
npm run scrape -- --output html

# Custom Limit
npm run scrape -- --limit 10
```

### Automatische Updates (Optional)

GitHub Actions läuft täglich um 08:00 UTC und generiert Headlines neu.

**Workflow:** `.github/workflows/generate-headlines.yml`
- Automatisches Scraping
- Generiert alle Zeitrahmen
- Committed & pusht zu GitHub
- Updates GitHub Pages automatisch

Um manuell zu triggen:
1. GitHub Repo → Actions
2. "📰 Generate Headlines" → "Run workflow"

## Ranking-Algorithmus

Scores werden berechnet aus:

1. **Keyword-Relevanz (40%)**
   - AI Keywords: artificial intelligence, machine learning, gpt, llm, neural, deep learning
   - Tech Keywords: software, hardware, cloud, web3, blockchain, startup
   - E-Commerce: shopping, retail, marketplace, payment
   - PIM/MDM: product information, master data, dam
   - Agentic: agent, autonomous, workflow automation, rpa

2. **Aktualität (25%)** - Neuere = höher

3. **Quelle (20%)** - TechCrunch, etailment, The Verge, ArsTechnica, Wired

4. **Häufigkeit (15%)** - Über mehrere Quellen berichtet

## Scraping-Quellen

| Quelle | URL | RSS | Region |
|--------|-----|-----|--------|
| TechCrunch | https://techcrunch.com | ✅ | Global |
| etailment | https://etailment.de | ✅ | DE |
| The Verge | https://theverge.com | ✅ | US |
| ArsTechnica | https://arstechnica.com | ✅ | US |
| Wired | https://wired.com | ✅ | US |

**Fallback:** Wenn RSS fehlschlägt → Web Scraping

## Output-Format

### Markdown
- Für Dokumentation
- Leicht lesbar
- Mit Links zu Originalartikeln
- Zeitstempel

### HTML
- Modernes Dark Mode Design
- 2026-konform
- Responsive (Mobile-friendly)
- Kategorisiert nach Themen
- Relevanz-Score sichtbar

## Struktur der generierten Dateien

**Im `docs/` Folder (GitHub Pages):**
```
index.html      → Dashboard mit Links
today.html      → Heutige Headlines
week.html       → Letzte 7 Tage (default)
month.html      → Letzte 30 Tage
quarter.html    → Letzte 90 Tage
```

**Im `output/` Folder (Lokal):**
```
latest-today.md/html
latest-week.md/html
latest-month.md/html
latest-quarter.md/html
headlines-week-2026-04-29.md/html   (datiert)
```

## Troubleshooting

### RSS Feed lädt nicht
→ Fallback zu Web Scraping automatisch

### Keine Artikel gefunden
→ Überprüf ob die Quellen online sind
→ Erhöhe das Datum-Limit im Filter

### HTML zeigt falsche Styles
→ Neuladen mit Strg+Shift+R (Cache löschen)

## Zukünftige Verbesserungen

- [ ] Lokale Caching (Redis/SQLite)
- [ ] Duplicate-Erkennung optimieren
- [ ] Webhook-Integration für Live-Updates
- [ ] Browser Extension
- [ ] Newsletter-Export
- [ ] Search-Funktionalität
- [ ] Reading Time Estimation
- [ ] Article Summarization (AI)

## Support & Bugs

Fehler gefunden? Issue auf GitHub öffnen:
https://github.com/aclelisabeth/Zeitungsjunge/issues

## Lizenz

MIT
