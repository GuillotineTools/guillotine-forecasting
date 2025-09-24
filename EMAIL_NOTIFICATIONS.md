# Email Notification Setup

The Metaculus Forecasting Bot now includes email notifications to keep you informed about its activity. You'll receive emails when the bot starts and completes its runs.

## Setting Up Email Notifications

To enable email notifications, you need to configure the following environment variables in your GitHub repository secrets:

### Required Environment Variables

1. **NOTIFICATION_SENDER_EMAIL** - The email address that will send the notifications
2. **NOTIFICATION_SENDER_PASSWORD** - The password for the sender email account
3. **NOTIFICATION_RECIPIENT_EMAIL** - The email address that will receive the notifications (optional, defaults to sender email)

### Optional Environment Variables

4. **NOTIFICATION_SMTP_SERVER** - SMTP server address (defaults to 'smtp.gmail.com')
5. **NOTIFICATION_SMTP_PORT** - SMTP server port (defaults to '587')

## Gmail Setup Instructions

If you're using Gmail as your email provider:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Navigate to Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this app password as your `NOTIFICATION_SENDER_PASSWORD`

## GitHub Repository Secrets Setup

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret" and add each of the required environment variables:
   - `NOTIFICATION_SENDER_EMAIL`
   - `NOTIFICATION_SENDER_PASSWORD`
   - `NOTIFICATION_RECIPIENT_EMAIL` (optional)
   - `NOTIFICATION_SMTP_SERVER` (optional)
   - `NOTIFICATION_SMTP_PORT` (optional)

## Testing Email Notifications

To test the email notifications:

1. Run the bot manually using the "workflow_dispatch" trigger
2. Check your email for startup and completion notifications
3. Verify that the email content includes the correct information about the run

## Notification Content

The notifications will include:

- **Startup notifications**: Inform you when the bot begins running
- **Completion notifications**: Summarize the run results including:
  - Number of questions processed
  - Number of questions with errors
  - Output file name
  - Run mode and timestamp

## Troubleshooting

If you're not receiving email notifications:

1. **Check environment variables**: Ensure all required secrets are set correctly
2. **Verify SMTP settings**: Confirm the SMTP server and port are correct for your email provider
3. **Check spam folder**: Notifications might be filtered as spam
4. **Review logs**: Check the GitHub Actions logs for any error messages related to email sending

## Security Notes

- Never commit email passwords or other sensitive information to the repository
- Use app-specific passwords when available (recommended for Gmail)
- The bot only uses these credentials to send notifications and does not store them