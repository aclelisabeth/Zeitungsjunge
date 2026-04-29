import { subDays, isAfter, isSameDay } from 'date-fns';

/**
 * Filter articles by date range
 */
export function filterByDateRange(articles, range = 'week') {
  const rangeMap = {
    today: 0,
    week: 7,
    month: 30,
    quarter: 90,
    all: Infinity
  };

  const daysBack = rangeMap[range] || 7;
  
  if (daysBack === Infinity) {
    return articles;
  }

  const cutoffDate = subDays(new Date(), daysBack);

  return articles.filter(article => {
    const articleDate = new Date(article.publishedAt);
    return isAfter(articleDate, cutoffDate) || isSameDay(articleDate, cutoffDate);
  });
}

/**
 * Group articles by date
 */
export function groupByDate(articles) {
  const grouped = {};

  articles.forEach(article => {
    const date = new Date(article.publishedAt);
    const dateKey = date.toISOString().split('T')[0]; // YYYY-MM-DD

    if (!grouped[dateKey]) {
      grouped[dateKey] = [];
    }
    grouped[dateKey].push(article);
  });

  // Sort by date descending
  const sorted = {};
  Object.keys(grouped).sort().reverse().forEach(key => {
    sorted[key] = grouped[key];
  });

  return sorted;
}

/**
 * Remove duplicate articles
 */
export function deduplicateArticles(articles) {
  const seen = new Set();
  const unique = [];

  articles.forEach(article => {
    // Normalize title for comparison
    const normalizedTitle = article.title
      .toLowerCase()
      .trim()
      .replace(/[^\w\s]/g, '');

    if (!seen.has(normalizedTitle)) {
      seen.add(normalizedTitle);
      unique.push(article);
    }
  });

  return unique;
}

/**
 * Remove articles with empty or minimal content
 */
export function filterQuality(articles) {
  return articles.filter(article => {
    const titleLength = (article.title || '').length;
    const descriptionLength = (article.description || '').length;
    const hasLink = !!article.link;

    return titleLength >= 10 && descriptionLength >= 20 && hasLink;
  });
}
