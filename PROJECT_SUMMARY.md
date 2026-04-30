# Zeitungsjunge - Project Summary

## Was wurde implementiert?

Ein **intelligenter News-Aggregator** für Tech & E-Commerce Headlines, der automatisch relevante Schlagzeilen sammelt, rankt und in modernen Formaten (Markdown + HTML) präsentiert.

---

## Features (Implementiert)

### 1. **Multi-Source Web Scraping**
- ✅ RSS-Feed Parsing (Primär)
- ✅ Web-Scraping Fallback
- ✅ 5 Premium-Quellen:
  - TechCrunch (Global)
  - etailment.de (Germany)
  - The Verge (US)
  - ArsTechnica (US)
  - Wired (US)

### 2. **Intelligentes Ranking-System**
- ✅ 4-Faktor Scoring:
  - Keyword-Relevanz (40%)
  - Aktualität (25%)
  - Quelle-Kredibilität (20%)
  - Multi-Source Häufigkeit (15%)
- ✅ 5 Keyword-Kategorien:
  - AI & Machine Learning
  - Technology
  - E-Commerce
  - PIM & Data Management
  - Agentic & Automation

### 3. **Flexible Zeitrahmen**
- ✅ Heute
- ✅ Letzte 7 Tage
- ✅ Letzte 30 Tage
- ✅ Letzte 90 Tage
- ✅ Alle verfügbaren Artikel

### 4. **Output-Formate**
- ✅ **Markdown** - Dokumentation-freundlich
- ✅ **HTML** - 2026 Modern Design mit:
  - Dark Mode
  - Responsive Layout
  - Relevanz-Scores sichtbar
  - Direkte Links zu Originalen

### 5. **GitHub Pages Integration**
- ✅ Automatische Deployment
- ✅ Dashboard mit Navigation
- ✅ Separate Seiten pro Zeitrahmen
- ✅ Modern responsive UI

### 6. **GitHub Actions Automation**
- ✅ Täglich 08:00 UTC Auto-Update
- ✅ Alle Zeitrahmen generieren
- ✅ Auto-Commit & Push
- ✅ Manual Trigger möglich

### 7. **CLI-Tool**
- ✅ Einfache Kommando-Interface
- ✅ NPM Scripts für häufige Fälle
- ✅ Erweiterte Optionen verfügbar
- ✅ Farbige Output mit Progress

### 8. **Daten-Verarbeitung**
- ✅ Automatische Deduplizierung
- ✅ Qualitäts-Filtering
- ✅ HTML-Sanitization
- ✅ Fehlerbehandlung mit Fallbacks

---

## Projektstruktur

```
Zeitungsjunge/
├── src/
│   ├── config.js          # Quellen, Keywords, Gewichtungen
│   ├── fetcher.js         # RSS + Web Scraping
│   ├── ranker.js          # Ranking Engine
│   ├── filter.js          # Filtering & Deduplizierung
│   ├── output.js          # Markdown & HTML Generator
│   └── cli.js             # CLI Entry Point
├── docs/                  # 📍 GitHub Pages
│   ├── index.html         # Dashboard
│   ├── today.html
│   ├── week.html
│   ├── month.html
│   └── quarter.html
├── .github/workflows/
│   └── generate-headlines.yml  # GitHub Actions
├── output/                # Lokal generierte Files
├── package.json           # Dependencies
├── README.md              # Main Dokumentation
├── DEPLOYMENT.md          # Setup Guide
└── QUICKSTART.md          # 30-Sekunden Guide
```

---

## Tech Stack

| Kategorie | Tech |
|-----------|------|
| **Runtime** | Node.js 18+ (ES Modules) |
| **HTTP Client** | Axios |
| **HTML Parsing** | Cheerio |
| **RSS Parsing** | rss-parser |
| **Datum-Handling** | date-fns |
| **CLI UI** | Chalk + Ora |
| **CI/CD** | GitHub Actions |
| **Hosting** | GitHub Pages (Static) |

---

## Beispiel Output

