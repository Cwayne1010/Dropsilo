# Appraisal Order Workflow

## Goal
Manage the end-to-end commercial real estate appraisal ordering process—from initial request through appraiser selection, quote collection, engagement, and delivery to the Loan Origination System (LOS).

## Inputs
- `property_address` (string): Full property address
- `property_type` (string): Office, Retail, Industrial, Multifamily, Mixed-Use, Special Purpose
- `loan_amount` (number): Requested loan amount
- `loan_purpose` (string): Purchase, Refinance, Construction, etc.
- `client_id` (string): Bank/Credit Union identifier
- `contact_name` (string): Loan officer or requester name
- `contact_email` (string): Email for communications
- `urgency` (string): Standard (10-14 days), Rush (5-7 days), Super Rush (3-5 days)
- `scope` (string): Full Appraisal, Limited Appraisal, Evaluation
- `special_instructions` (string, optional): Additional requirements

## Process

### Step 1: Receive Request & Validate
**Trigger:** Webhook from LOS or manual form submission

1. Validate all required fields are present
2. Verify `client_id` is active in client roster
3. Check property address geocodes correctly
4. Determine appraisal requirements based on:
   - Loan amount thresholds (regulatory requirements)
   - Property type complexity
   - Client-specific requirements
5. Generate unique `order_id`
6. Log order in tracking sheet

**n8n Nodes:**
- Webhook Trigger (receives POST from LOS)
- IF node (validation checks)
- Google Sheets (log new order)
- Error handling → notify ops team

---

### Step 2: Find Optimal Appraiser from Panel
**Goal:** Match order to qualified appraisers based on geography, expertise, and availability

1. Query appraiser panel sheet for:
   - Licensed/certified in property state
   - Property type expertise matches
   - Geographic coverage includes property location
   - Current workload < capacity threshold
   - Performance rating ≥ minimum threshold
   - Not on client exclusion list
2. Rank by:
   - Geographic proximity (primary)
   - Historical turnaround accuracy
   - Quality score
   - Fee competitiveness
3. Select top 3-5 candidates for RFP

**Data Sources:**
- `Appraiser Panel` Google Sheet (columns: name, email, states, property_types, capacity, avg_fee, avg_turnaround, quality_score)
- `Client Preferences` sheet (exclusions, preferred appraisers)

**n8n Nodes:**
- Google Sheets (read panel)
- Code node (filtering/ranking logic)
- Set node (prepare candidate list)

---

### Step 3: Automatic RFP Email to Appraisers
**Goal:** Send quote requests to selected appraisers with order details

1. Generate RFP email with:
   - Property details (address, type, size if known)
   - Scope of work
   - Required turnaround
   - Fee quote request
   - Response deadline (typically 24-48 hours)
   - Link to quote submission form
2. Send to all selected appraisers simultaneously
3. Log outreach in order history
4. Set reminder for quote deadline

**Email Template:**
```
Subject: Quote Request - [Property Type] Appraisal - [City, State]

Dear [Appraiser Name],

We have an appraisal assignment available:

Property: [Address]
Type: [Property Type]
Scope: [Full Appraisal / Evaluation]
Required Turnaround: [X business days]
Deadline for Quote: [Date/Time]

Please submit your fee and turnaround commitment via:
[Quote Form Link]

If you're unavailable, please decline so we can reassign promptly.

Best regards,
[AMC Name] Order Desk
```

**n8n Nodes:**
- Gmail node (send emails in loop)
- Google Sheets (log sent RFPs)
- Wait node (quote collection window)

---

### Step 4: Collect Quotes & Present to LOS
**Goal:** Aggregate appraiser quotes and present options to client/LOS

1. Monitor quote submissions (webhook or form responses)
2. For each quote received:
   - Validate appraiser is on original RFP list
   - Check fee is within acceptable range
   - Verify turnaround meets requirements
   - Log in quotes sheet
3. After deadline (or 3+ quotes received):
   - Compile quote summary
   - Rank by best value (fee + turnaround + quality score)
   - Generate recommendation
4. Push to LOS/client portal:
   - Quote comparison table
   - Recommended appraiser with rationale
   - Accept/reject options

**Quote Summary Format:**
| Appraiser | Fee | Turnaround | Quality Score | Recommendation |
|-----------|-----|------------|---------------|----------------|
| Smith & Co | $3,500 | 12 days | 4.8 | ★ Recommended |
| Jones Appraisal | $3,200 | 14 days | 4.2 | |
| ABC Valuation | $4,000 | 10 days | 4.5 | |

