# Product Auditor Tool Documentation

## Overview

The Product Auditor Tool is designed to audit product information scraped from websites. It uses AI to review various aspects of scraped product data including URL validity, title/description consistency, category accuracy, and keyword relevance.

## Features

- **URL Validation**: Checks if the URL is a valid product page (not category pages, success case pages, or multi-product listings)
- **Title Consistency Check**: Verifies that scraped titles match the product information from the source URL
- **Description Consistency Check**: Verifies that scraped descriptions are consistent with the product title and URL
- **Category Review**: Evaluates AI-predicted category accuracy and appropriateness
- **Keyword Review**: Checks if AI-predicted keywords match/describe the product (simplified review for max 3 keywords)
- **Color-coded Excel Reports**: Automatically generates color-coded Excel reports for easy review
  - Green: PASS (approved)
  - Yellow: NEEDS_REVIEW (needs spot-checking)
  - Red: NEEDS_MANUAL_CHECK (requires manual review)

## Installation

### 1. Install Dependencies

```bash
cd ../ai rating
pip install -r requirements.txt
```

Required dependencies:
- `dashscope`: QWEN API integration
- `pandas`: Data processing and Excel export
- `openpyxl`: Excel file generation with formatting
- `python-dotenv`: Environment variable management

### 2. Set Up API Key

Create or edit the `.env` file in the project root directory (`ai rating/`):

```bash
cd ../ai rating
echo "QWEN_API_KEY=your_api_key_here" > .env
```

Or use environment variables:
```bash
export QWEN_API_KEY=your_api_key_here
```

