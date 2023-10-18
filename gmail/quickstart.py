import base64
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    print("Running gmail quickstart...")
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)

        return service

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')



def extract_order_details(content):
    # List to store all order details
    order_details_list = []

    # Regex patterns
    order_number_pattern = r"orderId%3D(\d+-\d+-\d+)"
    ship_to_name_pattern = r"Ship to:\<\/span\> \<br \/\> \<b\> ([^\<]+) \<br \/\>"
    ship_to_location_pattern = r"\<b\> [^\<]+ \<br \/\> ([^\<]+) \<\/b\>"
    order_total_pattern = r"Order Total: \<\/td\>=20\r?\n\s+\<\/tr\>=20\r?\n\s+\<\/tbody\>\s+\<\/table\> \<\/td\>=20\r?\n\s+\<td\>=20\r?\n\s+\<table id=3D\"costBreakdownRight\"\>=[\s\S]+?\<b\>([^\<]+)\<\/b\>"
    item_name_pattern = r"<td class=3D\"name\"> <font style=3D\"color:#000000;\"> ([^\<]+) </font>"
    item_qty_pattern = r"Qty : (\d+)"

    # Extracting order details
    order_numbers = re.findall(order_number_pattern, content)
    ship_to_names = re.findall(ship_to_name_pattern, content)
    ship_to_locations = re.findall(ship_to_location_pattern, content)
    order_totals = re.findall(order_total_pattern, content)
    item_names = re.findall(item_name_pattern, content)
    item_qtys = re.findall(item_qty_pattern, content)

    # Loop through the orders
    for i in range(len(order_numbers)):
        order = {}
        order['Order Number'] = order_numbers[i] if i < len(order_numbers) else None
        order['Ship To'] = {'Name': ship_to_names[i] if i < len(ship_to_names) else None,
                            'Location': ship_to_locations[i] if i < len(ship_to_locations) else None}
        order['Order Total'] = order_totals[i] if i < len(order_totals) else None
        order_items = []
        for j in range(len(item_names)):
            item = {}
            item['name'] = item_names[j].replace("=\r\n", "").replace("&quot;", "\"").replace("&amp;", "&")
            item['qty'] = item_qtys[j]
            order_items.append(item)
        order['Items'] = order_items
        order_details_list.append(order)

    print(order_details_list)
    return order_details_list



def get_emails_from_amazon(service):
    query = "from:auto-confirm@amazon.com"
    results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
    messages = results.get('messages', [])

    email_contents = []

    # For each email, retrieve its content
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
        msg_str = base64.urlsafe_b64decode(msg['raw']).decode('utf-8')
        email_contents.append(msg_str)
    
    return email_contents

def check():
    service = get_service()
    emails = get_emails_from_amazon(service)
    for email in emails:
        extract_order_details(email)

# Use your existing 'check()' function to authenticate and create the 'service'
# Then call the 'get_emails_from_amazon(service)' function



if __name__ == '__main__':
    check()