import base64
import instructor
from openai import OpenAI

from src.config.config import Config
from src.models.invoice_response import InvoiceResponse



base_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=Config.OPENROUTER_API_KEY,
)


client = instructor.from_openai(base_client)


def extract_invoice_from_image(
    file_buffer: bytes,
    mime_type: str,
    prompt: str
) -> InvoiceResponse:
   
    try:
       
        base64_file = base64.b64encode(file_buffer).decode('utf-8')
        
       
        invoice = client.chat.completions.create(
            model=Config.IMAGE_MODEL,
            response_model=InvoiceResponse,  
            max_retries=Config.MAX_RETRIES,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that extracts structured invoice data. Extract all invoice information accurately."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_file}"
                            }
                        }
                    ]
                }
            ],
            temperature=Config.TEMPERATURE,
        )
        
        #
        return invoice
    
    except Exception as e:
        print(f"OpenRouter API error: {str(e)}")
        raise



def extract_invoice_with_validation(
    file_buffer: bytes,
    mime_type: str,
    prompt: str
) -> InvoiceResponse:
    """
    Extract with custom validation error handling
    """
    try:
        base64_file = base64.b64encode(file_buffer).decode('utf-8')
        
        invoice = client.chat.completions.create(
            model=Config.IMAGE_MODEL,
            response_model=InvoiceResponse,
            max_retries=3,
            validation_context={
                "strict": True,  
            },
            messages=[
                {
                    "role": "system",
                    "content": "Extract invoice data. If a field is missing, use null. All monetary values must be numbers."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{base64_file}"}
                        }
                    ]
                }
            ],
            temperature=0,
        )
        
        return invoice
        
    except instructor.exceptions.InstructorRetryException as e:
        print(f"Failed after retries: {e}")
        print(f"Last validation error: {e.last_completion}")
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise