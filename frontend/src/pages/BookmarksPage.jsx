import { useState, useEffect } from 'react';
import { useBookmarkStore, useUIStore } from '../store';
import { bookmarkAPI } from '../api/client';
import ArticleCard from '../components/ArticleCard';
import './BookmarksPage.css';

const BookmarksPage = () => {
  const [loading, setLoading] = useState(true);
  const { bookmarks, setBookmarks } = useBookmarkStore();
  const { showNotification } = useUIStore();

  useEffect(() => {
    loadBookmarks();
  }, []);

  const loadBookmarks = async () => {
    setLoading(true);
    try {
      const response = await bookmarkAPI.getBookmarks(100);
      setBookmarks(response.data.items || []);
    } catch (error) {
      showNotification('Failed to load bookmarks', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveBookmark = async (articleId) => {
    try {
      await bookmarkAPI.removeBookmark(articleId);
      await loadBookmarks();
      showNotification('Bookmark removed', 'success');
    } catch (error) {
      showNotification('Failed to remove bookmark', 'error');
    }
  };

  return (
    <div className="bookmarks-page">
      <h1>Saved Articles</h1>

      <button 
        onClick={loadBookmarks}
        disabled={loading}
        className="refresh-btn"
      >
        {loading ? 'Loading...' : 'Refresh'}
      </button>

      <div className="bookmarks-container">
        {loading && (
          <div className="loading-state">
            <p>Loading bookmarks...</p>
          </div>
        )}

        {!loading && bookmarks.length === 0 && (
          <div className="empty-state">
            <p>No saved articles yet</p>
            <p className="empty-subtitle">Star articles to save them here</p>
          </div>
        )}

        {!loading && bookmarks.length > 0 && (
          <>
            <p className="bookmarks-count">{bookmarks.length} saved article(s)</p>
            {bookmarks.map((article) => (
              <ArticleCard 
                key={article.id} 
                article={article}
                onRemove={() => handleRemoveBookmark(article.id)}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default BookmarksPage;
