import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { SOURCES, TIME_RANGES, TOP_HEADLINES } from './config.js';
import { fetchAllRSS, scrapWebsite } from './fetcher.js';
import { rankArticles, getTopArticles } from './ranker.js';
import { filterByDateRange, deduplicateArticles, filterQuality } from './filter.js';
import { generateMarkdown, generateHTML } from './output.js';

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    range: 'week',
    output: 'both', // 'md', 'html', 'both'
    limit: TOP_HEADLINES
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--range' && args[i + 1]) {
      options.range = args[i + 1];
      i++;
    } else if (args[i] === '--output' && args[i + 1]) {
      options.output = args[i + 1];
      i++;
    } else if (args[i] === '--limit' && args[i + 1]) {
      options.limit = parseInt(args[i + 1], 10);
      i++;
    }
  }

  return options;
}

/**
 * Main scraping function
 */
async function scrapeNews() {
  const options = parseArgs();

  console.log(chalk.cyan.bold('\n🚀 Zeitungsjunge - News Aggregator\n'));

  // Validate range
  if (!TIME_RANGES[options.range]) {
    console.error(chalk.red(`❌ Invalid range: ${options.range}`));
    console.log(chalk.yellow(`Available ranges: ${Object.keys(TIME_RANGES).join(', ')}`));
    process.exit(1);
  }

  const rangeLabel = TIME_RANGES[options.range].label;

  // Step 1: Fetch articles
  let spinner = ora({
    text: chalk.blue('Fetching articles from RSS feeds...'),
    prefixText: '1️⃣ '
  }).start();

  try {
    const articles = await fetchAllRSSWithFallback(SOURCES);
    spinner.succeed(chalk.green(`Fetched ${articles.length} articles`));

    // Step 2: Quality filtering
    spinner = ora({
      text: chalk.blue('Filtering low-quality articles...'),
      prefixText: '2️⃣ '
    }).start();

    let filtered = filterQuality(articles);
    spinner.succeed(chalk.green(`Quality filtered: ${filtered.length} articles`));

    // Step 3: Deduplication
    spinner = ora({
      text: chalk.blue('Removing duplicates...'),
      prefixText: '3️⃣ '
    }).start();

    filtered = deduplicateArticles(filtered);
    spinner.succeed(chalk.green(`Deduplicated: ${filtered.length} unique articles`));

    // Step 4: Date filtering
    spinner = ora({
      text: chalk.blue(`Filtering by date range: ${rangeLabel}...`),
      prefixText: '4️⃣ '
    }).start();

    filtered = filterByDateRange(filtered, options.range);
    spinner.succeed(chalk.green(`Date filtered: ${filtered.length} articles`));

    // Step 5: Ranking
    spinner = ora({
      text: chalk.blue('Ranking articles by relevance...'),
      prefixText: '5️⃣ '
    }).start();

    const ranked = rankArticles(filtered);
    spinner.succeed(chalk.green(`Ranked ${ranked.length} articles`));

    // Step 6: Get top articles
    spinner = ora({
      text: chalk.blue(`Selecting top ${options.limit} per category...`),
      prefixText: '6️⃣ '
    }).start();

    const topArticles = getTopArticles(ranked, options.limit);
    spinner.succeed(chalk.green(`Selected ${topArticles.length} top articles`));

    // Step 7: Generate output
    spinner = ora({
      text: chalk.blue('Generating output files...'),
      prefixText: '7️⃣ '
    }).start();

    const outputDir = path.join(process.cwd(), 'output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().split('T')[0];

    if (options.output === 'md' || options.output === 'both') {
      const markdownContent = generateMarkdown(topArticles, options.range, rangeLabel);
      const mdPath = path.join(outputDir, `headlines-${options.range}-${timestamp}.md`);
      fs.writeFileSync(mdPath, markdownContent);
      console.log(chalk.green(`   ✓ Markdown: ${mdPath}`));
    }

    if (options.output === 'html' || options.output === 'both') {
      const htmlContent = generateHTML(topArticles, options.range, rangeLabel);
      const htmlPath = path.join(outputDir, `headlines-${options.range}-${timestamp}.html`);
      fs.writeFileSync(htmlPath, htmlContent);
      console.log(chalk.green(`   ✓ HTML: ${htmlPath}`));
    }

    // Also update latest files
    if (options.output === 'md' || options.output === 'both') {
      const markdownContent = generateMarkdown(topArticles, options.range, rangeLabel);
      const mdPath = path.join(outputDir, `latest-${options.range}.md`);
      fs.writeFileSync(mdPath, markdownContent);
    }

    if (options.output === 'html' || options.output === 'both') {
      const htmlContent = generateHTML(topArticles, options.range, rangeLabel);
      const htmlPath = path.join(outputDir, `latest-${options.range}.html`);
      fs.writeFileSync(htmlPath, htmlContent);
    }

    spinner.succeed(chalk.green('Output files generated'));

    // Summary
    console.log(chalk.cyan.bold('\n📊 Summary\n'));
    console.log(chalk.gray(`  Time Range: ${rangeLabel}`));
    console.log(chalk.gray(`  Total Scraped: ${articles.length}`));
    console.log(chalk.gray(`  After Filtering: ${filtered.length}`));
    console.log(chalk.gray(`  Top Articles: ${topArticles.length}`));
    console.log(chalk.cyan(`\n✅ Done!\n`));

    process.exit(0);
  } catch (error) {
    spinner.fail(chalk.red(error.message));
    console.error(chalk.red(error));
    process.exit(1);
  }
}

/**
 * Fetch RSS feeds with fallback to web scraping
 */
async function fetchAllRSSWithFallback(sources) {
  const results = [];

  for (const source of sources) {
    try {
      const articles = await fetchAllRSS([source]);
      if (articles.length > 0) {
        results.push(...articles);
      } else {
        // Fallback to web scraping
        const scrapedArticles = await scrapWebsite(source);
        results.push(...scrapedArticles);
      }
    } catch (error) {
      console.warn(chalk.yellow(`⚠️  Error fetching ${source.name}: ${error.message}`));
      // Try web scraping as fallback
      try {
        const scrapedArticles = await scrapWebsite(source);
        results.push(...scrapedArticles);
      } catch (scrapeError) {
        console.warn(chalk.yellow(`⚠️  Web scraping also failed for ${source.name}`));
      }
    }
  }

  return results;
}

// Run the scraper
scrapeNews();