**n8n Nodes:**
- Webhook (receive quote submissions)
- Google Sheets (aggregate quotes)
- Code node (ranking logic)
- HTTP Request (push to LOS API) OR Email (send summary)

---

### Step 5: Engagement Letters
**Goal:** Formalize engagement with winning appraiser; notify unsuccessful bidders

**5a. Winner Engagement:**
1. Generate engagement letter with:
   - Full order details
   - Agreed fee and turnaround
   - Property access contact info
   - Scope of work / USPAP requirements
   - Delivery format requirements (PDF, XML, etc.)
   - Payment terms
2. Send via email (or DocuSign if signature required)
3. Request confirmation of acceptance
4. Update order status to "Engaged"
5. Trigger inspection scheduling workflow

**5b. Non-Selected Notifications:**
1. Send courtesy decline email to non-selected appraisers
2. Thank them for quoting
3. Keep relationship warm for future orders

**Engagement Email Template:**
```
Subject: Engagement Confirmation - Order #[Order ID] - [Property Address]

Dear [Appraiser Name],

You have been selected for the following assignment:

Order #: [Order ID]
Property: [Full Address]
Scope: [Scope]
Agreed Fee: $[Fee]
Due Date: [Date]

Property Contact: [Name] - [Phone] - [Email]

Please confirm acceptance by replying to this email.

Engagement terms and USPAP requirements attached.

Best regards,
[AMC Name]
```

**n8n Nodes:**
- Gmail (engagement letter to winner)
- Gmail (decline notices in loop)
- Google Sheets (update order status)
- Optional: DocuSign integration

---

### Step 6: Delivery Receipt
**Trigger:** Webhook POST to `/appraisal-delivery`
**Goal:** Receive completed report, notify client, flag for QC review

1. Appraiser submits delivery via webhook with:
   - `order_id`, `appraiser_id`, `report_url`, `report_type` (optional), `notes` (optional)
2. Validate required fields
3. Look up order details from Orders sheet
4. Update Orders sheet:
   - `status` → `qc_pending`
   - `delivered_at` → timestamp
   - `report_url` → submitted URL
5. Email client/loan officer:
   - Report link, property details, appraiser info
   - Note that QC review is in progress
6. Respond with success confirmation

**Note:** Client is notified immediately but order stays in `qc_pending` status until QC review is completed manually.

**n8n Workflow:** `execution/n8n/appraisal_delivery_receipt.json`

**n8n Nodes:**
- Webhook (receive delivery POST)
- Code (extract body, validate, merge data)
- IF (string-based `_valid === 'yes'` check)
- Google Sheets (read order, update status + report_url)
- Gmail (client notification)
- Respond to Webhook (success/error)

**Required:** Add `report_url` column to the Orders sheet before deploying.

---

## Tools & Integrations

### Google Sheets (Primary Data Store)
- **Orders**: All order data, status, history
- **Appraiser Panel**: Appraiser roster, qualifications, performance
- **Quotes**: Quote submissions per order
- **Clients**: Client roster, preferences, exclusions

### Gmail
- RFP emails to appraisers
- Engagement letters
- Client notifications
- Status updates

### LOS Integration (HTTP Request)
- Receive orders via webhook
- Push status updates
- Deliver final reports

### ClickUp (Optional)
- Internal task tracking
- QC review queue
- Escalation management

## Outputs
- Order logged and tracked in Google Sheets
- RFP emails sent to qualified appraisers
- Quote summary delivered to client/LOS
- Engagement letter sent to selected appraiser
- LOS updated with engagement details
- Milestone tracking activated

## Edge Cases

### No Appraisers Available
- Expand geographic search radius
- Contact backup panel list
- Notify ops team for manual assignment
- Alert client of potential delay

### No Quotes Received by Deadline
- Send reminder to RFP recipients
- Extend deadline by 24 hours
- Expand to additional appraisers
- Escalate to ops team

### All Quotes Exceed Budget
- Present options to client with context
- Offer to negotiate with preferred appraiser
- Suggest scope reduction if appropriate
- Document client decision

### Appraiser Declines After Engagement
- Immediately notify client
- Re-engage next-ranked appraiser
- Expedite new engagement
- Update LOS with revised timeline

### Client Cancels Order
- Notify engaged appraiser immediately
- Determine cancellation fee (if work started)
- Update all tracking systems
- Close order with cancellation reason

