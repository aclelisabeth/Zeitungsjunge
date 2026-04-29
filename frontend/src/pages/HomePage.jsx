import { useState, useEffect } from 'react';
import { useNewsStore, usePreferencesStore, useUIStore } from '../store';
import { newsAPI } from '../api/client';
import ArticleCard from '../components/ArticleCard';
import './HomePage.css';

const HomePage = () => {
  const [timeRange, setTimeRange] = useState('today');
  const [region, setRegion] = useState('global');
  const [loading, setLoading] = useState(true);
  const { articles, setArticles, setLoading: setNewsLoading } = useNewsStore();
  const { getTimeRange, getRegions } = usePreferencesStore();
  const { showNotification } = useUIStore();

  useEffect(() => {
    loadArticles();
  }, [timeRange, region]);

  const loadArticles = async () => {
    setLoading(true);
    setNewsLoading(true);
    try {
      const response = await newsAPI.getNews(
        timeRange,
        region === 'global' ? null : region,
        20
      );
      setArticles(response.data.items || []);
    } catch (error) {
      showNotification('Failed to load articles', 'error');
      console.error('Error loading articles:', error);
    } finally {
      setLoading(false);
      setNewsLoading(false);
    }
  };

  const handleSummarize = async (articleId) => {
    try {
      await newsAPI.summarizeArticle(articleId);
      await loadArticles();
      showNotification('Summary generated successfully', 'success');
    } catch (error) {
      showNotification('Failed to generate summary', 'error');
      console.error('Error summarizing:', error);
    }
  };

  return (
    <div className="home-page">
      <div className="page-header">
        <h1>News Feed</h1>
        <p>Stay informed with top-quality articles from trusted sources</p>
      </div>

      <div className="filters-container">
        <div className="filter-group">
          <label htmlFor="time-range">Time Range:</label>
          <select 
            id="time-range"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            disabled={loading}
          >
            <option value="today">Today</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="60d">Last 60 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="region">Region:</label>
          <select 
            id="region"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            disabled={loading}
          >
            <option value="global">Global</option>
            <option value="us">United States</option>
            <option value="de">Germany</option>
            <option value="eu">Europe</option>
          </select>
        </div>

        <button 
          onClick={loadArticles}
          disabled={loading}
          className="refresh-btn"
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <div className="articles-container">
        {loading && (
          <div className="loading-state">
            <p>Loading articles...</p>
          </div>
        )}

        {!loading && articles.length === 0 && (
          <div className="empty-state">
            <p>No articles found</p>
            <p className="empty-subtitle">Try changing your filters or check back later</p>
          </div>
        )}

        {!loading && articles.length > 0 && (
          <>
            <p className="articles-count">Found {articles.length} articles</p>
            {articles.map((article) => (
              <ArticleCard 
                key={article.id} 
                article={article}
                onSummarize={handleSummarize}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default HomePage;
