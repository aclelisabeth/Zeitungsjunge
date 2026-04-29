# Zeitungsjunge Backend API - Phase 2

Professionelle REST API für Nachrichtenaggregation und -zusammenfassung mit KI-gesteuerten Features.

## Features

### ✨ Core Features
- **News Aggregation**: Echtzeit-Nachrichtenaggregation aus mehreren Quellen (RSS + REST APIs)
- **Smart Filtering**: Nach Zeitbereich (today, 7d, 30d, 60d, 90d) und Region (US, DE, EU, Global)
- **AI Summarization**: Automatische Zusammenfassungen mit OpenAI GPT-3.5
- **User Bookmarks**: Artikel speichern und später abrufen
- **Full-Text Search**: Erweiterte Suchfunktion für Artikel
- **Trending Articles**: Algorithmus für Trend-Erkennung

### 🔐 Authentication & Security
- JWT Token-basierte Authentifizierung
- Bcrypt-Hashing für Passwörter
- User Preferences Management
- Rate Limiting (integriert über FastAPI)

### 📊 API Endpoints
```
# Authentication
POST   /auth/register              - Neue Benutzer registrieren
POST   /auth/login                 - Benutzer anmelden
GET    /auth/me                    - Aktuelle Benutzerinformationen
POST   /auth/refresh               - Token aktualisieren

# News & Articles
GET    /news/                      - Nachrichtenübersicht nach Zeitbereich
GET    /news/search                - Artikel durchsuchen
GET    /news/trending              - Trending-Artikel
GET    /news/{article_id}          - Artikel-Details
POST   /news/{article_id}/summarize - AI-Zusammenfassung generieren

# Bookmarks
POST   /bookmarks/{article_id}     - Artikel zu Lesezeichen hinzufügen
DELETE /bookmarks/{article_id}     - Aus Lesezeichen entfernen
GET    /bookmarks/                 - Alle Lesezeichen abrufen
GET    /bookmarks/check/{id}       - Prüfe ob Artikel gemerkt ist
DELETE /bookmarks/                 - Alle Lesezeichen löschen

# User & Preferences
GET    /users/profile              - Benutzerprofil
PUT    /users/profile              - Profil aktualisieren
DELETE /users/profile              - Konto deaktivieren
GET    /users/preferences          - Benutzer-Einstellungen
PUT    /users/preferences          - Einstellungen aktualisieren

# Health
GET    /                           - API Health Check
GET    /health                     - Health Status
```

## Installation

### Voraussetzungen
- Python 3.11+
- pip oder poetry
- SQLite3 (wird automatisch mit Python installiert)

### Setup

1. **Abhängigkeiten installieren**:
```bash
pip install -r requirements.txt
```

2. **Umgebungsvariablen konfigurieren**:
```bash
cp .env.example .env
# Bearbeite .env und füge deine API-Schlüssel ein
```

3. **Datenbank initialisieren**:
```bash
python -c "from backend.app.db.database import init_db; init_db()"
```

4. **Server starten**:
```bash
python -m backend.app.main
# oder mit Uvicorn direkt:
uvicorn backend.app.main:app --reload
```

Die API ist dann verfügbar unter: **http://localhost:8000**
API Dokumentation: **http://localhost:8000/api/docs**

## Konfiguration

### Umgebungsvariablen (.env)

```env
# Backend
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Database
DATABASE_URL=sqlite:///./zeitungsjunge.db

# Security
SECRET_KEY=your-secret-key-here

# OpenAI (für AI-Zusammenfassungen)
OPENAI_API_KEY=sk-...

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Weitere Optionen in .env.example
```

## Authentifizierung

Die API verwendet **JWT (JSON Web Tokens)** für die Authentifizierung.

### Login-Beispiel:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user",
    "password": "password123"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-04-29T10:00:00"
  }
}
```

### Autorisierte Requests:
```bash
curl -X GET http://localhost:8000/bookmarks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Verwendungsbeispiele

### 1. Benutzer registrieren
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "full_name": "John Doe",
    "password": "SecurePass123"
  }'
