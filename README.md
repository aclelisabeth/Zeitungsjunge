# Zeitungsjunge – News Aggregation & Summarization Tool

A Python-based news aggregation and summarization application that collects headlines from multiple online news sources, filters them by time range and region, deduplicates stories, ranks them by importance, and generates clean Markdown reports.

## Features (MVP Phase 1)

✅ **Configurable News Sources**: Easily add/remove RSS feeds or REST APIs via JSON configuration  
✅ **Multiple Time Ranges**: Filter articles by today, 7d, 30d, 60d, or 90d  
✅ **Smart Deduplication**: Identifies duplicate stories across sources (75% similarity threshold)  
✅ **Importance Ranking**: Scores articles by frequency, recency, and source credibility  
✅ **Regional Filtering**: Filter by US, German, European, or Global sources  
✅ **6-Hour Caching**: Efficient caching system with configurable TTL  
✅ **Markdown Output**: Clean, formatted reports saved to `Extrablatt/` directory  
✅ **CLI Interface**: Flexible command-line arguments for all parameters  

## Supported News Sources (Default)

### European/German
- **TechCrunch** (RSS, US/Global) - Technology and startup news
- **etailment.de** (RSS, Germany) - E-commerce and retail tech

### US Tech Sources
- **Hacker News** (REST API, US) - Tech-focused crowdsourced news
- **The Verge** (RSS, US) - Consumer tech and gadgets
- **ArsTechnica** (RSS, US) - In-depth technology analysis
- **CNBC Tech** (RSS, US) - Business and technology
- **Wired** (RSS, US) - Design, culture, technology
- **Mashable Tech** (RSS, US) - Technology and pop culture

All sources are fully configurable via `config/sources.json`.

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup

1. **Clone or navigate to the project**:
```bash
cd Zeitungsjunge
```

2. **Create a virtual environment (recommended)**:
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Verify installation**:
```bash
python src/main.py --help
```

## Usage

### Basic Usage

Generate a report for today's top news (all sources):
```bash
python src/main.py
```

### Time Range Filtering

```bash
# Last 7 days
python src/main.py --range 7d

# Last 30 days
python src/main.py --range 30d

# Last 60 days
python src/main.py --range 60d

# Last 90 days
python src/main.py --range 90d
```

### Regional Filtering

```bash
# US sources only
python src/main.py --range 7d --region us

# German sources only
python src/main.py --range 7d --region de

# European sources (Germany, Europe)
python src/main.py --range 7d --region eu

# All sources (default)
python src/main.py --range 7d --region global
```

### Advanced Options

```bash
# Fresh fetch, bypass 6-hour cache
python src/main.py --range 7d --no-cache

# Use custom config file
python src/main.py --config ./custom_sources.json

# Show help
python src/main.py --help
```

## Configuration

### Adding New News Sources

Edit `config/sources.json`:

```json
{
  "sources": [
    {
      "id": "my_source",
      "name": "My News Source",
      "type": "rss",
      "url": "https://example.com/feed.xml",
      "credibility_weight": 0.90,
      "region": "us",
      "enabled": true,
      "category": "tech"
    }
  ]
}
```

**Source Fields**:
- `id`: Unique identifier (lowercase, no spaces)
- `name`: Display name
- `type`: `"rss"` or `"api"` (currently supports RSS and Hacker News API)
- `url`: Feed URL or API base URL
- `credibility_weight`: 0.0 - 1.0 (used in importance ranking)
- `region`: `"us"`, `"de"`, `"eu"`, or `"global"`
- `enabled`: `true` or `false`
- `category`: Optional category tag (e.g., "tech", "business")

### Configuration Parameters

Modify `config/sources.json` to adjust:

```json
{
  "cache": {
    "enabled": true,
    "ttl_hours": 6,
    "storage": "file",
    "cache_dir": "./cache"
  },
  "deduplication": {
    "enabled": true,
    "similarity_threshold": 0.75,
    "method": "difflib"
  },
  "ranking": {
    "top_articles": 15,
    "weights": {
      "frequency": 0.4,
      "recency": 0.3,
      "credibility": 0.3
    }
  }
}
```

## Output

Reports are generated as Markdown files in the `Extrablatt/` directory:

```
Extrablatt/
├── news_today_20260429_143000.md
├── news_7d_20260429_143015.md
└── news_30d_20260429_143030.md
```

### Example Output

