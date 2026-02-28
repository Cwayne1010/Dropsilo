# Appraisal Workflow - n8n Architecture

## Overview

This document provides the technical n8n implementation guide for the appraisal order workflow.

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPRAISAL ORDER WORKFLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   STEP 1     │
    │   Webhook    │──────┐
    │   Trigger    │      │
    └──────────────┘      │
                          ▼
                    ┌──────────────┐     ┌──────────────┐
                    │   Validate   │────▶│  Log Order   │
                    │   Request    │     │  (Sheets)    │
                    └──────────────┘     └──────────────┘
                          │                     │
                          ▼                     │
    ┌──────────────┐      │                     │
    │   STEP 2     │◀─────┴─────────────────────┘
    │  Query Panel │
    │   (Sheets)   │
    └──────────────┘
          │
          ▼
    ┌──────────────┐     ┌──────────────┐
    │   Filter &   │────▶│   Select     │
    │   Rank       │     │   Top 3-5    │
    │   (Code)     │     │              │
    └──────────────┘     └──────────────┘
                               │
                               ▼
    ┌──────────────┐     ┌──────────────┐
    │   STEP 3     │     │   Log RFP    │
    │  Send RFP    │────▶│   Sent       │
    │  Emails      │     │   (Sheets)   │
    └──────────────┘     └──────────────┘
          │
          ▼
    ┌──────────────┐
    │    Wait      │
    │   24-48 hrs  │
    └──────────────┘
          │
          ▼
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │   STEP 4     │────▶│    Rank      │────▶│   Send to    │
    │  Aggregate   │     │   Quotes     │     │   LOS/Client │
    │   Quotes     │     │   (Code)     │     │              │
    └──────────────┘     └──────────────┘     └──────────────┘
                                                    │
                    ┌───────────────────────────────┘
                    │   (Wait for client selection)
                    ▼
    ┌──────────────┐     ┌──────────────┐
    │   STEP 5     │────▶│   Decline    │
    │  Engagement  │     │   Emails     │
    │  Letter      │     │   (losers)   │
    └──────────────┘     └──────────────┘
          │
          ▼
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │   STEP 6     │────▶│   Set Up     │────▶│   Notify     │
    │  Update LOS  │     │   Reminders  │     │   Client     │
    │              │     │              │     │              │
    └──────────────┘     └──────────────┘     └──────────────┘
```

## n8n Node Configuration

### Workflow 1: Order Intake & Appraiser Selection

**Node 1: Webhook Trigger**
```json
{
  "node": "Webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "appraisal-order",
    "responseMode": "onReceived",
    "responseData": "allEntries"
  }
}
```

**Node 2: Validate Request (IF)**
```json
{
  "node": "IF",
  "parameters": {
    "conditions": {
      "boolean": [
        {
          "value1": "={{ $json.property_address }}",
          "operation": "isNotEmpty"
        },
        {
          "value1": "={{ $json.property_type }}",
          "operation": "isNotEmpty"
        },
        {
          "value1": "={{ $json.client_id }}",
          "operation": "isNotEmpty"
        }
      ]
    }
  }
}
```

**Node 3: Generate Order ID (Code)**
```javascript
// Generate unique order ID
const date = new Date();
const year = date.getFullYear();
const random = Math.floor(Math.random() * 100000).toString().padStart(5, '0');
const orderId = `ORD-${year}-${random}`;

return {
  ...items[0].json,
  order_id: orderId,
  created_at: date.toISOString(),
  status: 'pending'
};
```

**Node 4: Log Order (Google Sheets)**
```json
{
  "node": "Google Sheets",
  "parameters": {
    "operation": "append",
    "sheetId": "{{ ORDERS_SHEET_ID }}",
    "sheetName": "Orders",
    "columns": {
      "order_id": "={{ $json.order_id }}",
      "property_address": "={{ $json.property_address }}",
      "property_type": "={{ $json.property_type }}",
      "loan_amount": "={{ $json.loan_amount }}",
      "client_id": "={{ $json.client_id }}",
      "contact_email": "={{ $json.contact_email }}",
      "urgency": "={{ $json.urgency }}",
      "scope": "={{ $json.scope }}",
      "status": "pending",
      "created_at": "={{ $json.created_at }}"
    }
  }
}
```

**Node 5: Query Appraiser Panel (Google Sheets)**
```json
{
  "node": "Google Sheets",
  "parameters": {
    "operation": "read",
    "sheetId": "{{ PANEL_SHEET_ID }}",
    "sheetName": "Appraisers",
    "range": "A:Z"
  }
}
```

**Node 6: Filter & Rank Appraisers (Code)**
```javascript
const order = items[0].json;
const appraisers = items[1].json; // From panel query