> Get API Key: Visit [Alibaba Cloud DashScope Console](https://dashscope.console.aliyun.com/)

## Usage

### 1. Prepare Input File

The input file should be a CSV format, placed in the `database/` folder, containing the following columns:
- `id`: Product ID
- `url`: Product source URL
- `title`: Product title (scraped from source website)
- `description`: Product description (scraped from source website)
- `product_main_image`: Main image URL
- `product_image_list`: Additional image URLs (JSON array or comma-separated string)
- `cate_info_ai`: AI-predicted category (JSON format)
- `keyword_ai`: AI-predicted keywords (JSON format)

Example file: `database/dema.csv`

### 2. Run Audit

```bash
# Navigate to scraper directory
cd scraper

# Basic usage (report will be saved to report/ folder)
python3 product_auditor.py database/dema.csv

# Specify output file (will be saved to report/ folder)
python3 product_auditor.py database/dema.csv -o custom_audit_results.xlsx

# Use different model
python3 product_auditor.py database/dema.csv --model qwen-turbo

# Specify API Key via command line
python3 product_auditor.py database/dema.csv --api-key your_api_key_here
```

### 3. View Results

After auditing, an Excel file will be generated in the `report/` folder with the following columns:
- `id`: Product ID
- `url`: Product source URL
- `title`: Product title
- `url_判定结果`: URL audit status (PASS/NEEDS_REVIEW/NEEDS_MANUAL_CHECK)
- `url_判定原因`: URL audit reason
- `title_判定结果`: Title audit status
- `title_判定原因`: Title audit reason
- `description_判定结果`: Description audit status
- `description_判定原因`: Description audit reason
- `category_判定结果`: Category audit status
- `category_判定原因`: Category audit reason
- `keyword_判定结果`: Keyword audit status
- `keyword_判定原因`: Keyword audit reason

## Audit Criteria

### URL Review

The tool checks if the URL is a valid product page:
- ✅ **PASS**: URL is clearly a valid single product page
- ⚠️ **NEEDS_REVIEW** (Yellow): 
  - URL is a category page or multi-product listing page
  - Uncertain whether URL is a valid product page
- ❌ **NEEDS_MANUAL_CHECK** (Red): URL is a success case/portfolio page or clearly not a product page

**Detection Keywords:**
- Category/Multi-product pages: "category", "catalog", "products", "list", "collection", "browse", "shop", "all"
- Success case pages: "case", "portfolio", "success", "project", "client", "example", "story"
- Other non-product pages: "search", "home", "about", "contact"

### Title Review

Since titles are directly scraped from the source website (no AI processing), the review focuses on consistency:
- ✅ **PASS**: Scraped title matches the product name/identifier in the source URL
- ⚠️ **NEEDS_REVIEW** (Yellow): Slight inconsistency but mostly acceptable
- ❌ **NEEDS_MANUAL_CHECK** (Red): Significant inconsistency or mismatch with URL

### Description Review

Since descriptions are directly scraped from the source website (no AI processing), the review focuses on consistency:
- ✅ **PASS**: Scraped description matches/relates to the product name in the URL and is consistent with the title
- ⚠️ **NEEDS_REVIEW** (Yellow): Slight inconsistency but mostly acceptable
- ❌ **NEEDS_MANUAL_CHECK** (Red): Significant inconsistency or mismatch

### Category Review

Evaluates AI-predicted category:
- ✅ **PASS**: Category is accurate and appropriate, matches the product type
- ⚠️ **NEEDS_REVIEW** (Yellow): Category has minor issues (slightly too broad/narrow)
- ❌ **NEEDS_MANUAL_CHECK** (Red): Wrong category or significant issues

### Keyword Review

Since keywords are limited to a maximum of 3, the review is simplified:
- ✅ **PASS**: Keywords match/describe the product
- ⚠️ **NEEDS_REVIEW** (Yellow): Some keywords are slightly irrelevant but mostly acceptable
- ❌ **NEEDS_MANUAL_CHECK** (Red): Keywords are completely irrelevant or don't match the product

## Status Definitions

- **PASS** (通过): Content is acceptable and can be used directly (highlighted in **green**)
- **NEEDS_REVIEW** (需要抽查): Content has minor issues, is uncertain, or needs spot-checking (highlighted in **yellow**)
- **NEEDS_MANUAL_CHECK** (需要人工复核): Content has significant issues and requires manual review (highlighted in **red**)

## Output Format

The Excel report includes:
- All original data columns
- Audit status for each aspect (URL, Title, Description, Category, Keyword)
- Detailed reasons for each audit decision
- Color-coded cells for quick visual review:
  - 🟢 Green = PASS
  - 🟡 Yellow = NEEDS_REVIEW
  - 🔴 Red = NEEDS_MANUAL_CHECK

## File Structure

```
ai rating/
├── .env                    # API Key configuration (in root directory)
├── .gitignore              # Git ignore file (in root directory)
├── requirements.txt        # Python dependencies (in root directory)
└── scraper/
    ├── product_auditor.py  # Main auditor program
    ├── README.md           # This documentation
    ├── report/             # Audit report output folder
    │   └── *_audit_result.xlsx
    └── database/
        └── dema.csv        # Input data file
```

## Example Workflow

```bash
# 1. Navigate to scraper directory
cd scraper

# 2. Run audit (report will be automatically saved to report/ folder)
python3 product_auditor.py database/dema.csv

# 3. Generate combined summary report from all audit files
python3 generate_combined_summary.py

# 4. View results
# Open the generated report files:
# - report/*_audit_result.xlsx (detailed audit results for each file)
# - report/combined_summary_report_*.xlsx (combined summary report)
```

## Combined Summary Report

After generating audit results, you can create a combined summary report from all audit files:

```bash
python3 generate_combined_summary.py
```

The combined summary report includes five sheets:

1. **Summary Statistics**: 
   - Overall pass rates and status distribution for each aspect (URL, Title, Description, Category, Keyword)
   - Aggregated statistics across all audit files
   - Color-coded pass rates (Green ≥80%, Yellow ≥60%, Red <60%)
   - Total counts and percentages for each status

2. **File Statistics**: 
   - Statistics for each source file
   - Pass rates by aspect for each file
   - Easy comparison across different data sources

3. **Issue Analysis**: 
   - Common issues and their frequency across all files
   - Grouped by aspect and status
   - Top 10 most common issues for each category

4. **Problem Items**: 
   - Detailed list of all products that need attention (NEEDS_REVIEW or NEEDS_MANUAL_CHECK)
   - Includes Source File, ID, URL, Title, and all audit results with color coding
   - Easy to filter and review

5. **All Data**: 
   - Complete combined dataset from all audit files
   - Includes Source File column to identify origin
   - All audit results with color coding

The combined summary report is automatically saved to the `report/` folder with timestamp (e.g., `combined_summary_report_20241204_184600.xlsx`).

## Notes

1. Requires a valid Qwen/DashScope API Key
2. Audit process calls DashScope API and incurs costs
3. Default model is `qwen-plus`, can also use `qwen-turbo` (faster, cheaper) or `qwen-max` (more accurate)
4. Be aware of API rate limits when processing large batches
5. If JSON parsing errors occur, the first 500 characters of the response will be displayed for debugging
6. API Key configuration file (`.env`) is in the project root directory (`ai rating/`), not in the `scraper/` directory
7. Image review is currently skipped

## Troubleshooting

### Issue 1: API Call Failed
- Check if API Key is correct (in `.env` file in project root)
- Verify account balance is sufficient
- Check network connection

### Issue 2: JSON Parsing Failed
- View the response content shown in error message
- Try using `qwen-max` model (more accurate)

### Issue 3: File Path Error
- Ensure input file path is correct (relative to `scraper/` directory)
- Use relative or absolute paths

### Issue 4: Module Not Found
- Ensure dependencies are installed in project root: `cd ../ai rating && pip install -r requirements.txt`

## Model Options

- `qwen-turbo`: Fast response, lower cost (suitable for quick audits)
- `qwen-plus`: Balanced performance and cost (recommended)
- `qwen-max`: Highest performance, higher cost (suitable for high-precision requirements)

---

## Online Product Auditor (product_auditor_online.py)

### Overview

The Online Product Auditor is designed for auditing products from online platforms **without source URLs**. It evaluates products based solely on title and description, focusing on information completeness, consistency, and non-spam content detection.

### Key Differences from product_auditor.py

- **No URL validation**: Products don't have source URLs
- **Product validity check**: Identifies non-product content (success stories, case studies, portfolio pages)
- **Information completeness**: Checks if title and description are clear and complete
- **Consistency check**: Verifies title and description match
- **Non-spam detection**: Identifies spam, gibberish, or meaningless content
- **Output location**: Results saved to `report_online/` folder

### Usage

```bash
# Navigate to scraper directory
cd scraper

# Basic usage (report will be saved to report_online/ folder)
python3 product_auditor_online.py online/old_url_scrap_data_output.csv

# Specify output file
python3 product_auditor_online.py online/old_url_scrap_data_output.csv -o custom_results.xlsx

# Use different model
python3 product_auditor_online.py online/old_url_scrap_data_output.csv --model qwen-turbo
```

### Input File Format

The input CSV file should contain the following columns:
- `offer_id`: Product offer ID
- `title`: Product title
- `description`: Product description
- `category_id`: Category ID
- `category_name`: Category name
- `keywords`: Keywords (JSON array format)

Example file: `online/old_url_scrap_data_output.csv`

### Output Format

After auditing, an Excel file will be generated in the `report_online/` folder with the following columns:
- `offer_id`: Product offer ID
- `title`: Product title
- `description`: Product description (truncated to 200 chars)
- `category_id`: Category ID
- `category_name`: Category name
- `product_validity_判定结果`: Product validity status (PASS/NEEDS_REVIEW/NEEDS_MANUAL_CHECK)
- `product_validity_判定原因`: Product validity reason
- `information_completeness_判定结果`: Information completeness status
- `information_completeness_判定原因`: Information completeness reason
- `consistency_判定结果`: Consistency status
- `consistency_判定原因`: Consistency reason
- `non_spam_content_判定结果`: Non-spam content status
- `non_spam_content_判定原因`: Non-spam content reason
- `category_判定结果`: Category review status
- `category_判定原因`: Category review reason
- `keyword_判定结果`: Keyword review status
- `keyword_判定原因`: Keyword review reason

### Audit Criteria

#### Product Validity
- ✅ **PASS**: Content describes a valid product
- ⚠️ **NEEDS_REVIEW** (Yellow): Uncertain if it's a valid product
- ❌ **NEEDS_MANUAL_CHECK** (Red): 
  - Contains non-product content (success stories, case studies, portfolio pages)
  - Company information or "about us" content
  - General service descriptions without specific product details

#### Information Completeness
- ✅ **PASS**: Title and description are clear and complete
- ⚠️ **NEEDS_REVIEW** (Yellow): Title or description is slightly vague or incomplete
- ❌ **NEEDS_MANUAL_CHECK** (Red): 
  - Title is missing or too vague
  - Description is missing or too short (< 20 words)

#### Consistency
- ✅ **PASS**: Title and description are consistent
- ⚠️ **NEEDS_REVIEW** (Yellow): Slight inconsistency but mostly acceptable
- ❌ **NEEDS_MANUAL_CHECK** (Red): Significant mismatch between title and description

#### Non-Spam Content
- ✅ **PASS**: Content is meaningful and relevant
- ⚠️ **NEEDS_REVIEW** (Yellow): Content is slightly unclear but acceptable
- ❌ **NEEDS_MANUAL_CHECK** (Red): Content is spam, gibberish, or meaningless

#### Category Review
- ✅ **PASS**: Category is accurate and appropriate
- ⚠️ **NEEDS_REVIEW** (Yellow): Category has minor issues (slightly too broad/narrow)
- ❌ **NEEDS_MANUAL_CHECK** (Red): 
  - Category is wrong or significantly inappropriate
  - Category is empty or N/A

#### Keyword Review
- ✅ **PASS**: Keywords match/describe the product
- ⚠️ **NEEDS_REVIEW** (Yellow): Some keywords are slightly irrelevant but mostly acceptable
- ❌ **NEEDS_MANUAL_CHECK** (Red): Keywords are completely irrelevant or don't match the product

### File Structure

```
scraper/
├── product_auditor.py          # Main auditor (with URL)
├── product_auditor_online.py   # Online auditor (without URL)
├── online/                     # Input folder for online products
│   └── old_url_scrap_data_output.csv
└── report_online/              # Output folder for online audit results
    └── *_audit_result.xlsx
```
