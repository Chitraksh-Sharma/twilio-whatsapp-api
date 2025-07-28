from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio credentials (get from Twilio Console)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'  # Sandbox number

# Your WhatsApp number (must be added to sandbox)
YOUR_WHATSAPP_NUMBER = 'whatsapp:+179XXXXXXX'  # Replace with your number

def send_test_message():
    try:
        
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send message
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body='Hello Man! How are you?',
            to=YOUR_WHATSAPP_NUMBER
        )
        
        print(f"Message sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        
        return message.sid
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

if __name__ == "__main__":
    print("Sending test WhatsApp message via Twilio...")
    send_test_message()
