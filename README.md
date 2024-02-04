# Stripe and Google Sheets Integration

This Flask application integrates Stripe payments with Google Sheets, allowing you to automatically update a Google Sheet with customer data whenever a payment is completed using a Stripe Checkout Session.

## Setup

### Google Sheets

1. Create a Google Sheets document and note the document key.
2. Open the document and create a worksheet (e.g., "Sheet1").

### Stripe

1. Sign up for a [Stripe](https://stripe.com/) account if you don't have one.
2. Obtain your Stripe API key from the [Dashboard](https://dashboard.stripe.com/apikeys).
3. Replace the placeholder `sk_test_...` with your actual Stripe API key in the Flask app.

### Flask App

1. Install required dependencies using the following command:
   ```bash
   pip install -r requirements.txt
    ```
    Save your Google Sheets credentials as credentials.json in the root directory.

### Usage

1. Run the Flask app:

    ```bash
    python app.py
    ```

2. Expose the app to the internet using tools like ngrok:

    ```bash
    ngrok http 5000
    ```
   
    Set up the webhook endpoint in your Stripe Dashboard.
        Use the ngrok HTTPS URL with the /webhook path (e.g., https://your-ngrok-url/webhook).
        Subscribe to the checkout.session.completed event.

### Folder Structure
- `app.py`: Main Flask application file.
- `credentials.json`: Google Sheets API credentials file.
- `requirements.txt`: List of Python dependencies.
- `README.md`: Project documentation.
