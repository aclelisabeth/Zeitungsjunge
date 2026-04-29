# ⚡ Zeitungsjunge - Quick Start

## In 30 Sekunden

```bash
# 1. Setup
npm install

# 2. Scrape headlines
npm run scrape:week

# 3. Anschauen
open output/latest-week.html  # macOS
start output/latest-week.html # Windows
xdg-open output/latest-week.html # Linux
```

**Fertig!** 🎉

---

## Alle Befehle

```bash
npm run scrape:today        # Heute
npm run scrape:week         # Diese Woche (default)
npm run scrape:month        # Dieser Monat
npm run scrape -- --range quarter  # Letzte 90 Tage
npm run scrape -- --range all      # Alle Artikel

npm run scrape -- --output md      # Nur Markdown
npm run scrape -- --output html    # Nur HTML
npm run scrape -- --limit 10       # Top 10 Artikel
```

## Output

```
output/
├── latest-today.{md,html}     ← immer aktuell
├── latest-week.{md,html}
├── latest-month.{md,html}
├── latest-quarter.{md,html}
└── headlines-RANGE-DATE.{md,html}  ← datiert
```

## GitHub Pages

Nach Setup in Repository Settings:
- Branch: `master`
- Folder: `/docs`

→ Online unter: `https://aclelisabeth.github.io/Zeitungsjunge/`

## Kategorien

Die Headlines werden automatisch kategorisiert:

- 🤖 AI & Machine Learning
- 💻 Technology
- 🛒 E-Commerce
- 📊 PIM & Data Management
- 🔄 Agentic & Automation

## Quellen

| Quelle | Region |
|--------|--------|
| TechCrunch | 🌍 Global |
| etailment | 🇩🇪 Germany |
| The Verge | 🇺🇸 US |
| ArsTechnica | 🇺🇸 US |
| Wired | 🇺🇸 US |

## Ranking-Faktoren

1. Keywords (40%) - AI, Tech, E-Commerce, PIM, MDM, Agentic
2. Aktualität (25%) - Je neuer, desto besser
3. Quelle (20%) - Reputation
4. Häufigkeit (15%) - Multi-Source Coverage

## Tipps

- Tägliche Automation: Nutze `.github/workflows/generate-headlines.yml`
- Markdown für Dokumentation, HTML für Web
- Top 5 pro Kategorie default (mit `--limit` änderbar)
- RSS-Fallback auf Web Scraping automatisch

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| Keine Artikel | `node src/cli.js --range all` für mehr Daten |
| RSS Failed | Automatischer Fallback zu Web Scraping |
| Styles laden nicht | Page mit Strg+Shift+R neuladen |
| Alte Headlines | Output Ordner löschen, neu generieren |

---

**Mehr Info:** Siehe README.md und DEPLOYMENT.md
