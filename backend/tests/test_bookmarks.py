"""Tests for bookmarks endpoints."""

import pytest
from backend.tests.conftest import client, TestingSessionLocal
from backend.app.models.models import NewsSource, Article
from datetime import datetime, timedelta


class TestBookmarksEndpoints:
    """Test bookmarks endpoints."""
    
    @staticmethod
    def create_test_article(title):
        """Helper to create a test article."""
        db = TestingSessionLocal()
        try:
            # Create or get test source
            source = db.query(NewsSource).filter_by(name="Bookmark Test News").first()
            if not source:
                source = NewsSource(
                    name="Bookmark Test News",
                    url="https://bookmarktest.example.com",
                    feed_type="rss",
                    region="global",
                    credibility_score=0.8,
                    is_active=True
                )
                db.add(source)
                db.flush()
            
            article = Article(
                source_id=source.id,
                title=title,
                description=f"Description for {title}",
                content=f"Content for {title}",
                url=f"https://bookmarktest.example.com/{title.lower().replace(' ', '-')}",
                author="Test Author",
                published_at=datetime.utcnow(),
                importance_score=5.0,
                region="global",
                language="en"
            )
            db.add(article)
            db.commit()
            return article.id
        finally:
            db.close()
    
    def test_add_bookmark_requires_auth(self):
        """Test adding bookmark requires authentication."""
        article_id = self.create_test_article("Article to Bookmark")
        
        response = client.post(f"/bookmarks/{article_id}")
        assert response.status_code == 401
    
    def test_add_bookmark_success(self, test_user_token):
        """Test successfully adding a bookmark."""
        article_id = self.create_test_article("Bookmarkable Article")
        
        response = client.post(
            f"/bookmarks/{article_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article_id
        assert data["title"] == "Bookmarkable Article"
    
    def test_add_bookmark_nonexistent_article(self, test_user_token):
        """Test adding bookmark for nonexistent article."""
        response = client.post(
            "/bookmarks/999999",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 404
    
    def test_remove_bookmark_requires_auth(self):
        """Test removing bookmark requires authentication."""
        article_id = self.create_test_article("Article to Remove Bookmark")
        
        response = client.delete(f"/bookmarks/{article_id}")
        assert response.status_code == 401
    
    def test_remove_bookmark_success(self, test_user_token):
        """Test successfully removing a bookmark."""
        article_id = self.create_test_article("Article to Remove")
        
        # First add a bookmark
        client.post(
            f"/bookmarks/{article_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        # Then remove it
        response = client.delete(
            f"/bookmarks/{article_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 204
    
    def test_remove_nonexistent_bookmark(self, test_user_token):
        """Test removing a bookmark that doesn't exist."""
        response = client.delete(
            "/bookmarks/999999",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        # Should succeed (idempotent) or return 404
        assert response.status_code in [204, 404]
    
    def test_get_bookmarks_requires_auth(self):
        """Test getting bookmarks requires authentication."""
        response = client.get("/bookmarks/")
        assert response.status_code == 401
    
    def test_get_bookmarks_empty(self, test_user_token):
        """Test getting bookmarks when user has none."""
        response = client.get(
            "/bookmarks/",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
    
    def test_get_bookmarks_with_items(self, test_user_token):
        """Test getting bookmarks with items."""
        # Create and bookmark articles
        article_id1 = self.create_test_article("Bookmarked Article 1")
        article_id2 = self.create_test_article("Bookmarked Article 2")
        
        client.post(
            f"/bookmarks/{article_id1}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        client.post(
            f"/bookmarks/{article_id2}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        # Get bookmarks
        response = client.get(
            "/bookmarks/",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2
    
    def test_get_bookmarks_pagination(self, test_user_token):
        """Test bookmarks pagination."""
        # Create multiple articles
        for i in range(5):
            article_id = self.create_test_article(f"Article {i}")
            client.post(
                f"/bookmarks/{article_id}",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
        
        # Get with limit
        response = client.get(
            "/bookmarks/?limit=2&offset=0",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["limit"] == 2
        assert data["offset"] == 0
    
    def test_check_bookmark_requires_auth(self):
        """Test checking bookmark status requires auth."""
        article_id = self.create_test_article("Check Bookmark Article")
        
        response = client.get(f"/bookmarks/check/{article_id}")
        assert response.status_code == 401
    
    def test_check_bookmark_exists(self, test_user_token):
        """Test checking if bookmark exists."""
        article_id = self.create_test_article("Bookmarked Check Article")
        
        # Add bookmark
        client.post(
            f"/bookmarks/{article_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        # Check if it exists
        response = client.get(
            f"/bookmarks/check/{article_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("bookmarked") is True or data.get("is_bookmarked") is True
    
    def test_check_bookmark_not_exists(self, test_user_token):
        """Test checking for nonexistent bookmark."""
        article_id = self.create_test_article("Not Bookmarked Article")
        
        response = client.get(
            f"/bookmarks/check/{article_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("bookmarked") is False or data.get("is_bookmarked") is False
    
    def test_clear_all_bookmarks_requires_auth(self):
        """Test clearing bookmarks requires authentication."""
        response = client.delete("/bookmarks/")
        assert response.status_code == 401
    
    def test_clear_all_bookmarks_success(self, test_user_token):
        """Test successfully clearing all bookmarks."""
        # Add some bookmarks
        for i in range(3):
            article_id = self.create_test_article(f"Clear Test Article {i}")
            client.post(
                f"/bookmarks/{article_id}",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
        
        # Clear all
        response = client.delete(
            "/bookmarks/",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 204
        
        # Verify they're deleted
        response = client.get(
            "/bookmarks/",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        data = response.json()
        assert data["total"] == 0
