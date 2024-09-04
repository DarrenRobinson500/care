import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

account_sid = os.environ.get("account_sid")
auth_token = os.environ.get("auth_token")
my_twilio_number = os.environ.get("my_twilio_number")
target_number = os.environ.get("target_number")

client = Client(account_sid, auth_token)
# content = "Hello"
# to_mobile = "+61493461541"
# client.messages.create(body=content, from_=my_twilio_number, to=to_mobile)

# print(account_sid)