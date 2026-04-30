// Configuration for news sources with scraping strategies
export const SOURCES = [
  {
    name: "TechCrunch",
    url: "https://techcrunch.com",
    rssUrl: "https://techcrunch.com/feed/",
    country: "US",
    credibility: 0.95,
    scrapingStrategy: "rss-primary"
  },
  {
    name: "etailment",
    url: "https://etailment.de",
    rssUrl: "https://etailment.de/feed/",
    country: "DE",
    credibility: 0.85,
    scrapingStrategy: "rss-primary"
  },
  {
    name: "The Verge",
    url: "https://theverge.com",
    rssUrl: "https://www.theverge.com/rss/index.xml",
    country: "US",
    credibility: 0.90,
    scrapingStrategy: "rss-primary"
  },
  {
    name: "ArsTechnica",
    url: "https://arstechnica.com",
    rssUrl: "https://feeds.arstechnica.com/arstechnica/index",
    country: "US",
    credibility: 0.90,
    scrapingStrategy: "rss-primary"
  },
  {
    name: "Wired",
    url: "https://wired.com",
    rssUrl: "https://www.wired.com/feed/rss",
    country: "US",
    credibility: 0.85,
    scrapingStrategy: "rss-primary"
  },
  {
    name: "PIMvendors",
    url: "https://pimvendors.com/",
    rssUrl: "https://pimvendors.com/feed/rss",
    country: "NL",
    credibility: 0.65,
    scrapingStrategy: "rss-primary"
  },
  {
    name: "OpenAI",
    url: "https://openai.com/de-DE/news/",
    rssUrl: "https://openai.com/news/rss.xml",
    country: "US",
    credibility: 1.0,
    scrapingStrategy: "rss-primary"
  }
];

// Keywords for ranking and categorization
export const KEYWORDS = {
  ai: ["artificial intelligence", "ai", "machine learning", "ml", "gpt", "llm", "neural", "deep learning"],
  tech: ["tech", "technology", "software", "hardware", "cloud", "web3", "blockchain", "startup"],
  ecommerce: ["e-commerce", "ecommerce", "e-com", "shopping", "retail", "marketplace", "checkout", "payment"],
  pim: ["pim", "product information", "mdm", "master data", "dam", "digital asset"],
  agentic: ["agentic", "agent", "autonomous", "workflow automation", "robotic process", "rpa"],
  general: ["news", "update", "launch", "acquisition", "funding", "partnership"]
};

// Scoring weights for ranking
export const RANKING_WEIGHTS = {
  keywordMatch: 0.40,      // 40% - keyword relevance
  recency: 0.25,            // 25% - how recent
  credibility: 0.20,        // 20% - source credibility
  frequency: 0.15           // 15% - how many sources report it
};

// Time ranges for filtering
export const TIME_RANGES = {
  today: { days: 0, label: "Today" },
  week: { days: 7, label: "Last 7 Days" },
  month: { days: 30, label: "Last 30 Days" },
  quarter: { days: 90, label: "Last 90 Days" },
  all: { days: Infinity, label: "All Articles" }
};

export const TOP_HEADLINES = 5; // Top 5 per time range