// Filter by qualifications
const qualified = appraisers.filter(a => {
  const states = a.states.split(',').map(s => s.trim());
  const types = a.property_types.split(',').map(t => t.trim());

  return (
    a.active === 'TRUE' &&
    states.includes(order.property_state) &&
    types.includes(order.property_type) &&
    parseInt(a.current_workload) < parseInt(a.capacity) &&
    parseFloat(a.quality_score) >= 4.0
  );
});

// Rank by quality score and availability
const ranked = qualified.sort((a, b) => {
  const scoreA = parseFloat(a.quality_score);
  const scoreB = parseFloat(b.quality_score);
  return scoreB - scoreA;
});

// Return top 5
return ranked.slice(0, 5).map(a => ({ json: a }));
```

**Node 7: Send RFP Emails (Gmail - Loop)**
```json
{
  "node": "Gmail",
  "parameters": {
    "operation": "send",
    "to": "={{ $json.email }}",
    "subject": "Quote Request - {{ $node['Order Data'].json.property_type }} Appraisal - {{ $node['Order Data'].json.property_city }}",
    "message": "Dear {{ $json.name }},\n\nWe have an appraisal assignment available:\n\nOrder #: {{ $node['Order Data'].json.order_id }}\nProperty: {{ $node['Order Data'].json.property_address }}\nType: {{ $node['Order Data'].json.property_type }}\nScope: {{ $node['Order Data'].json.scope }}\nRequired Turnaround: {{ $node['Order Data'].json.urgency }}\n\nPlease submit your fee and turnaround commitment by replying to this email or using our quote form.\n\nDeadline for Quote: {{ $now.plus(48, 'hours').toFormat('MMMM d, yyyy h:mm a') }}\n\nBest regards,\nOrder Desk"
  }
}
```

---

### Workflow 2: Quote Collection & Engagement

**Node 1: Quote Submission Webhook**
```json
{
  "node": "Webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "appraisal-quote",
    "responseMode": "onReceived"
  }
}
```

**Node 2: Log Quote (Google Sheets)**
```json
{
  "node": "Google Sheets",
  "parameters": {
    "operation": "append",
    "sheetId": "{{ QUOTES_SHEET_ID }}",
    "sheetName": "Quotes",
    "columns": {
      "order_id": "={{ $json.order_id }}",
      "appraiser_id": "={{ $json.appraiser_id }}",
      "fee": "={{ $json.fee }}",
      "turnaround_days": "={{ $json.turnaround_days }}",
      "submitted_at": "={{ $now.toISO() }}"
    }
  }
}
```

**Node 3: Check Quote Threshold (Code)**
```javascript
// Check if we have enough quotes or deadline passed
const quotes = items; // All quotes for this order
const MINIMUM_QUOTES = 3;

if (quotes.length >= MINIMUM_QUOTES) {
  return { proceed: true, quotes: quotes };
}

// Otherwise, wait for more
return { proceed: false };
```

**Node 4: Rank Quotes (Code)**
```javascript
const quotes = items;

// Score each quote (lower is better)
const scored = quotes.map(q => {
  const feeScore = parseFloat(q.json.fee) / 1000; // Normalize
  const timeScore = parseInt(q.json.turnaround_days);
  const qualityBonus = parseFloat(q.json.appraiser_quality_score) * -0.5;

  return {
    ...q.json,
    total_score: feeScore + timeScore + qualityBonus
  };
});

// Sort by score
const ranked = scored.sort((a, b) => a.total_score - b.total_score);

