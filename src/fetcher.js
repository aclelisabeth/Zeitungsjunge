import Parser from 'rss-parser';
import axios from 'axios';

const parser = new Parser({
  timeout: 10000,
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  }
});

/**
 * Fetch articles from RSS feed
 */
export async function fetchRSS(source) {
  try {
    const feed = await parser.parseURL(source.rssUrl);
    
    const articles = (feed.items || []).map(item => ({
      id: `${source.name}-${item.guid || item.link}`.replace(/[^a-zA-Z0-9-_]/g, ''),
      title: item.title || 'Untitled',
      description: item.contentSnippet || item.summary || item.description || '',
      link: item.link || '',
      source: source.name,
      sourceUrl: source.url,
      publishedAt: new Date(item.pubDate || item.isoDate || Date.now()),
      author: item.creator || item.author || '',
      category: item.categories?.[0] || 'General',
      credibility: source.credibility,
      country: source.country
    }));

    return articles;
  } catch (error) {
    console.error(`❌ Error fetching RSS from ${source.name}:`, error.message);
    return [];
  }
}

/**
 * Fetch multiple RSS feeds in parallel
 */
export async function fetchAllRSS(sources) {
  const results = await Promise.all(
    sources.map(source => fetchRSS(source))
  );
  
  // Flatten array
  return results.flat();
}

/**
 * Web scraping fallback for sources without proper RSS
 */
export async function scrapWebsite(source) {
  try {
    const { data } = await axios.get(source.url, {
      timeout: 10000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    // Basic HTML extraction - returns meta description as fallback
    const titleMatch = data.match(/<title[^>]*>([^<]+)<\/title>/i);
    const descMatch = data.match(/<meta\s+name="description"\s+content="([^"]+)"/i);

    return [{
      id: `${source.name}-${Date.now()}`,
      title: titleMatch?.[1] || source.name,
      description: descMatch?.[1] || 'Latest news',
      link: source.url,
      source: source.name,
      sourceUrl: source.url,
      publishedAt: new Date(),
      credibility: source.credibility * 0.8, // Lower credibility for scraped content
      country: source.country
    }];
  } catch (error) {
    console.error(`⚠️  Web scraping failed for ${source.name}:`, error.message);
    return [];
  }
}
