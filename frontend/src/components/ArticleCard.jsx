import { useState } from 'react';
import { useBookmarkStore } from '../store';
import { bookmarkAPI } from '../api/client';
import './ArticleCard.css';

const ArticleCard = ({ article, onSummarize }) => {
  const [isSummarizing, setIsSummarizing] = useState(false);
  const { isBookmarked, addBookmark, removeBookmark } = useBookmarkStore();
  const bookmarked = isBookmarked(article.id);

  const handleBookmarkToggle = async () => {
    try {
      if (bookmarked) {
        await bookmarkAPI.removeBookmark(article.id);
        removeBookmark(article.id);
      } else {
        await bookmarkAPI.addBookmark(article.id);
        addBookmark(article.id);
      }
    } catch (error) {
      console.error('Bookmark error:', error);
    }
  };

  const handleSummarize = async () => {
    if (onSummarize) {
      setIsSummarizing(true);
      try {
        await onSummarize(article.id);
      } finally {
        setIsSummarizing(false);
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <article className="article-card">
      {article.image_url && (
        <img src={article.image_url} alt={article.title} className="article-image" />
      )}
      
      <div className="article-content">
        <div className="article-header">
          <h3 className="article-title">{article.title}</h3>
          <button 
            className={`bookmark-btn ${bookmarked ? 'active' : ''}`}
            onClick={handleBookmarkToggle}
            title={bookmarked ? 'Remove bookmark' : 'Add bookmark'}
          >
            {bookmarked ? '★' : '☆'}
          </button>
        </div>

        {article.author && (
          <p className="article-author">By {article.author}</p>
        )}

        <p className="article-description">{article.description}</p>

        {article.summary && (
          <div className="article-summary">
            <strong>Summary:</strong>
            <p>{article.summary}</p>
          </div>
        )}

        <div className="article-metadata">
          <span className="region-badge">{article.region}</span>
          <span className="score">{(article.importance_score * 100).toFixed(0)}%</span>
          <span className="date">{formatDate(article.published_at)}</span>
        </div>

        <div className="article-actions">
          <a href={article.url} target="_blank" rel="noopener noreferrer" className="read-btn">
            Read Article
          </a>
          {!article.summary && (
            <button 
              className="summarize-btn"
              onClick={handleSummarize}
              disabled={isSummarizing}
            >
              {isSummarizing ? 'Generating...' : 'AI Summary'}
            </button>
          )}
        </div>
      </div>
    </article>
  );
};

export default ArticleCard;
