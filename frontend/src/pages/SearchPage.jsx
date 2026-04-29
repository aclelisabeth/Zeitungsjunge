import { useState } from 'react';
import { useNewsStore, useUIStore } from '../store';
import { newsAPI } from '../api/client';
import ArticleCard from '../components/ArticleCard';
import './SearchPage.css';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [region, setRegion] = useState('global');
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const { articles, setArticles } = useNewsStore();
  const { showNotification } = useUIStore();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      showNotification('Please enter a search query', 'warning');
      return;
    }

    setLoading(true);
    setSearched(true);
    try {
      const response = await newsAPI.searchNews(
        query,
        region === 'global' ? null : region,
        30,
        20
      );
      setArticles(response.data.results || []);
    } catch (error) {
      showNotification('Search failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async (articleId) => {
    try {
      await newsAPI.summarizeArticle(articleId);
      const response = await newsAPI.searchNews(query, region === 'global' ? null : region, 30, 20);
      setArticles(response.data.results || []);
      showNotification('Summary generated', 'success');
    } catch (error) {
      showNotification('Failed to generate summary', 'error');
    }
  };

  return (
    <div className="search-page">
      <h1>Search Articles</h1>

      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search articles..."
            disabled={loading}
            className="search-input"
          />
          <button type="submit" disabled={loading} className="search-btn">
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        <div className="search-filters">
          <label htmlFor="search-region">Region:</label>
          <select 
            id="search-region"
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
      </form>

      <div className="search-results">
        {!searched && (
          <div className="search-hint">
            <p>Enter a search term to find articles</p>
          </div>
        )}

        {searched && loading && (
          <div className="loading-state">
            <p>Searching...</p>
          </div>
        )}

        {searched && !loading && articles.length === 0 && (
          <div className="empty-state">
            <p>No results found for "{query}"</p>
          </div>
        )}

        {searched && !loading && articles.length > 0 && (
          <>
            <p className="results-count">Found {articles.length} results</p>
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

export default SearchPage;
