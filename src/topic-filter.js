import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

let topicsConfig = null;

/**
 * Load topics configuration from topics.json
 */
function loadTopics() {
  if (topicsConfig) return topicsConfig;

  const topicsPath = path.join(process.cwd(), 'topics.json');
  const content = fs.readFileSync(topicsPath, 'utf-8');
  topicsConfig = JSON.parse(content);
  return topicsConfig;
}

/**
 * Get available topic names
 */
export function getAvailableTopics() {
  const config = loadTopics();
  return Object.keys(config.topics);
}

/**
 * Get current extrablatt topic
 */
export function getCurrentExtrablattTopic() {
  const config = loadTopics();
  return config.extrablatt;
}

/**
 * Get topic configuration
 */
export function getTopicConfig(topicName) {
  const config = loadTopics();
  return config.topics[topicName] || null;
}

/**
 * Check if article matches topic keywords (case-insensitive)
 */
function matchesKeywords(article, keywords) {
  const text = `${article.title} ${article.description} ${article.source}`.toLowerCase();
  return keywords.some(keyword => text.includes(keyword.toLowerCase()));
}

/**
 * Filter articles by topic
 * Returns up to maxResults articles matching the topic
 */
export function filterByTopic(articles, topicName, maxResults = 20) {
  const topicConfig = getTopicConfig(topicName);
  
  if (!topicConfig) {
    return [];
  }

  const matching = articles.filter(article => 
    matchesKeywords(article, topicConfig.keywords)
  );

  // Sort by relevance score (highest first)
  matching.sort((a, b) => b.score - a.score);

  return matching.slice(0, maxResults);
}

/**
 * Search within topic articles
 * Returns articles matching both topic AND search query
 */
export function searchWithinTopic(articles, topicName, searchQuery) {
  if (!searchQuery || searchQuery.trim().length === 0) {
    return filterByTopic(articles, topicName);
  }

  const topicFiltered = filterByTopic(articles, topicName, 100);
  const query = searchQuery.toLowerCase();

  return topicFiltered.filter(article => {
    const titleMatch = article.title.toLowerCase().includes(query);
    const descMatch = article.description.toLowerCase().includes(query);
    const sourceMatch = article.source.toLowerCase().includes(query);
    return titleMatch || descMatch || sourceMatch;
  });
}

/**
 * Get fallback topics if primary topic has insufficient articles
 * Searches in priority order until we have minimum threshold
 */
export function expandTopicSearch(articles, topicName, minRequired = 3) {
  const primaryResults = filterByTopic(articles, topicName, 100);

  if (primaryResults.length >= minRequired) {
    return primaryResults.slice(0, 20);
  }

  // Primary topic insufficient, expand search
  const availableTopics = getAvailableTopics();
  const otherTopics = availableTopics.filter(t => t !== topicName);
  
  let allResults = [...primaryResults];

  for (const topic of otherTopics) {
    if (allResults.length >= minRequired) {
      break;
    }
    const additional = filterByTopic(articles, topic, 100);
    allResults = [...allResults, ...additional];
  }

  return allResults.slice(0, 20);
}

/**
 * Get all topics with their metadata
 */
export function getAllTopicsMetadata() {
  const config = loadTopics();
  return config.topics;
}
