# Task 6: Article + Scheme Scraper & Summary Report

## Overview
This project implements a web scraper that extracts articles from Microsoft Research Blog and schemes from MyScheme Portal. The scraper handles JavaScript-rendered content, pagination, and generates comprehensive reports with structured data output.

## Architecture

```
Task_6/
├── scraper.py          # Main scraper implementation
├── requirements.txt    # Python dependencies
├── setup.py           # Automated setup script
├── README.md          # This documentation
├── SUMMARY.md         # Project summary and challenges
├── scraped_data.json  # Output JSON file (generated)
├── scraped_data.csv   # Output CSV file (generated)
└── summary_report.json # Technical report (generated)
```

## Flow Diagram

```
┌─────────────────┐
│   Start Scraper │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Initialize      │
│ Playwright      │
│ Browser         │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Scrape Microsoft│
│ Research Blog   │
│ (with pagination)│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Wait 2 secs   │
│  (Rate limiting)│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Scrape MyScheme│
│     Portal      │
│ (with pagination)│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Save Results   │
│ (JSON + CSV)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Generate Summary│
│ & Analysis Report│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Close Browser   │
│   & Complete    │
└─────────────────┘
```

## Quick Start

### Automated Setup
```bash
python setup.py
```

### Manual Setup
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Run the scraper:
   ```bash
   python scraper.py
   ```

## Technical Implementation

### Scraping Strategy
- **Playwright Integration**: Handles JavaScript-rendered content with headless Chromium
- **Async Architecture**: Efficient concurrent processing with proper resource management
- **Multi-Selector Strategy**: Robust element detection with fallback mechanisms
- **Pagination Handling**: Automatic detection and handling of "Load More" and "Next" buttons
- **Rate Limiting**: Respectful delays between requests and pages

### Data Processing
- **URL Normalization**: Converts relative URLs to absolute URLs
- **Data Validation**: Handles missing fields gracefully
- **Text Processing**: Truncates descriptions to 200 characters
- **Timestamp Tracking**: Adds scraping timestamp to each item

### Error Handling
- **Graceful Degradation**: Continues scraping even if individual items fail
- **Comprehensive Logging**: Detailed progress and error information
- **Fallback Mechanisms**: Multiple selector strategies for robust extraction
- **Resource Cleanup**: Proper browser and resource management

## Output Files

### scraped_data.json
Structured JSON format with all scraped items:
```json
{
  "source": "Microsoft Research Blog",
  "title": "Article Title",
  "link": "https://example.com/article",
  "description": "Article description...",
  "scraped_at": "2025-01-XX",
  "page": 1
}
```

### scraped_data.csv
Same data in CSV format for spreadsheet analysis.

### summary_report.json
Comprehensive technical analysis including:
- Total items scraped per source
- Page structure challenges identified
- Anti-bot mechanisms encountered
- Data completeness evaluation
- Technical approach details
- Production recommendations

## Features Demonstrated

### ✅ Dynamic Content Handling
- JavaScript-rendered content processing
- Network idle waiting for complete page loading
- Modern website compatibility

### ✅ Pagination Support
- Automatic "Load More" button detection
- "Next" page link handling
- Configurable page limits (3 pages per site for demo)

### ✅ Robust Error Handling
- Individual item failure recovery
- Missing element graceful handling
- Comprehensive error logging

### ✅ Professional Data Output
- Multiple output formats (JSON, CSV)
- Structured data with metadata
- Technical analysis and reporting

### ✅ Production-Ready Architecture
- Async processing for efficiency
- Proper resource management
- Configurable and extensible design

## Challenges Addressed

### Page Structure Challenges
- Dynamic class names and React components
- Inconsistent HTML structures across pages
- Variable article/scheme card formats

### Anti-Bot Mechanisms
- Rate limiting protection
- User-Agent validation requirements
- JavaScript execution requirements

### Data Quality Issues
- Missing descriptions and malformed links
- Relative URL conversion needs
- Variable content completeness

## Demo Commands

```bash
# Quick setup and run
python setup.py
python scraper.py

# View results
cat scraped_data.json | jq '.[0:2]'  # First 2 items
head -5 scraped_data.csv             # CSV preview
cat summary_report.json | jq '.summary'  # Summary overview

# Check logs during execution
python scraper.py 2>&1 | tee scraper.log
```

## Production Considerations

### Current Limitations
- Limited to 3 pages per site (demo constraint)
- Single browser instance (no parallel processing)
- File-based storage (no database integration)
- Basic pagination detection

### Recommended Improvements
- Database integration for scalable storage
- Distributed scraping with multiple browser instances
- Advanced retry mechanisms with exponential backoff
- Proxy rotation for large-scale operations
- Real-time monitoring and alerting

## Testing

Verify successful installation and execution:
```bash
# Check Python version (3.8+ required)
python --version

# Verify dependencies
pip list | grep playwright

# Test scraper execution
python scraper.py

# Validate output files
ls -la scraped_data.*
ls -la summary_report.json
```

## Troubleshooting

### Common Issues
- **Playwright not found**: Run `playwright install chromium`
- **Permission errors**: Ensure proper virtual environment activation
- **Network timeouts**: Check internet connection and site accessibility
- **Empty results**: Sites may have changed structure; check logs for errors

### Debug Mode
Enable detailed logging by modifying the script:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Notes

- Scraper respects rate limits with 2-second delays between sites
- Limited to 3 pages per site to avoid overwhelming servers
- All output files are UTF-8 encoded for international character support
- Browser runs in headless mode for efficiency
- Comprehensive error handling ensures script completion even with partial failures

This implementation demonstrates modern web scraping techniques suitable for production environments with proper scaling and infrastructure support.