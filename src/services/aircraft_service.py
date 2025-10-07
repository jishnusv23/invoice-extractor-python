import instructor
from openai import OpenAI
import PyPDF2

from src.config.config import Config
from src.models.aircraft_models import AircraftUtilization


#Initailize  OpenRouter 
base_client=OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=Config.OPENROUTER_API_KEY
)
client=instructor.from_openai(base_client)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from PDF file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text from all pages
    """
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"📄 PDF has {len(reader.pages)} page(s)")
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                text += page_text + "\n"
                print(f"   Page {page_num}: {len(page_text)} characters extracted")
        
        return text.strip()
    
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise


def extract_aircraft_from_pdf(file_path: str, prompt: str) -> AircraftUtilization:
   
    try:
  
        print("\n🔄 Reading PDF...")
        pdf_text = extract_text_from_pdf(file_path)
        
        if not pdf_text:
            raise ValueError("No text could be extracted from the PDF")
        
        print(f"✅ Extracted {len(pdf_text)} characters from PDF")
        
      
        print("🤖 Sending data to AI for extraction...")
        
        aircraft_data = client.chat.completions.create(
            model=Config.TEXT_MODEL,
            response_model=AircraftUtilization,  
            max_retries=Config.MAX_RETRIES,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that extracts structured aircraft utilization data from maintenance reports. Extract all information accurately according to the schema provided."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n--- PDF CONTENT ---\n{pdf_text}"
                }
            ],
            temperature=Config.TEMPERATURE,
        )
        
        print("✅ Data extracted and validated")
        return aircraft_data
    
    except Exception as e:
        print(f"❌ Error in extraction: {str(e)}")
        raise

