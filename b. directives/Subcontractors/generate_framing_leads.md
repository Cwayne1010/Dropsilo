# Generate Framing/Carpentry Subcontractor Leads

## Goal
Generate a list of 500 framing and carpentry subcontractor leads starting with Minneapolis/St. Paul, expanding to other high-construction-demand cities. Output to Google Sheets with company info, contact details, and ratings.

## Inputs
- `target_cities` (list): Cities to scrape, ordered by priority
  - Default: Minneapolis, St. Paul, Denver, Phoenix, Dallas, Austin, Nashville, Charlotte
- `lead_count` (int): Target number of leads (default: 500)
- `output_sheet_id` (string): Google Sheet ID for output

## Target Cities (by construction demand)

### Primary (Start Here)
1. Minneapolis, MN
2. St. Paul, MN

### Secondary (Expand if needed)
3. Denver, CO - Major construction boom
4. Phoenix, AZ - Fastest growing metro
5. Dallas, TX - High commercial/residential activity
6. Austin, TX - Tech-driven construction surge
7. Nashville, TN - Rapid growth market
8. Charlotte, NC - Southeast construction hub

## Process

### Step 1: Scrape via Apify (Recommended - Reliable)

**Prerequisites:** Add `APIFY_API_TOKEN` to `.env` (free tier: $5/month)

```bash
python execution/scrape_via_apify.py \
  --source google_maps \
  --cities "Minneapolis,St. Paul,Denver,Phoenix,Dallas,Austin" \
  --category "framing contractors" \
  --max-results 100 \
  --output .tmp/apify_leads.json
```

**Cost:** ~$2.50 per 1000 results from Google Maps

**Data collected:**
- Company name
- Full address (city, state)
- Phone number
- Website URL
- Rating (stars)
- Reviews count

### Step 1 (Alternative): Basic Scrapers (Limited Data)

If Apify isn't available, use the basic scrapers. Note: These only get company names due to JS rendering.

```bash
# Thumbtack (gets names, limited contact info)
python execution/scrape_thumbtack.py \
  --cities "Minneapolis,St. Paul,Denver,Phoenix,Dallas,Austin" \
  --category "framing-contractors" \
  --max-results 300 \
  --output .tmp/thumbtack_leads.json

# Angi (often blocked by anti-bot)
python execution/scrape_angi.py \
  --cities "Minneapolis,St. Paul,Denver,Phoenix,Dallas,Austin" \
  --category "framing" \
  --max-results 300 \
  --output .tmp/angi_leads.json
```

### Step 2: Deduplicate & Merge
```bash
python execution/merge_leads.py \
  --inputs ".tmp/thumbtack_leads.json,.tmp/angi_leads.json" \
  --output .tmp/merged_leads.json \
  --limit 500
```

**Deduplication logic:**
- Match on normalized company name + city
- Keep record with most data (prefer one with website)
- Merge ratings from both sources

### Step 4: Enrich Emails (Free Tier)
```bash
python execution/enrich_emails_free.py \
  --input .tmp/merged_leads.json \
  --output .tmp/enriched_leads.json
```

**Methods (in order):**
1. Hunter.io free tier (25 searches/month)
2. Snov.io free tier (50 credits/month)
3. Website scraping for contact pages
4. Email pattern guessing (first@domain.com, info@domain.com)

### Step 5: Export to Google Sheets
```bash
python execution/export_leads_to_sheets.py \
  --input .tmp/enriched_leads.json \
  --sheet-name "Framing Leads - $(date +%Y-%m-%d)"
```

**Sheet columns:**
| Column | Source |
|--------|--------|
| Company Name | Thumbtack/Angi |
| City | Thumbtack/Angi |
| State | Thumbtack/Angi |
| Phone | Thumbtack/Angi |
| Email | Enrichment |
| Website | Thumbtack/Angi |
| Rating | Average of sources |
| Reviews | Sum of sources |
| Source | "Thumbtack", "Angi", "Both" |
| Verified | Angi verified badge |

## Tools
- `execution/scrape_thumbtack.py` - Thumbtack scraper
- `execution/scrape_angi.py` - Angi scraper
- `execution/merge_leads.py` - Deduplication and merge
- `execution/enrich_emails_free.py` - Free email enrichment
- `execution/export_leads_to_sheets.py` - Google Sheets export

## Outputs
- Google Sheet with 500 leads
- Columns: Company, City, State, Phone, Email, Website, Rating, Reviews, Source, Verified
- Sheet shared with user's Google account

## Edge Cases

### Thumbtack blocks scraping
- Use Apify's Thumbtack scraper as fallback
- Implement random delays (2-5 seconds between requests)
- Rotate user agents

### Angi CAPTCHA
- Reduce request rate
- Use residential proxy if available
- Fall back to Thumbtack-only if blocked

### Not enough leads in primary cities
- Expand to secondary cities automatically
- Log which cities were used

### Email enrichment rate limits
- Hunter.io: 25/month free - use first for highest-rated leads
- Snov.io: 50/month free - use for remaining
- Website scraping: unlimited but slower
- Don't fail pipeline if enrichment incomplete

### Duplicate companies across cities
- Keep both entries (could be different branches)
- Add "Branch" indicator if same company name in multiple cities

## Rate Limits & Timing
- Thumbtack: 2-3 second delay between pages
- Angi: 3-5 second delay (stricter)
- Hunter.io: 25 requests/month (free)
- Snov.io: 50 credits/month (free)
- Google Sheets: 100 requests/100 seconds

## Learning Notes
(Updated as system learns)

- Initial version: 2025-01-16
- 2025-01-16: Thumbtack and Angi use heavy JS rendering. Basic HTTP scraping only gets company names, not contact info. Use Apify's Google Maps scraper for reliable data with phone/website. Cost is ~$2.50/1000 results which is worth it for the data quality.
- 2025-01-16: Google Sheets export requires OAuth setup. User needs credentials.json from Google Cloud Console.
