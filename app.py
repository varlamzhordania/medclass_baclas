from flask import Flask, request
import stripe
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Set up Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)
client = gspread.authorize(creds)

# Set up Stripe
stripe.api_key = ""

# Google Sheets configuration
spreadsheet_key = ""
worksheet_name = "Sheet1"  # Change this to your sheet name


def update_google_sheets(customer_data):
    """
    Update Google Sheets with customer data.

    :param customer_data: Dictionary containing extracted customer data
    :return: True if successful, False otherwise
    """
    try:
        # Open the Google Sheet
        sheet = client.open_by_key(spreadsheet_key).worksheet(worksheet_name)

        # Extracted fields
        extracted_fields = [
            'cetipdemodeldesimularevreissusii',
            'numecandidat',
            'prenumecandidat',
            'amount_total',
            'currency',
            'customer',
            'email',
            'name',
            'phone',
            'tax_exempt',
            'city',
            'country',
            'line1',
            'line2',
            'postal_code',
            'state',
            'payment_status',
            'status'
        ]

        # Create a list to store values for the row
        row_values = []
        column_values = []

        # Append values to the row
        for field in extracted_fields:
            if isinstance(customer_data[field], dict):
                row_values.append(customer_data.get(field, {}).get('value', ''))
                column_values.append(customer_data.get(field, {}).get('label', ''))
            else:
                row_values.append(customer_data.get(field))
                column_values.append(field)

        # add headers
        sheet.update('A1', [column_values])

        # Append a new row with customer data
        sheet.insert_row(row_values, index=2)

        return True
    except Exception as e:
        print(f"Error updating Google Sheets: {str(e)}")
        return False


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Stripe webhook endpoint to handle events.

    :return: Empty response with status code
    """
    payload = request.get_data(as_text=True)

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        print(f"Error decoding Stripe event: {str(e)}")
        return '', 400

    if event['type'] == 'checkout.session.completed':
        customer_data = extract_customer_data(event)
        update_google_sheets(customer_data)

    return '', 200


def extract_customer_data(event):
    """
    Extract relevant customer data from Stripe event.

    :param event: Stripe event data
    :return: Dictionary containing extracted customer data
    """
    session = event['data']['object']
    custom_fields = session.get('custom_fields', [])
    customer_details = session.get('customer_details', {})
    customer_address = customer_details.get('address', {})
    extracted_data = {}

    for field in custom_fields:
        field_key = field['key']
        field_type = field['type']
        field_label = field['label']["custom"]

        if field_type == 'dropdown':
            # Handle dropdown type
            options = field.get('dropdown', {}).get('options', [])
            selected_value = field.get('dropdown', {}).get('value', '')
            for option in options:
                if option['value'] == selected_value:
                    extracted_data[field_key] = {"value": option['label'], "label": field_label}
                    break

        elif field_type == 'text':
            # Handle text type
            extracted_data[field_key] = {"value": field.get('text', {}).get('value', ''), "label": field_label}

        # Add more cases if you have other field types

    # Format amount_total as currency
    extracted_data["amount_total"] = "${:.2f}".format(session.get("amount_total", 0) / 100)
    extracted_data["currency"] = session.get("currency", '')
    extracted_data["customer"] = session.get("customer", '')
    extracted_data["email"] = customer_details.get("email", '')
    extracted_data["name"] = customer_details.get("name", '')
    extracted_data["phone"] = customer_details.get("phone", '')
    extracted_data["tax_exempt"] = customer_details.get("tax_exempt", '')
    extracted_data["city"] = customer_address.get("city", '')
    extracted_data["country"] = customer_address.get("country", '')
    extracted_data["line1"] = customer_address.get("line1", '')
    extracted_data["line2"] = customer_address.get("line2", '')
    extracted_data["postal_code"] = customer_address.get("postal_code", '')
    extracted_data["state"] = customer_address.get("state", '')
    extracted_data["payment_status"] = session.get("payment_status", '')
    extracted_data["status"] = session.get("status", '')

    return extracted_data


if __name__ == '__main__':
    app.run(port=5000)
