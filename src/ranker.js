import { KEYWORDS, RANKING_WEIGHTS } from './config.js';

/**
 * Calculate relevance score based on keywords
 */
function calculateKeywordScore(text, keywords) {
  const lowerText = text.toLowerCase();
  let score = 0;
  let matchCount = 0;

  for (const keyword of keywords) {
    if (lowerText.includes(keyword)) {
      score += 1;
      matchCount++;
    }
  }

  return matchCount > 0 ? Math.min(score, keywords.length) : 0;
}

/**
 * Calculate recency score (newer = higher score)
 */
function calculateRecencyScore(publishedAt, maxAgeMs = 30 * 24 * 60 * 60 * 1000) {
  const ageMs = Date.now() - publishedAt.getTime();
  const normalizedAge = Math.max(0, 1 - ageMs / maxAgeMs);
  return normalizedAge;
}

/**
 * Rank articles based on relevance and metadata
 */
export function rankArticles(articles) {
  const scoredArticles = articles.map(article => {
    const title = article.title || '';
    const description = article.description || '';
    const combinedText = `${title} ${description}`;

    // Calculate individual scores
    const aiScore = calculateKeywordScore(combinedText, KEYWORDS.ai);
    const techScore = calculateKeywordScore(combinedText, KEYWORDS.tech);
    const ecomScore = calculateKeywordScore(combinedText, KEYWORDS.ecommerce);
    const pimScore = calculateKeywordScore(combinedText, KEYWORDS.pim);
    const agenticScore = calculateKeywordScore(combinedText, KEYWORDS.agentic);

    // Determine primary category and relevance
    const categories = [
      { name: 'AI', score: aiScore },
      { name: 'Tech', score: techScore },
      { name: 'E-Commerce', score: ecomScore },
      { name: 'PIM/MDM', score: pimScore },
      { name: 'Agentic', score: agenticScore }
    ];

    const topCategory = categories.reduce((a, b) => a.score > b.score ? a : b);
    const totalKeywordScore = aiScore + techScore + ecomScore + pimScore + agenticScore;

    // Normalize keyword score to 0-1
    const maxPossibleScore = Math.max(
      KEYWORDS.ai.length,
      KEYWORDS.tech.length,
      KEYWORDS.ecommerce.length,
      KEYWORDS.pim.length,
      KEYWORDS.agentic.length
    );
    const normalizedKeywordScore = Math.min(totalKeywordScore / (maxPossibleScore * 2), 1);

    // Calculate recency score
    const recencyScore = calculateRecencyScore(article.publishedAt);

    // Final composite score
    const compositeScore =
      (normalizedKeywordScore * RANKING_WEIGHTS.keywordMatch) +
      (recencyScore * RANKING_WEIGHTS.recency) +
      (article.credibility * RANKING_WEIGHTS.credibility);

    return {
      ...article,
      score: compositeScore,
      relevanceCategory: topCategory.name,
      keywordMatches: totalKeywordScore
    };
  });

  // Sort by score descending
  return scoredArticles.sort((a, b) => b.score - a.score);
}

/**
 * Get top N articles from ranked list, ensuring source diversity.
 * First picks the best article from each source, then fills remaining
 * slots with the next highest-scoring articles overall.
 */
export function getTopArticles(rankedArticles, limit = 5) {
  const selected = [];
  const usedSources = new Set();

  // Pass 1: best article per source
  for (const article of rankedArticles) {
    if (!usedSources.has(article.source)) {
      selected.push(article);
      usedSources.add(article.source);
    }
    if (selected.length >= limit) break;
  }

  // Pass 2: fill remaining slots with next best (any source)
  if (selected.length < limit) {
    const selectedIds = new Set(selected.map(a => a.id));
    for (const article of rankedArticles) {
      if (!selectedIds.has(article.id)) {
        selected.push(article);
        if (selected.length >= limit) break;
      }
    }
  }

  // Re-sort by score so the final list is still ordered by relevance
  return selected.sort((a, b) => b.score - a.score);
}

/**
 * Group articles by category
 */
export function groupByCategory(articles) {
  const grouped = {
    'AI': [],
    'Tech': [],
    'E-Commerce': [],
    'PIM/MDM': [],
    'Agentic': [],
    'Other': []
  };

  articles.forEach(article => {
    const category = article.relevanceCategory || 'Other';
    if (grouped[category]) {
      grouped[category].push(article);
    } else {
      grouped['Other'].push(article);
    }
  });

  return grouped;
}
