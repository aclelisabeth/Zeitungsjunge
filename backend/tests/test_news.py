"""Tests for news endpoints."""

from datetime import datetime, timedelta
import pytest
from backend.tests.conftest import client, TestingSessionLocal
from backend.app.models.models import NewsSource, Article


class TestNewsEndpoints:
    """Test news and articles endpoints."""
    
    @staticmethod
    def create_test_article(title, days_old=0, score=5.0):
        """Helper to create a test article."""
        db = TestingSessionLocal()
        try:
            # Create or get test source
            source = db.query(NewsSource).filter_by(name="Test News").first()
            if not source:
                source = NewsSource(
                    name="Test News",
                    url="https://testnews.example.com",
                    feed_type="rss",
                    region="global",
                    credibility_score=0.8,
                    is_active=True
                )
                db.add(source)
                db.flush()
            
            now = datetime.utcnow()
            article = Article(
                source_id=source.id,
                title=title,
                description=f"Description for {title}",
                content=f"Full content of {title}...",
                url=f"https://testnews.example.com/{title.lower().replace(' ', '-')}",
                author="Test Author",
                published_at=now - timedelta(days=days_old),
                importance_score=score,
                region="global",
                language="en"
            )
            db.add(article)
            db.commit()
            return article.id
        finally:
            db.close()
    
    def test_get_news_today(self):
        """Test getting news from today."""
        # Create a test article from today
        self.create_test_article("Breaking News Today", days_old=0, score=9.5)
        
        response = client.get("/news/?time_range=today")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 1  # At least our article
    
    def test_get_news_7_days(self):
        """Test getting news from last 7 days."""
        self.create_test_article("Week Old News", days_old=5, score=7.0)
        
        response = client.get("/news/?time_range=7d")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) <= data["total"]
    
    def test_get_news_with_pagination(self):
        """Test news pagination."""
        self.create_test_article("Article 1", days_old=0, score=5.0)
        self.create_test_article("Article 2", days_old=1, score=6.0)
        
        response = client.get("/news/?time_range=90d&limit=1&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 1
        assert data["offset"] == 0
        assert len(data["items"]) <= 1
    
    def test_get_news_invalid_time_range(self):
        """Test with invalid time range."""
        response = client.get("/news/?time_range=invalid")
        assert response.status_code == 422  # Validation error
    
    def test_get_news_with_region(self):
        """Test filtering by region."""
        response = client.get("/news/?time_range=30d&region=global")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
    
    def test_get_news_invalid_region(self):
        """Test with invalid region."""
        response = client.get("/news/?region=invalid")
        assert response.status_code == 422
    
    def test_search_news(self):
        """Test searching for news."""
        self.create_test_article("Important Breaking Story", days_old=0)
        
        response = client.get("/news/search?query=breaking")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "query" in data
        assert "results" in data
        assert data["query"] == "breaking"
    
    def test_search_news_with_filters(self):
        """Test search with region and days filters."""
        self.create_test_article("Test Story Here", days_old=5)
        
        response = client.get("/news/search?query=story&region=global&days=30&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_search_news_empty_query(self):
        """Test search with empty query."""
        response = client.get("/news/search?query=")
        assert response.status_code == 422  # Validation error
    
    def test_search_news_no_results(self):
        """Test search with query that has no results."""
        response = client.get("/news/search?query=nonexistentquery123456xyz")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["results"]) == 0
    
    def test_get_trending_articles(self):
        """Test getting trending articles."""
        self.create_test_article("Trending 1", days_old=1, score=9.0)
        self.create_test_article("Trending 2", days_old=2, score=8.0)
        self.create_test_article("Not Trending", days_old=10, score=2.0)
        
        response = client.get("/news/trending")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_trending_articles_with_limit(self):
        """Test trending articles with limit."""
        self.create_test_article("Trending A", days_old=1, score=9.0)
        self.create_test_article("Trending B", days_old=1, score=8.5)
        
        response = client.get("/news/trending?limit=1&days=30")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 1
    
    def test_get_article_by_id(self):
        """Test getting a specific article."""
        article_id = self.create_test_article("Specific Article", days_old=0)
        
        response = client.get(f"/news/{article_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article_id
        assert "title" in data
        assert "description" in data
        assert "url" in data
    
    def test_get_nonexistent_article(self):
        """Test getting a nonexistent article."""
        response = client.get("/news/999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_article_response_structure(self):
        """Test article response has required fields."""
        article_id = self.create_test_article("Test Article", days_old=0)
        
        response = client.get(f"/news/{article_id}")
        assert response.status_code == 200
        data = response.json()
        required_fields = ["id", "title", "url", "source_id", "published_at"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_summarize_article_with_auth(self, test_user_token):
        """Test article summarization with authentication."""
        article_id = self.create_test_article("Article to Summarize", days_old=0)
        
        response = client.post(
            f"/news/{article_id}/summarize",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "article_id" in data
        assert "summary" in data
        assert "already_generated" in data
    
    def test_summarize_article_without_auth(self):
        """Test summarization requires authentication."""
        article_id = self.create_test_article("Article", days_old=0)
        
        response = client.post(f"/news/{article_id}/summarize")
        assert response.status_code == 401
    
    def test_summarize_nonexistent_article(self, test_user_token):
        """Test summarizing a nonexistent article."""
        response = client.post(
            "/news/999999/summarize",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 404
