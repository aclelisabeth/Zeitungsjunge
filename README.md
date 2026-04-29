# 📰 Zeitungsjunge - Smart News Aggregator

Ein intelligenter Nachrichten-Aggregator, der die wichtigsten Schlagzeilen zu **AI, Tech, E-Commerce, PIM/MDM und Agentic Commerce** sammelt, rankt und in modernem Design präsentiert.

## Features

✨ **Smart Ranking System**
- Automatisches Ranking nach Relevanz
- Keyword-basierte Kategorisierung (AI, Tech, E-Commerce, PIM, MDM, Agentic)
- Berücksichtigung von Aktualität und Quelle

🔄 **Multi-Source Scraping**
- RSS-Feed Support (Fallback: Web Scraping)
- 5 Premium-Quellen: TechCrunch, etailment, The Verge, ArsTechnica, Wired
- Automatische Deduplizierung

🎯 **Flexible Zeitrahmen**
- Heute
- Letzte 7 Tage
- Letzte 30 Tage
- Letzte 90 Tage

📄 **Moderne Output-Formate**
- **Markdown** - für GitHub, Dokumentation
- **HTML** - modernes 2026-Design mit Dark Mode

## Installation

```bash
npm install
```

## Verwendung

### Interaktives CLI

```bash
# Standard: Letzte 7 Tage, beide Formate (MD + HTML)
npm run scrape

# Nur heute
npm run scrape:today

# Letzte Woche
npm run scrape:week

# Letzte 30 Tage
npm run scrape:month

# Alles (alle vorhandenen Artikel)
npm run scrape:all
```

### Erweiterte Optionen

```bash
# Custom range
node src/cli.js --range week

# Nur Markdown
node src/cli.js --range month --output md

# Nur HTML
node src/cli.js --range month --output html

# Custom Limit (Top N Artikel)
node src/cli.js --limit 10
```

## Output

Die generierten Dateien finden sich im `output/` Ordner:

- `latest-today.md` / `latest-today.html` - Heutige News
- `latest-week.md` / `latest-week.html` - News der letzten 7 Tage
- `latest-month.md` / `latest-month.html` - News des letzten Monats
- `latest-quarter.md` / `latest-quarter.html` - News der letzten 3 Monate

Plus datierte Versionen: `headlines-week-2026-04-29.md` etc.

## Projektstruktur

```
src/
├── config.js       - Quellen, Keywords, Gewichtungen
├── fetcher.js      - RSS + Web Scraping
├── ranker.js       - Ranking-Engine
├── filter.js       - Zeitrahmen, Deduplizierung
├── output.js       - Markdown & HTML Generator
├── cli.js          - CLI-Werkzeug
└── index.js        - Main Entry Point

output/            - Generierte Headlines (Markdown/HTML)
```

## Ranking-Algorithmus

Das System bewertet Artikel anhand von:

1. **Keyword-Relevanz (40%)**
   - AI: artificial intelligence, machine learning, gpt, llm, neural, deep learning
   - Tech: software, hardware, cloud, web3, blockchain, startup
   - E-Commerce: shopping, retail, marketplace, payment
   - PIM/MDM: product information, master data, digital asset
   - Agentic: agent, autonomous, workflow automation, rpa

2. **Aktualität (25%)** - Neuere Artikel werden bevorzugt

3. **Quelle (20%)** - TechCrunch, etailment, The Verge, ArsTechnica, Wired

4. **Häufigkeit (15%)** - Artikel, über die mehrere Quellen berichten

## GitHub Pages Deployment

```bash
# Automatisch generierte HTML wird gehostet auf GitHub Pages
# https://aclelisabeth.github.io/Zeitungsjunge/
```

## Tech Stack

- **Runtime:** Node.js 18+
- **Dependencies:**
  - `axios` - HTTP Requests
  - `cheerio` - HTML Parsing
  - `rss-parser` - RSS Feed Parsing
  - `date-fns` - Datum-Handling
  - `chalk` - CLI Farben
  - `ora` - CLI Spinner

## Lizenz

MIT

## Autor

Elisabeth Schallerl