```markdown
# Extrablatt – Top News

**Report Generated**: 2026-04-29 14:30:00 UTC  
**Time Range**: Last 7 days  
**Coverage**: 8 sources | 47 articles fetched | 15 stories selected  
**Regional Filter**: Global

---

## 1. OpenAI Releases New Model — Score: 8.5/10

- **Sources**: TechCrunch, The Verge, ArsTechnica (3 sources)
- **Published**: 2026-04-28 10:30 UTC
- **Summary**: OpenAI announced a new AI model with improved capabilities...
- **Read More**: [https://techcrunch.com/...](https://techcrunch.com/...)

---

## 2. Tech Startup Raises $100M — Score: 8.2/10

...
```

## Architecture

```
Zeitungsjunge/
├── config/
│   └── sources.json              # News source configuration
├── src/
│   ├── models.py                 # Data models
│   ├── fetcher/                  # Article fetching (RSS + API)
│   ├── filter/                   # Date range filtering
│   ├── deduplicator/             # Duplicate detection
│   ├── ranker/                   # Importance scoring & ranking
│   ├── cache/                    # Caching system
│   ├── output/                   # Markdown generation
│   └── main.py                   # CLI entry point
├── Extrablatt/                   # Generated reports
├── cache/                        # Cache storage
├── requirements.txt              # Python dependencies
├── .gitignore
└── README.md                     # This file
```

## How It Works

### 1. Fetching
- RSS feeds are parsed using `feedparser`
- Hacker News API fetches top tech stories
- Articles are validated and sanitized

### 2. Filtering
- Articles older than the selected time range are removed
- Regional filters exclude sources outside selected regions

### 3. Deduplication
- Articles are compared using title + description similarity
- If similarity ≥ 75%, they're considered duplicates
- Duplicates are merged, keeping the most credible source
- Other reporting sources are recorded in metadata

### 4. Ranking
Importance score = (frequency × 0.4) + (recency × 0.3) + (credibility × 0.3)

- **Frequency**: How many sources reported the story
- **Recency**: How fresh the article is (newer = higher score)
- **Credibility**: Source credibility weight

### 5. Output
- Top 15 articles (configurable) are selected
- Formatted as a clean Markdown report
- Saved to `Extrablatt/` with timestamp

### 6. Caching
- Reports are cached for 6 hours
- Cache is automatically invalidated after TTL
- Users can bypass cache with `--no-cache`

## Security Considerations

### Input Validation
- All URLs are validated (HTTP/HTTPS only, max 2048 chars)
- HTML tags and entities are stripped from descriptions
- Article titles are limited to 300 characters
- Descriptions are limited to 500 characters

### Rate Limiting
- Request timeout: 10 seconds (prevents hanging)
- Max 30 items per source (prevents memory overload)
- Hacker News stories filtered by minimum score (5 points)

### Error Handling
- Malformed feed entries are skipped gracefully
- Failed sources don't crash the entire pipeline
- All errors are logged to console

### File Security
- Cache files stored in isolated `cache/` directory
- Output files use safe timestamped filenames
- No secrets or API keys stored in code

## Performance

- **Fetch time**: ~5-15 seconds (depends on network)
- **Processing time**: ~1-2 seconds
- **Output generation**: <1 second
- **Cache hit time**: <100ms (if cache valid)

## Troubleshooting

### No articles fetched
- Check your internet connection
- Verify RSS feed URLs are accessible:
  ```bash
  curl https://techcrunch.com/feed/
  ```
- Check `config/sources.json` for typos

### Articles not appearing in report
- Check date range filter (`--range`)
- Check regional filter (`--region`)
- Check similarity threshold (deduplication might be too aggressive)

### Cache not working
- Ensure `cache/` directory exists and is writable
- Check `config/sources.json` cache settings
- Use `--no-cache` to bypass

### ImportError: feedparser not found
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Planned Features (Phase 2)

🎯 Web Application (React + Next.js frontend)  
🎯 Interactive UI with time range selector  
🎯 Dark mode support  
🎯 Topic-based filtering  
🎯 Advanced summarization (AI-powered)  
🎯 Language support (English + German)  
🎯 API backend (FastAPI)  
🎯 User preferences & bookmarks  
🎯 Email digest delivery  

## Development

### Running Tests (Future)
```bash
pytest tests/
```

### Code Style
- Python 3.8+ compatible
- Type hints throughout
- Docstrings for all modules
- Maximum line length: 100 characters

## License

MIT License - Feel free to use and modify!

## Support

For issues, feature requests, or feedback:
- GitHub Issues: [Report issues here]
- Documentation: [This README]

---

**Built with ❤️ for news enthusiasts and developers**

*Zeitungsjunge = "Newspaper Boy" in German* 📰
