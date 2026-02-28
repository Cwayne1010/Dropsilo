# Contact Form Submission

## Goal
Process incoming contact form submissions from dropsilo.ai. Send a notification email to the team and a confirmation email to the submitter.

## Implementation
- **Platform:** n8n (eliwayne.app.n8n.cloud)
- **Workflow:** "Dropsilo Contact Form"
- **Webhook URL:** `https://eliwayne.app.n8n.cloud/webhook/dropsilo-contact`
- **Workflow JSON:** `c. execution/n8n/dropsilo_contact_form.json`
- **Frontend:** `Dropsilo/Dropsilo.ai/dropsilo-site/main.js` (sends POST via fetch)

## Inputs
- `name` (string, required): Full name of the submitter
- `email` (string, required): Submitter's email address
- `company` (string, optional): Company name
- `interest` (string, optional): Area of interest — one of: audit, automation, integration, ai, general
- `message` (string, required): Description of their operational challenge

## Process

1. **Validate inputs** (Code node)
   - Check that `name`, `email`, and `message` are provided and non-empty
   - If any required field is missing, return error with the missing field names
   - Validate email format (must contain @)
   - Uses explicit string `_valid: 'yes'/'no'` (not boolean — see n8n IF node caveat)

2. **Send notification email** to hello@dropsilo.ai
   - Subject: "New Lead: {name} — {interest label}"
   - Body includes all submitted fields and timestamp
   - From: "Dropsilo Contact Form" via Gmail SMTP

3. **Send confirmation email** to submitter
   - Subject: "Thanks for reaching out — Dropsilo"
   - From: "Dropsilo" via Gmail SMTP
   - Body (HTML email — see template below)

## Confirmation Email Template

Use the submitter's first name (parsed from `name` — everything before the first space). If no space, use the full name.

```
Subject: Thanks for reaching out — Dropsilo

Hi {first_name},

Thanks for reaching out to Dropsilo. We received your message and we're looking forward to learning more about your business.

I'll personally follow up within 24 hours to schedule your free 30-minute consultation.

In the meantime, here are a few things worth thinking about before we talk — they'll help us make the most of our time together:

YOUR CURRENT BOTTLENECKS
— What process eats up the most time for you or your team each week?
— Where do things break down or fall through the cracks most often?
— Are there tasks your team does manually that feel like they should be automated?

YOUR TECH STACK
— What tools does your team rely on day to day? (CRM, spreadsheets, email, project management, accounting, etc.)
— Are there tools that don't talk to each other the way you wish they would?
— Do you have any legacy systems or processes you've been meaning to replace?

YOUR GOALS
— If you could wave a wand and fix one operational problem tomorrow, what would it be?
— Are you looking to save time, reduce errors, cut costs — or all three?
— Is there a specific workflow or department you'd like to focus on first?

You don't need to have answers to all of these — they're just conversation starters. We'll figure out the rest together on the call.

Talk soon,

Eli Wayne
Dropsilo
hello@dropsilo.com
```

4. **Return success**
   - Return JSON: `{"status": "ok", "message": "Submission received"}`

## Tools
- n8n Email Send node (Gmail SMTP credential)
- n8n Webhook node (POST, response mode)
- n8n Code node (validation)

## Outputs
- Notification email to hello@dropsilo.ai
- Confirmation email to submitter
- JSON success/error response to the form

## Edge Cases

### Missing required fields
- Return 400: `{"status": "error", "message": "Missing required fields: [field_names]"}`
- Do not send emails

### Invalid email format
- Return 400: `{"status": "error", "message": "Missing required fields: email (invalid format)"}`
- Do not proceed

### Email send fails
- n8n execution will show error in execution log
- Form may show "Something went wrong" to user

## Learning Notes
- n8n IF node v2 is unreliable with boolean values — use explicit string comparison (`'yes'`/`'no'`) instead
- webhook-test URL only works in "Test workflow" listening mode; production URL requires workflow to be activated (toggled on)
- SMTP credential host must be `smtp.gmail.com` (not `smpt`)