```

### 2. Nachrichten abrufen
```bash
# Nachrichten von heute
curl http://localhost:8000/news/?time_range=today&region=global

# Mit Pagination
curl http://localhost:8000/news/?time_range=7d&limit=20&offset=0
```

### 3. Artikel durchsuchen
```bash
curl "http://localhost:8000/news/search?query=KI&region=global&days=30"
```

### 4. Trending Artikel
```bash
curl http://localhost:8000/news/trending?days=7&limit=20
```

### 5. Artikel merken
```bash
curl -X POST http://localhost:8000/bookmarks/42 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. AI-Zusammenfassung generieren
```bash
curl -X POST http://localhost:8000/news/123/summarize \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Datenbankschema

### Haupttabellen:
- **users**: Benutzer und Authentifizierung
- **user_preferences**: Benutzer-Einstellungen
- **articles**: Nachrichtenartikel
- **news_sources**: Konfigurierte Nachrichtenquellen
- **user_bookmarks**: Benutzer-zu-Artikel Zuordnung (Many-to-Many)
- **search_history**: Suchverlauf für Analytics
- **email_subscriptions**: E-Mail Newsletter Einstellungen

## Fehlerbehebung

### 1. "Secret key not set"
→ Stelle sicher, dass `SECRET_KEY` in der `.env` Datei gesetzt ist

### 2. "OpenAI API key not configured"
→ Für AI-Zusammenfassungen: `OPENAI_API_KEY` in der `.env` setzen
→ Die API funktioniert auch ohne, gibt aber None für Zusammenfassungen zurück

### 3. Datenbank-Fehler
→ Stelle sicher, dass die `zeitungsjunge.db` Datei beschreibbar ist
→ Lösche `zeitungsjunge.db` und lasse sie neu erstellen

### 4. CORS-Fehler
→ Überprüfe `CORS_ORIGINS` in der `.env` Datei

## Tests

```bash
# Unit Tests
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=backend --cov-report=html

# Spezifisches Modul
pytest tests/test_auth.py -v
```

## Deployment

### Docker
```bash
docker build -t zeitungsjunge-api .
docker run -p 8000:8000 zeitungsjunge-api
```

### Produktionsumgebung (Gunicorn + Nginx)
```bash
gunicorn backend.app.main:app --workers 4 --bind 0.0.0.0:8000
```

## API-Dokumentation

Die interaktive API-Dokumentation ist verfügbar unter:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Sicherheit

### Best Practices:
- ✅ Alle Passwörter werden mit bcrypt gehashed
- ✅ JWT Tokens haben begrenzte Gültigkeitsdauer (30 Minuten)
- ✅ CORS ist konfigurierbar für Production
- ✅ Input-Validierung mit Pydantic
- ✅ SQL Injection Schutz durch SQLAlchemy ORM
- ✅ Rate Limiting wird durch FastAPI unterstützt

### Production-Checklist:
- [ ] `SECRET_KEY` auf einen starken Wert ändern
- [ ] `DEBUG=false` setzen
- [ ] HTTPS verwenden (Nginx/Caddy)
- [ ] `.env` Datei nicht ins Repo committen
- [ ] Regelmäßige Datensicherungen
- [ ] Logging monitoren

## Performance

- **Datenbankabfragen**: Mit Indizes optimiert
- **Caching**: 6 Stunden TTL für Artikel
- **Paginierung**: Standardmäßig aktiviert
- **Async Support**: Für I/O-intensive Operationen

## Roadmap

- [x] Core API Endpoints
- [x] User Authentication
- [x] AI Summarization
- [ ] Email Newsletter
- [ ] RSS Export
- [ ] Advanced Analytics
- [ ] Webhook Support
- [ ] GraphQL API

## Kontakt & Support

Für Fragen oder Issues:
- GitHub Issues: https://github.com/aclelisabeth/Zeitungsjunge
- Email: support@zeitungsjunge.de

## Lizenz

MIT License - siehe LICENSE Datei
