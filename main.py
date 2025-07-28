from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from twilio.rest import Client
import os
from dotenv import load_dotenv
from typing import Optional
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp Twilio API",
    description="Send WhatsApp messages using Twilio API",
    version="1.0.0"
)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'  # Sandbox number

# Validate Twilio credentials on startup
if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    logger.error("Twilio credentials not found in environment variables")
    raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Pydantic models for request/response
class WhatsAppMessage(BaseModel):
    to: str = Field(..., description="Recipient WhatsApp number (format: whatsapp:+1234567890)")
    message: str = Field(..., min_length=1, max_length=1600, description="Message content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "to": "whatsapp:+911XXXXXXXX",
                "message": "Hello! This is a test message from FastAPI."
            }
        }

class MessageResponse(BaseModel):
    success: bool
    message_sid: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    twilio_configured: bool
    sandbox_number: str

# API Endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "WhatsApp Twilio API is running",
        "docs": "/docs",
        "status": "/status"
    }

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Check API and Twilio configuration status"""
    twilio_configured = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)
    
    return StatusResponse(
        status="online",
        twilio_configured=twilio_configured,
        sandbox_number=TWILIO_WHATSAPP_NUMBER
    )

@app.post("/send-message", response_model=MessageResponse)
async def send_whatsapp_message(message_data: WhatsAppMessage):
    """Send a WhatsApp message via Twilio"""
    try:
        # Validate phone number format
        if not message_data.to.startswith("whatsapp:+"):
            raise HTTPException(
                status_code=400,
                detail="Phone number must be in format 'whatsapp:+1234567890'"
            )
        
        # Send message via Twilio
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_data.message,
            to=message_data.to
        )
        
        logger.info(f"Message sent successfully. SID: {message.sid}")
        
        return MessageResponse(
            success=True,
            message_sid=message.sid,
            status=message.status
        )
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        
        # Handle Twilio-specific errors
        if hasattr(e, 'code'):
            error_msg = f"Twilio Error {e.code}: {e.msg}"
        else:
            error_msg = str(e)
            
        return MessageResponse(
            success=False,
            error=error_msg
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-07-28"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
