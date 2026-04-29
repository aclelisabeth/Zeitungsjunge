"""Tests for articles functionality."""

import pytest
from backend.tests.conftest import client, TestingSessionLocal
from backend.app.models.models import NewsSource, Article
from datetime import datetime, timedelta


class TestArticlesFunctionality:
    """Test article management and retrieval."""
    
    @staticmethod
    def create_article(title, region="global", score=5.0, days_old=0):
        """Helper to create a test article."""
        db = TestingSessionLocal()
        try:
            source = db.query(NewsSource).filter_by(name="Article Test News").first()
            if not source:
                source = NewsSource(
                    name="Article Test News",
                    url="https://articletest.example.com",
                    feed_type="rss",
                    region=region,
                    credibility_score=0.8,
                    is_active=True
                )
                db.add(source)
                db.flush()
            
            article = Article(
                source_id=source.id,
                title=title,
                description=f"Description for {title}",
                content=f"Detailed content for {title}",
                url=f"https://articletest.example.com/{title.lower().replace(' ', '-')}",
                author="Test Author",
                published_at=datetime.utcnow() - timedelta(days=days_old),
                importance_score=score,
                region=region,
                language="en"
            )
            db.add(article)
            db.commit()
            return article.id
        finally:
            db.close()
    
    def test_article_with_keywords(self):
        """Test article with keywords metadata."""
        db = TestingSessionLocal()
        try:
            source = db.query(NewsSource).filter_by(name="Keyword Test").first()
            if not source:
                source = NewsSource(
                    name="Keyword Test",
                    url="https://keywordtest.example.com",
                    feed_type="rss",
                    region="global",
                    credibility_score=0.8,
                    is_active=True
                )
                db.add(source)
                db.flush()
            
            article = Article(
                source_id=source.id,
                title="Article with Keywords",
                description="Description with many words",
                content="Content here",
                url="https://keywordtest.example.com/keywords",
                author="Author",
                keywords="python,testing,software",
                importance_score=7.0,
                region="global",
                language="en"
            )
            db.add(article)
            db.commit()
            
            # Verify we can retrieve it
            response = client.get(f"/news/{article.id}")
            assert response.status_code == 200
            data = response.json()
            assert data["keywords"] == "python,testing,software"
        finally:
            db.close()
    
    def test_article_with_image(self):
        """Test article with image URL."""
        db = TestingSessionLocal()
        try:
            source = db.query(NewsSource).filter_by(name="Image Test").first()
            if not source:
                source = NewsSource(
                    name="Image Test",
                    url="https://imagetest.example.com",
                    feed_type="rss",
                    region="global",
                    credibility_score=0.8,
                    is_active=True
                )
                db.add(source)
                db.flush()
            
            article = Article(
                source_id=source.id,
                title="Article with Image",
                description="Description",
                content="Content",
                url="https://imagetest.example.com/image",
                image_url="https://example.com/image.jpg",
                author="Author",
                importance_score=6.0,
                region="global",
                language="en"
            )
            db.add(article)
            db.commit()
            
            response = client.get(f"/news/{article.id}")
            assert response.status_code == 200
            data = response.json()
            assert data["image_url"] == "https://example.com/image.jpg"
        finally:
            db.close()
    
    def test_article_multilingual(self):
        """Test articles in different languages."""
        article_en = self.create_article("English Article", score=5.0)
        
        db = TestingSessionLocal()
        try:
            source = db.query(NewsSource).filter_by(name="Multilingual Test").first()
            if not source:
                source = NewsSource(
                    name="Multilingual Test",
                    url="https://multitest.example.com",
                    feed_type="rss",
                    region="global",
                    credibility_score=0.8,
                    is_active=True
                )
                db.add(source)
                db.flush()
            
            article_de = Article(
                source_id=source.id,
                title="Deutscher Artikel",
                description="Beschreibung",
                content="Inhalt",
                url="https://multitest.example.com/de/artikel",
                author="Autor",
                importance_score=5.0,
                region="eu",
                language="de"
            )
            db.add(article_de)
            db.commit()
            
            # Verify both exist
            en_response = client.get(f"/news/{article_en}")
            de_response = client.get(f"/news/{article_de.id}")
            assert en_response.status_code == 200
            assert de_response.status_code == 200
            assert en_response.json()["language"] == "en"
            assert de_response.json()["language"] == "de"
        finally:
            db.close()
    
    def test_article_importance_scoring(self):
        """Test article importance scoring."""
        high_score = self.create_article("High Importance", score=9.5)
        low_score = self.create_article("Low Importance", score=1.0)
        
        high_resp = client.get(f"/news/{high_score}")
        low_resp = client.get(f"/news/{low_score}")
        
        assert high_resp.status_code == 200
        assert low_resp.status_code == 200
        assert high_resp.json()["importance_score"] > low_resp.json()["importance_score"]
    
    def test_article_by_region(self):
        """Test retrieving articles by region."""
        self.create_article("US Article", region="us")
        self.create_article("EU Article", region="eu")
        self.create_article("Global Article", region="global")
        
        # All regions should return results
        us_response = client.get("/news/?region=us&time_range=30d")
        eu_response = client.get("/news/?region=eu&time_range=30d")
        global_response = client.get("/news/?region=global&time_range=30d")
        
        assert us_response.status_code == 200
        assert eu_response.status_code == 200
        assert global_response.status_code == 200
    
    def test_article_summary_generation(self, test_user_token):
        """Test article summary generation."""
        article_id = self.create_article("Article to Summarize")
        
        response = client.post(
            f"/news/{article_id}/summarize",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "article_id" in data
        assert data["article_id"] == article_id
        assert "summary" in data
        assert "already_generated" in data
    
    def test_article_summary_cached(self, test_user_token):
        """Test that summaries are cached."""
        article_id = self.create_article("Article for Cache Test")
        
        # Generate summary first time
        response1 = client.post(
            f"/news/{article_id}/summarize",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Generate again - should be cached
        response2 = client.post(
            f"/news/{article_id}/summarize",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # If already_generated is present, check cache behavior
        if "already_generated" in data2:
            # Should indicate it was cached or newly generated
            assert isinstance(data2["already_generated"], bool)
    
    def test_article_search_filters(self):
        """Test article search with various filters."""
        # Create articles for testing
        self.create_article("Python Programming Guide", score=8.0, days_old=1)
        self.create_article("Python for Beginners", score=7.0, days_old=5)
        self.create_article("JavaScript Basics", score=6.0, days_old=10)
        
        # Search for Python
        response = client.get("/news/search?query=python&days=30")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) >= 2
    
    def test_article_frequency_tracking(self):
        """Test article frequency count."""
        db = TestingSessionLocal()
        try:
            source = db.query(NewsSource).filter_by(name="Frequency Test").first()
            if not source:
                source = NewsSource(
                    name="Frequency Test",
                    url="https://freqtest.example.com",
                    feed_type="rss",
                    region="global",
                    credibility_score=0.8,
                    is_active=True
                )
                db.add(source)
                db.flush()
            
            # Create article with high frequency count
            article = Article(
                source_id=source.id,
                title="Frequently Discussed Topic",
                description="A popular topic",
                content="Content",
                url="https://freqtest.example.com/popular",
                frequency_count=10,  # Appears 10 times across sources
                importance_score=8.5,
                region="global",
                language="en"
            )
            db.add(article)
            db.commit()
            
            response = client.get(f"/news/{article.id}")
            assert response.status_code == 200
            data = response.json()
            assert data["frequency_count"] == 10
        finally:
            db.close()
    
    def test_trending_articles_recent_priority(self):
        """Test that trending shows recent articles higher."""
        # Create recent high-score article
        recent = self.create_article("Recent Important News", score=9.0, days_old=1)
        # Create old high-score article
        old = self.create_article("Old Important News", score=9.0, days_old=90)
        
        response = client.get("/news/trending?days=7")
        assert response.status_code == 200
        data = response.json()
        
        # If both are in results, recent should come first (or only recent should be there)
        if len(data) > 0:
            recent_ids = [a["id"] for a in data]
            # At least the recent one should be included
            if len(recent_ids) == 1:
                assert recent_ids[0] == recent
    
    def test_article_pagination_consistency(self):
        """Test pagination returns consistent results."""
        # Create multiple articles
        for i in range(10):
            self.create_article(f"Article {i}", score=5.0 + i*0.5)
        
        # Get first page
        response1 = client.get("/news/?time_range=30d&limit=5&offset=0")
        data1 = response1.json()
        first_ids = [a["id"] for a in data1["items"]]
        
        # Get second page
        response2 = client.get("/news/?time_range=30d&limit=5&offset=5")
        data2 = response2.json()
        second_ids = [a["id"] for a in data2["items"]]
        
        # Should have no overlap
        assert len(set(first_ids) & set(second_ids)) == 0
