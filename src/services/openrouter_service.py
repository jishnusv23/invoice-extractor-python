import json
import base64
from openai import OpenAI
from tenacity import retry,stop_after_attempt,wait_exponential
from src.config.config import Config
from src.models.invoice_response import InvoiceResponse

client=OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=Config.OPENROUTER_API_KEY
)

def parse_json_response(content: str) -> dict:
  
    try:
        json_string = content.strip()
        
      
        if json_string.startswith("```"):
            json_string = json_string.replace("```json\n", "").replace("```json", "")
            json_string = json_string.replace("```\n", "").replace("```", "")
            json_string = json_string.strip()
        
        parsed = json.loads(json_string)
        return parsed
    
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {content}")
        raise ValueError(f"Failed to parse JSON response: {str(e)}")


@retry(
    stop=stop_after_attempt(Config.MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def extract_invoice_from_image(
    file_buffer: bytes,
    mime_type: str,
    prompt: str
) -> InvoiceResponse:
   
    try:
        
        base64_file = base64.b64encode(file_buffer).decode('utf-8')
        
        
        response = client.chat.completions.create(
            model=Config.IMAGE_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that extracts structured invoice data in JSON format. Return only valid JSON without markdown formatting."
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
        
     
        text = response.choices[0].message.content
        
     
        parsed_data = parse_json_response(text)
        
      
        invoice = InvoiceResponse(**parsed_data)
        
        return invoice
    
    except Exception as e:
        print(f"OpenRouter API error: {str(e)}")
        raise