### LOS API Unavailable
- Queue updates for retry
- Send email notification as backup
- Log for manual reconciliation
- Retry with exponential backoff

## Data Schema

### Order Record
```json
{
  "order_id": "ORD-2024-001234",
  "status": "engaged",
  "property_address": "123 Main St, Chicago, IL 60601",
  "property_type": "Office",
  "loan_amount": 5000000,
  "scope": "Full Appraisal",
  "urgency": "Standard",
  "client_id": "BANK-001",
  "contact_email": "loanofficer@bank.com",
  "created_at": "2024-01-15T10:30:00Z",
  "engaged_appraiser": "APP-042",
  "engaged_fee": 3500,
  "due_date": "2024-01-29",
  "report_url": "https://drive.google.com/file/d/...",
  "delivered_at": "2024-01-28T09:00:00Z",
  "milestones": {
    "rfp_sent": "2024-01-15T11:00:00Z",
    "quotes_received": "2024-01-16T14:00:00Z",
    "engaged": "2024-01-16T16:30:00Z",
    "inspection_complete": null,
    "draft_received": null,
    "qc_complete": null,
    "delivered": null
  }
}
```

### Appraiser Panel Record
```json
{
  "appraiser_id": "APP-042",
  "name": "Smith Valuation Services",
  "email": "john@smithvaluation.com",
  "phone": "312-555-1234",
  "states": ["IL", "IN", "WI"],
  "property_types": ["Office", "Retail", "Industrial"],
  "certifications": ["MAI", "SRA"],
  "current_workload": 3,
  "capacity": 8,
  "avg_fee_office": 3500,
  "avg_turnaround_days": 12,
  "quality_score": 4.8,
  "active": true
}
```

## Metrics to Track
- Order volume by client
- Average turnaround time
- Quote-to-engagement conversion rate
- Appraiser utilization
- Fee variance from estimates
- On-time delivery rate
- Revision request rate

## Execution Scripts

All deterministic logic lives in `execution/appraisal/`. Scripts are called by the orchestration layer (Claude) based on this directive.

### Setup
```bash
# First time: create Google Sheets
python execution/appraisal/setup_sheets.py

# Add the sheet ID to .env:
# APPRAISAL_ORDERS_SHEET_ID=xxx
# APPRAISAL_PANEL_SHEET_ID=xxx
# APPRAISAL_QUOTES_SHEET_ID=xxx
```

### Step 1: Receive Order
```bash
# Validate and log new order
python execution/appraisal/receive_order.py --json '{"property_address": "...", "property_type": "Office", ...}'

# Test with sample data
python execution/appraisal/receive_order.py --test
```

### Step 2: Find Appraisers
```bash
# Get ranked appraiser candidates
python execution/appraisal/find_appraisers.py --order-id ORD-2024-12345

# Or query directly
python execution/appraisal/find_appraisers.py --property-state IL --property-type Office
```

### Step 3: Send RFP
```bash
# Send RFP to auto-selected appraisers
python execution/appraisal/send_rfp.py --order-id ORD-2024-12345

# Preview without sending
python execution/appraisal/send_rfp.py --order-id ORD-2024-12345 --dry-run
```

### Step 4: Collect Quotes
```bash
# Record incoming quote
python execution/appraisal/collect_quotes.py --record --order-id ORD-2024-12345 --appraiser-id APP-001 --fee 3500 --turnaround 12

# Get ranked summary
python execution/appraisal/collect_quotes.py --summary --order-id ORD-2024-12345

# Send summary to client
python execution/appraisal/collect_quotes.py --send-summary --order-id ORD-2024-12345
```

### Step 5: Engagement
```bash
# Engage specific quote
python execution/appraisal/send_engagement.py --order-id ORD-2024-12345 --quote-id Q-xxx

# Auto-engage recommended
python execution/appraisal/send_engagement.py --order-id ORD-2024-12345 --auto
```

### Webhook Endpoints
Modal webhooks are configured in `execution/webhooks.json`:
- `appraisal-order` - Receive new order
- `appraisal-find-appraisers` - Query appraiser panel
- `appraisal-send-rfp` - Send RFP emails
- `appraisal-record-quote` - Log incoming quote
- `appraisal-quote-summary` - Get/send summary
- `appraisal-engage` - Finalize engagement

## Learning Notes
(Updated as system learns)

- [Date]: Initial workflow created
- 2025-01: Execution scripts created for Modal + Python implementation