### Markdown
```markdown
# Tech & E-Commerce Headlines
**Generated:** 29. April 2026 14:26

### AI & Machine Learning
1. **OpenAI Really Wants Codex to Shut Up About Goblins**
   - Source: Wired | Date: 29.04.2026
   - Score: 49.1%
   - [Read More →](https://www.wired.com/...)
```

### HTML
- Dark Mode Design mit Gradient
- Kategorie-Sections mit Emoji
- Relevanz-Score-Badge
- Responsive Grid Layout
- Hover-Effekte & Animations

---

## ⚡ Quick Commands

```bash
npm install                      # Setup
npm run scrape:today            # Heute
npm run scrape:week             # Diese Woche
npm run scrape:month            # Dieser Monat
npm run scrape -- --range all   # Alle
npm run scrape -- --limit 10    # Top 10
```

---

## Deployment Steps

1. **GitHub Pages aktivieren:**
   - Repo Settings → Pages
   - Source: `master` / `/docs`
   - Save!

2. **GitHub Actions (Optional):**
   - Bereits konfiguriert
   - Läuft täglich 08:00 UTC

3. **Manuell Generieren:**
   ```bash
   npm run scrape:week
   cp output/latest-week.html docs/week.html
   git add docs/ && git commit && git push
   ```

---

## Ranking Beispiel

**Artikel:** "OpenAI launches new AI agents for e-commerce"

Scoring:
- Keywords: "OpenAI" (AI) + "agents" (Agentic) + "e-commerce" (Ecom) = **0.8 out of 1.0** (40% = 0.32)
- Recency: Heute = **1.0** (25% = 0.25)
- Source: Wired = **0.85** (20% = 0.17)
- Frequency: 3 Quellen berichten = **0.9** (15% = 0.135)

**Total Score: 0.36 + 0.25 + 0.17 + 0.135 = 0.895 = 89.5% Relevanz**

---

## Metrics

| Metrik | Wert |
|--------|------|
| Quellen | 5 |
| Headlines pro Run | ~125 |
| Nach Filtering | ~100-110 |
| Top-Artikel | 5 pro Kategorie |
| Kategorien | 5 |
| Zeitrahmen | 5 (today, week, month, quarter, all) |
| Output-Formate | 2 (MD, HTML) |
| CLI Commands | 8+ |

---

## Mögliche Zukünftige Features

- [ ] Artikel-Zusammenfassung (AI)
- [ ] Newsletter-Export
- [ ] Browser Extension
- [ ] Search-Funktionalität
- [ ] Lokale Datenbank (SQLite)
- [ ] Reading Time Estimate
- [ ] PDF-Export
- [ ] Webhook Integration
- [ ] API-Endpoint
- [ ] Docker Container
- [ ] Cron-Job Support
- [ ] Machine Learning Ranking

---

## Dokumentation

| Datei | Zweck |
|-------|-------|
| `README.md` | Hauptdokumentation + Features |
| `DEPLOYMENT.md` | Setup & Deployment Guide |
| `QUICKSTART.md` | 30-Sekunden Start Guide |
| `package.json` | Dependencies & Scripts |

---

## Qualität

- ✅ Fehlerbehandlung
- ✅ Fallback-Mechanismen
- ✅ HTML-Sanitization
- ✅ Responsive Design
- ✅ Moderner Code (ES6+)
- ✅ Umfangreiche Dokumentation
- ✅ Git History
- ✅ GitHub Actions

---

## Status

**PRODUCTION READY** ✅

Das Projekt ist vollständig implementiert und einsatzbereit:
- CLI funktioniert einwandfrei
- Scraping erfolgreich
- Ranking funktioniert
- Output generiert
- GitHub Pages deploybar
- Dokumentation komplett

---

## Support

Fehler? → GitHub Issues
Feedback? → Pull Request
Questions? → Siehe DEPLOYMENT.md

---

**Autor:** Elisabeth Schallerl  
**Datum:** 29. April 2026  
**Status:** ✅ COMPLETED
