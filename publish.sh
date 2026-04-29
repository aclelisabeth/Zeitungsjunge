#!/bin/bash

# Script to generate and publish headlines to GitHub Pages
# Usage: ./publish.sh [range]

RANGE=${1:-week}
OUTPUT_DIR="output"
GITHUB_PAGES_DIR="docs"

echo "🚀 Generating headlines for range: $RANGE"
node src/cli.js --range $RANGE

echo "📁 Creating GitHub Pages directory..."
mkdir -p $GITHUB_PAGES_DIR

echo "📋 Copying files..."
cp $OUTPUT_DIR/latest-$RANGE.html $GITHUB_PAGES_DIR/index.html
cp $OUTPUT_DIR/latest-today.html $GITHUB_PAGES_DIR/today.html 2>/dev/null || true
cp $OUTPUT_DIR/latest-week.html $GITHUB_PAGES_DIR/week.html 2>/dev/null || true
cp $OUTPUT_DIR/latest-month.html $GITHUB_PAGES_DIR/month.html 2>/dev/null || true
cp $OUTPUT_DIR/latest-quarter.html $GITHUB_PAGES_DIR/quarter.html 2>/dev/null || true

# Create a simple index if it doesn't exist
if [ ! -f $GITHUB_PAGES_DIR/index.html ]; then
  cp $OUTPUT_DIR/latest-week.html $GITHUB_PAGES_DIR/index.html
fi

echo "✅ Files ready for GitHub Pages!"
echo "📍 Location: ./$GITHUB_PAGES_DIR/"