return ranked.map((q, i) => ({
  json: { ...q, rank: i + 1, recommended: i === 0 }
}));
```

**Node 5: Send Quote Summary to Client (Gmail)**
```json
{
  "node": "Gmail",
  "parameters": {
    "operation": "send",
    "to": "={{ $node['Order Data'].json.contact_email }}",
    "subject": "Appraisal Quotes Ready - Order #{{ $node['Order Data'].json.order_id }}",
    "message": "Quotes received for {{ $node['Order Data'].json.property_address }}:\n\n{{ $json.quote_summary_table }}\n\nRecommended: {{ $json.recommended_appraiser }}\n\nPlease reply with your selection or click the link to approve the recommendation."
  }
}
```

**Node 6: Wait for Selection**
```json
{
  "node": "Wait",
  "parameters": {
    "resume": "webhook",
    "webhookSuffix": "selection"
  }
}
```

**Node 7: Send Engagement Letter (Gmail)**
```json
{
  "node": "Gmail",
  "parameters": {
    "operation": "send",
    "to": "={{ $json.selected_appraiser_email }}",
    "subject": "Engagement Confirmation - Order #{{ $json.order_id }}",
    "message": "Dear {{ $json.selected_appraiser_name }},\n\nYou have been selected for the following assignment:\n\nOrder #: {{ $json.order_id }}\nProperty: {{ $json.property_address }}\nScope: {{ $json.scope }}\nAgreed Fee: ${{ $json.agreed_fee }}\nDue Date: {{ $json.due_date }}\n\nProperty Contact: {{ $json.property_contact_name }} - {{ $json.property_contact_phone }}\n\nPlease confirm acceptance by replying to this email.\n\nBest regards,\nOrder Desk"
  }
}
```

**Node 8: Send Decline Notices (Gmail - Loop)**
```javascript
// For each non-selected appraiser
const selected = items[0].json.selected_appraiser_id;
const allQuotes = items[0].json.all_quotes;

const declined = allQuotes.filter(q => q.appraiser_id !== selected);

return declined.map(q => ({ json: q }));
```

**Node 9: Update LOS (HTTP Request)**
```json
{
  "node": "HTTP Request",
  "parameters": {
    "method": "POST",
    "url": "{{ LOS_API_ENDPOINT }}/orders/{{ $json.order_id }}/engage",
    "authentication": "headerAuth",
    "body": {
      "appraiser_id": "={{ $json.selected_appraiser_id }}",
      "appraiser_name": "={{ $json.selected_appraiser_name }}",
      "fee": "={{ $json.agreed_fee }}",
      "due_date": "={{ $json.due_date }}",
      "status": "engaged"
    }
  }
}
```

---

## Required Google Sheets

### 1. Orders Sheet
| Column | Type | Description |
|--------|------|-------------|
| order_id | String | Unique order identifier |
| property_address | String | Full property address |
| property_type | String | Office, Retail, etc. |
| loan_amount | Number | Loan amount |
| client_id | String | Client identifier |
| contact_email | String | LO email |
| urgency | String | Standard/Rush/Super Rush |
| scope | String | Full/Limited/Evaluation |
| status | String | pending/rfp_sent/quotes_received/engaged/in_progress/qc_pending/delivered |
| created_at | DateTime | Order creation timestamp |
| engaged_appraiser | String | Appraiser ID |
| engaged_fee | Number | Agreed fee |
| due_date | Date | Report due date |
| report_url | String | URL to delivered report (Drive, Dropbox, etc.) |
| delivered_at | DateTime | Report delivery timestamp |

### 2. Appraiser Panel Sheet
| Column | Type | Description |
|--------|------|-------------|
| appraiser_id | String | Unique appraiser identifier |
| name | String | Company/individual name |
| email | String | Contact email |
| phone | String | Contact phone |
| states | String | Comma-separated state codes |
| property_types | String | Comma-separated property types |
| certifications | String | MAI, SRA, etc. |
| current_workload | Number | Active assignments |
| capacity | Number | Max concurrent assignments |
| avg_fee | Number | Average fee charged |
| avg_turnaround | Number | Average days to complete |
| quality_score | Number | 1-5 rating |
| active | Boolean | Currently accepting work |

### 3. Quotes Sheet
| Column | Type | Description |
|--------|------|-------------|
| order_id | String | Order reference |
| appraiser_id | String | Appraiser reference |
| fee | Number | Quoted fee |
| turnaround_days | Number | Quoted turnaround |
| submitted_at | DateTime | Quote submission time |
| selected | Boolean | Was this quote selected |

---

## Environment Variables (n8n Credentials)

```
ORDERS_SHEET_ID=1abc...xyz
PANEL_SHEET_ID=1def...uvw
QUOTES_SHEET_ID=1ghi...rst
LOS_API_ENDPOINT=https://api.los-system.com/v1
LOS_API_KEY=sk_live_...
```

## Deployment Checklist

- [ ] Create Google Sheets (Orders, Panel, Quotes)
- [ ] Set up Gmail credentials in n8n
- [ ] Configure Google Sheets credentials in n8n
- [ ] Set up LOS API credentials (if applicable)
- [ ] Deploy Order Intake workflow
- [ ] Deploy Quote Collection workflow
- [ ] Configure webhooks in LOS
- [ ] Test end-to-end with sample order
- [ ] Set up error notifications (Slack/email)
