# Task 6: Article + Scheme Scraper & Summary Report

## Overview
This project implements a simple web scraper that extracts articles from Microsoft Research Blog and schemes from MyScheme Portal. The scraper handles basic web scraping challenges and generates structured data output with a comprehensive summary report.

## Architecture

```
Task_6/
├── scraper.py          # Main scraper script
├── requirements.txt    # Python dependencies
├── README.md          # This documentation
├── scraped_data.json  # Output JSON file (generated)
├── scraped_data.csv   # Output CSV file (generated)
└── summary_report.json # Summary report (generated)
```

## Flow Diagram

```
┌─────────────────┐
│   Start Scraper │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Scrape Microsoft│
│ Research Blog   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Wait 2 secs   │
│  (Be respectful)│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Scrape MyScheme│
│     Portal      │
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
│     Report      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Complete      │
└─────────────────┘
```

## Environment Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
1. Clone the repository and navigate to Task_6 folder
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment:
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## How to Run

### Basic Execution
```bash
python scraper.py
```

### Expected Output
The scraper will:
1. Display progress logs in the terminal
2. Generate `scraped_data.json` with all scraped items
3. Generate `scraped_data.csv` with the same data in CSV format
4. Generate `summary_report.json` with analysis and challenges

### Sample Output Structure
```json
{
  "source": "Microsoft Research Blog",
  "title": "Article Title",
  "link": "https://example.com/article",
  "description": "Article description...",
  "scraped_at": "2025-01-XX"
}
```

## Technical Implementation

### Scraping Strategy
- **Microsoft Research Blog**: Uses Playwright for JavaScript-rendered content, handles pagination with "Load More" buttons
- **MyScheme Portal**: Multiple selector strategies for robust element discovery, pagination detection
- **Error Handling**: Graceful fallbacks for missing elements, continues scraping on individual failures  
- **Rate Limiting**: Respectful delays between pages and actions
- **Pagination**: Automatically detects and handles "Load More" and "Next" buttons (limited to 3 pages per site for demo)

### Data Processing
- Extracts title, link, and description for each item
- Converts relative URLs to absolute URLs
- Truncates descriptions to 200 characters
- Adds timestamp for each scraped item

### Output Formats
- **JSON**: Structured data for programmatic use
- **CSV**: Tabular format for spreadsheet analysis
- **Summary Report**: Comprehensive analysis of scraping challenges

## Challenges Identified

### Page Structure Challenges
- Dynamic class names that may change over time
- Complex nested HTML structures
- Inconsistent article/scheme card formats

### Anti-Bot Mechanisms
- Rate limiting protection
- User-Agent validation requirements
- JavaScript-rendered content (not handled in simple scraper)

### Data Completeness
- Some articles may lack complete descriptions
- Relative URLs need conversion to absolute
- Variable HTML structures across different pages

## Limitations & Improvements

### Current Limitations
- Limited to 3 pages per site for demo purposes
- Basic pagination detection (may not work on all site structures)
- No proxy support for large-scale scraping
- Single browser instance (no parallel scraping)

### Future Improvements
- Implement retry mechanisms with exponential backoff
- Add proxy rotation for large-scale operations
- Database storage for better data management
- Change detection for incremental updates
- Distributed scraping with multiple browser instances

## Demo Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run the scraper
python scraper.py

# View results
cat scraped_data.json

# Check summary report
cat summary_report.json

# View CSV output
head scraped_data.csv
```

## Testing

The scraper can be tested by running:
```bash
# Install dependencies first
pip install -r requirements.txt
playwright install chromium

# Run the scraper
python scraper.py
```

Check the generated files to verify successful scraping:
- `scraped_data.json` - Contains all scraped items with pagination info
- `scraped_data.csv` - Same data in CSV format
- `summary_report.json` - Comprehensive analysis and challenges

## Notes

- The scraper uses Playwright for JavaScript-rendered content
- Pagination is automatically detected and handled (limited to 3 pages per site)
- Error handling ensures the script continues even if individual items fail
- All output files are UTF-8 encoded to handle international characters
- Comprehensive logging provides visibility into the scraping process
- Respectful delays prevent overwhelming target servers