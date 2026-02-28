# Onboard Client Directive

## Goal
Send a professional onboarding email to a new client that introduces our company, provides background information, and invites them to a kickoff call.

## Inputs
- `client_email` (string, required): Email address of the new client
- `client_name` (string, optional): Client's name (if known, for personalization)
- `company_name` (string, optional): Client's company name

## Process

1. **Validate inputs**
   - Check that `client_email` is provided and valid format
   - Extract name from email if `client_name` not provided (e.g., "john.smith@example.com" → "John Smith")

2. **Prepare email content**
   - Use professional, welcoming tone
   - Include company introduction and background
   - Highlight what the client can expect
   - Include calendar link for kickoff call
   - Add contact information

3. **Send onboarding email**
   - Use `execution/send_email.py` script
   - Pass parameters: `--to "{client_email}" --subject "Welcome to [Company]" --template onboarding`
   - Include calendar link in email body

4. **Log activity**
   - Record onboarding in `.tmp/onboarding_log.json`
   - Include: timestamp, client email, status (sent/failed)

## Tools
- `execution/send_email.py` - Email sending script
- Optional: `update_sheet` - Log to Google Sheet if tracking sheet exists

## Outputs
- Confirmation message: "Onboarding email sent to {client_email}"
- Email sent with:
  - Company introduction
  - Background on services
  - Next steps
  - Calendar link for kickoff call
  - Contact information

## Email Template Structure

**Subject**: Welcome to [Company Name] - Let's Get Started!

**Body**:
- Warm welcome message
- Brief company introduction (who we are, what we do)
- What the client can expect from us
- Invitation to kickoff call with calendar link
- Contact information for questions
- Professional signature

## Edge Cases

### Invalid email format
- Return error: "Invalid email format: {client_email}"
- Do not proceed with sending

### Email sending fails
- Retry once after 5 seconds
- If still fails, log error with details
- Return error message to user

### Missing calendar link in environment
- Log warning
- Send email without calendar link
- Notify user that calendar link needs to be configured

### SMTP configuration missing
- Return error: "Email configuration missing. Please set up SMTP in .env"
- Guide user to add: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

## Configuration Required

In `.env` file:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@company.com
SMTP_PASSWORD=your-app-password
COMPANY_NAME=Your Company Name
CALENDAR_LINK=https://calendly.com/your-link
```

## Learning Notes
(Updated as system learns)

- Initial creation: 2026-01-15
